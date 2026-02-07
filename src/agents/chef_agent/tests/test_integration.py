"""
ChefAgent 集成测试

测试完整的工作流程:
1. 预算管理流程
2. 失败评估和人工介入流程
3. 项目完成验证流程
"""

import pytest
from datetime import datetime
from src.agents.chef_agent.agent import ChefAgent
from src.agents.chef_agent.models import Event, EventType, Money


class TestBudgetManagementWorkflow:
    """测试完整的预算管理流程"""

    @pytest.mark.asyncio
    async def test_complete_budget_workflow(self):
        """
        测试完整的预算管理流程:
        1. 创建项目并分配预算
        2. 处理多个成本事件
        3. 触发预算预警
        4. 触发预算超支
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_budget_001",
            project_id="proj_budget_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 验证预算已分配
        project_data = agent._project_cache.get("proj_budget_001")
        assert project_data is not None
        assert project_data["budget"].total.amount == 90.0  # 30 * 3.0
        assert project_data["status"] == "ACTIVE"

        # 验证发布了 BUDGET_ALLOCATED 事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.BUDGET_ALLOCATED

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 处理多个成本事件（总计 60 美元，使用率 66%）
        for i in range(6):
            cost_event = Event(
                event_id=f"evt_budget_cost_{i}",
                project_id="proj_budget_001",
                event_type=EventType.IMAGE_GENERATED,
                actor="ImageAgent",
                payload={},
                timestamp=datetime.now().isoformat(),
                cost=Money(amount=10.0, currency="USD"),
            )
            await agent.handle_event(cost_event)

        # 验证预算已更新
        project_data = agent._project_cache.get("proj_budget_001")
        assert project_data["budget"].spent.amount == 60.0

        # 验证没有发布预警事件（使用率 < 80%）
        events = agent.event_manager.get_published_events()
        assert len(events) == 0

        # 3. 再处理 2 个成本事件（总计 80 美元，使用率 88%）
        for i in range(2):
            cost_event = Event(
                event_id=f"evt_budget_warning_{i}",
                project_id="proj_budget_001",
                event_type=EventType.IMAGE_GENERATED,
                actor="ImageAgent",
                payload={},
                timestamp=datetime.now().isoformat(),
                cost=Money(amount=10.0, currency="USD"),
            )
            await agent.handle_event(cost_event)

        # 验证触发了预警事件
        events = agent.event_manager.get_published_events()
        warning_events = [
            e for e in events if e.event_type == EventType.COST_OVERRUN_WARNING
        ]
        assert len(warning_events) > 0

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 4. 再处理 2 个成本事件（总计 100 美元，使用率 111%）
        for i in range(2):
            cost_event = Event(
                event_id=f"evt_budget_exceeded_{i}",
                project_id="proj_budget_001",
                event_type=EventType.IMAGE_GENERATED,
                actor="ImageAgent",
                payload={},
                timestamp=datetime.now().isoformat(),
                cost=Money(amount=10.0, currency="USD"),
            )
            await agent.handle_event(cost_event)

        # 验证触发了预算超支事件
        events = agent.event_manager.get_published_events()
        exceeded_events = [
            e for e in events if e.event_type == EventType.BUDGET_EXCEEDED
        ]
        assert len(exceeded_events) > 0

        # 验证最终预算状态
        project_data = agent._project_cache.get("proj_budget_001")
        assert project_data["budget"].spent.amount == 100.0
        assert project_data["budget"].total.amount == 90.0

    @pytest.mark.asyncio
    async def test_budget_with_strategy_adjustment(self):
        """
        测试预算管理与策略调整的集成:
        1. 创建高质量项目
        2. 消耗预算触发预警
        3. 自动降低质量档位
        """
        agent = ChefAgent()

        # 1. 创建高质量项目
        create_event = Event(
            event_id="evt_strategy_001",
            project_id="proj_strategy_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "high"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 验证预算已分配（high 质量档位：30 * 3.0 * 1.5 = 135）
        project_data = agent._project_cache.get("proj_strategy_001")
        assert project_data["budget"].total.amount == 135.0
        assert project_data["quality_tier"] == "high"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 消耗预算到 85%（触发预警和策略调整）
        cost_event = Event(
            event_id="evt_strategy_cost_001",
            project_id="proj_strategy_001",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=115.0, currency="USD"),  # 85% 使用率
        )

        await agent.handle_event(cost_event)

        # 验证触发了预警事件
        events = agent.event_manager.get_published_events()
        warning_events = [
            e for e in events if e.event_type == EventType.COST_OVERRUN_WARNING
        ]
        assert len(warning_events) > 0

        # 3. 模拟预算错误并触发策略降级
        project_data = agent._project_cache.get("proj_strategy_001")
        budget = project_data["budget"]

        error = Exception("Budget exceeded")
        context = {"project_id": "proj_strategy_001", "budget": budget}

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        result = await agent.handle_with_fallback(error, context)

        # 验证降级成功
        assert result["action"] == "QUALITY_REDUCED"
        assert result["new_tier"] == "balanced"  # high -> balanced

        # 验证项目质量档位已更新
        updated_project = agent._project_cache.get("proj_strategy_001")
        assert updated_project["quality_tier"] == "balanced"

        # 验证发布了策略更新事件
        events = agent.event_manager.get_published_events()
        strategy_events = [
            e for e in events if e.event_type == EventType.STRATEGY_UPDATE
        ]
        assert len(strategy_events) == 1


class TestFailureEvaluationWorkflow:
    """测试失败评估和人工介入流程"""

    @pytest.mark.asyncio
    async def test_failure_to_human_gate_workflow(self):
        """
        测试失败评估到人工介入的完整流程:
        1. 创建项目
        2. 触发失败事件（重试次数达到 3 次）
        3. 触发人工介入
        4. 处理用户批准
        5. 恢复项目
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_failure_001",
            project_id="proj_failure_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 验证项目已创建
        project_data = agent._project_cache.get("proj_failure_001")
        assert project_data is not None
        assert project_data["status"] == "ACTIVE"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 触发失败事件（重试次数达到 3 次）
        failed_event = Event(
            event_id="evt_failure_002",
            project_id="proj_failure_001",
            event_type=EventType.CONSISTENCY_FAILED,
            actor="ConsistencyAgent",
            payload={
                "task_id": "task_001",
                "error_type": "APIError",
                "error_message": "API timeout",
                "retry_count": 3,
                "cost_impact": 5.0,
                "severity": "medium",
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(failed_event)

        # 3. 验证触发了人工介入
        project_data = agent._project_cache.get("proj_failure_001")
        assert project_data["status"] == "PAUSED"
        assert project_data["human_gate_request"] is not None

        # 验证发布了 HUMAN_GATE_TRIGGERED 事件
        events = agent.event_manager.get_published_events()
        human_gate_events = [
            e for e in events if e.event_type == EventType.HUMAN_GATE_TRIGGERED
        ]
        assert len(human_gate_events) == 1

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 4. 处理用户批准
        approved_event = Event(
            event_id="evt_failure_003",
            project_id="proj_failure_001",
            event_type=EventType.USER_APPROVED,
            actor="AdminCLI",
            payload={
                "decided_by": "admin",
                "notes": "Approved after review",
                "decided_at": datetime.now().isoformat(),
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(approved_event)

        # 5. 验证项目已恢复
        project_data = agent._project_cache.get("proj_failure_001")
        assert project_data["status"] == "ACTIVE"
        assert project_data["human_gate_request"] is None

    @pytest.mark.asyncio
    async def test_failure_to_rejection_workflow(self):
        """
        测试失败评估到用户拒绝的流程:
        1. 创建项目
        2. 触发失败事件
        3. 触发人工介入
        4. 处理用户拒绝
        5. 标记项目为失败
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_reject_001",
            project_id="proj_reject_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 触发失败事件（成本影响超过 $20）
        failed_event = Event(
            event_id="evt_reject_002",
            project_id="proj_reject_001",
            event_type=EventType.CONSISTENCY_FAILED,
            actor="ConsistencyAgent",
            payload={
                "task_id": "task_002",
                "error_type": "QualityError",
                "error_message": "Quality check failed",
                "retry_count": 1,
                "cost_impact": 25.0,  # 超过 $20
                "severity": "high",
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(failed_event)

        # 验证触发了人工介入
        project_data = agent._project_cache.get("proj_reject_001")
        assert project_data["status"] == "PAUSED"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 3. 处理用户拒绝
        rejected_event = Event(
            event_id="evt_reject_003",
            project_id="proj_reject_001",
            event_type=EventType.USER_REJECTED,
            actor="AdminCLI",
            payload={
                "decided_by": "admin",
                "notes": "Quality issues cannot be resolved",
                "decided_at": datetime.now().isoformat(),
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(rejected_event)

        # 4. 验证项目已标记为失败
        project_data = agent._project_cache.get("proj_reject_001")
        assert project_data["status"] == "FAILED"
        assert project_data["failure_reason"] == "Quality issues cannot be resolved"
        assert project_data["human_gate_request"] is None

    @pytest.mark.asyncio
    async def test_failure_to_revision_workflow(self):
        """
        测试失败评估到修订请求的流程:
        1. 创建项目
        2. 触发失败事件
        3. 触发人工介入
        4. 处理用户修订请求
        5. 创建修订任务
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_revise_001",
            project_id="proj_revise_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 触发失败事件（严重程度为 critical）
        failed_event = Event(
            event_id="evt_revise_002",
            project_id="proj_revise_001",
            event_type=EventType.CONSISTENCY_FAILED,
            actor="ConsistencyAgent",
            payload={
                "task_id": "task_003",
                "error_type": "CriticalError",
                "error_message": "Critical system error",
                "retry_count": 1,
                "cost_impact": 10.0,
                "severity": "critical",
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(failed_event)

        # 验证触发了人工介入
        project_data = agent._project_cache.get("proj_revise_001")
        assert project_data["status"] == "PAUSED"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 3. 处理用户修订请求
        revision_event = Event(
            event_id="evt_revise_003",
            project_id="proj_revise_001",
            event_type=EventType.USER_REVISION_REQUESTED,
            actor="AdminCLI",
            payload={
                "decided_by": "admin",
                "notes": "Please adjust the quality parameters",
                "decided_at": datetime.now().isoformat(),
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(revision_event)

        # 4. 验证创建了修订任务
        project_data = agent._project_cache.get("proj_revise_001")
        assert project_data["status"] == "REVISION"
        assert project_data["revision_notes"] == "Please adjust the quality parameters"
        assert project_data["human_gate_request"] is None


class TestProjectCompletionWorkflow:
    """测试项目完成验证流程"""

    @pytest.mark.asyncio
    async def test_complete_project_delivery_workflow(self):
        """
        测试完整的项目交付流程:
        1. 创建项目
        2. 处理成本事件
        3. 完成项目
        4. 验证项目完成
        5. 生成总结报告
        6. 发布 PROJECT_DELIVERED 事件
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_complete_001",
            project_id="proj_complete_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 处理成本事件
        cost_event = Event(
            event_id="evt_complete_002",
            project_id="proj_complete_001",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=50.0, currency="USD"),
        )

        await agent.handle_event(cost_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 3. 完成项目
        finalized_event = Event(
            event_id="evt_complete_003",
            project_id="proj_complete_001",
            event_type=EventType.PROJECT_FINALIZED,
            actor="Orchestrator",
            payload={
                "shots": {
                    "shot_001": {"status": "FINAL_RENDERED"},
                    "shot_002": {"status": "FINAL_RENDERED"},
                },
                "artifacts": {
                    "artifact_001": {"cost": {"amount": 30.0, "currency": "USD"}},
                    "artifact_002": {"cost": {"amount": 20.0, "currency": "USD"}},
                },
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(finalized_event)

        # 4. 验证项目已完成
        project_data = agent._project_cache.get("proj_complete_001")
        assert project_data["status"] == "DELIVERED"
        assert project_data["summary"] is not None

        # 5. 验证总结报告
        summary = project_data["summary"]
        assert summary.project_id == "proj_complete_001"
        assert summary.total_cost.amount == 50.0  # 30 + 20
        assert summary.budget_total.amount == 90.0
        assert summary.budget_compliance.is_compliant is True
        assert summary.shots_count == 2

        # 6. 验证发布了 PROJECT_DELIVERED 事件
        events = agent.event_manager.get_published_events()
        delivered_events = [
            e for e in events if e.event_type == EventType.PROJECT_DELIVERED
        ]
        assert len(delivered_events) == 1

    @pytest.mark.asyncio
    async def test_project_with_budget_overrun(self):
        """
        测试预算超支的项目完成流程:
        1. 创建项目
        2. 处理大额成本事件（超出预算）
        3. 完成项目
        4. 验证预算超支被记录
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_overrun_001",
            project_id="proj_overrun_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 处理大额成本事件（超出预算）
        cost_event = Event(
            event_id="evt_overrun_002",
            project_id="proj_overrun_001",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=120.0, currency="USD"),  # 超出预算 90.0
        )

        await agent.handle_event(cost_event)

        # 验证触发了预算超支事件
        events = agent.event_manager.get_published_events()
        exceeded_events = [
            e for e in events if e.event_type == EventType.BUDGET_EXCEEDED
        ]
        assert len(exceeded_events) > 0

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 3. 完成项目
        finalized_event = Event(
            event_id="evt_overrun_003",
            project_id="proj_overrun_001",
            event_type=EventType.PROJECT_FINALIZED,
            actor="Orchestrator",
            payload={
                "shots": {"shot_001": {"status": "FINAL_RENDERED"}},
                "artifacts": {
                    "artifact_001": {"cost": {"amount": 120.0, "currency": "USD"}}
                },
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(finalized_event)

        # 4. 验证预算超支被记录
        project_data = agent._project_cache.get("proj_overrun_001")
        assert project_data["status"] == "DELIVERED"

        summary = project_data["summary"]
        assert summary.budget_compliance.is_compliant is False
        assert summary.budget_compliance.overrun_amount == 30.0  # 120 - 90
        assert summary.total_cost.amount == 120.0
        assert summary.budget_total.amount == 90.0


class TestEndToEndWorkflow:
    """测试端到端的完整工作流程"""

    @pytest.mark.asyncio
    async def test_complete_end_to_end_workflow(self):
        """
        测试完整的端到端工作流程:
        1. 创建项目并分配预算
        2. 处理多个成本事件
        3. 触发预算预警
        4. 触发失败事件和人工介入
        5. 用户批准后恢复
        6. 完成项目并生成报告
        """
        agent = ChefAgent()

        # 1. 创建项目
        create_event = Event(
            event_id="evt_e2e_001",
            project_id="proj_e2e_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 60.0, "quality_tier": "high"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(create_event)

        # 验证预算已分配（60 * 3.0 * 1.5 = 270）
        project_data = agent._project_cache.get("proj_e2e_001")
        assert project_data["budget"].total.amount == 270.0
        assert project_data["quality_tier"] == "high"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 2. 处理多个成本事件（总计 200 美元，使用率 74%）
        for i in range(10):
            cost_event = Event(
                event_id=f"evt_e2e_cost_{i}",
                project_id="proj_e2e_001",
                event_type=EventType.IMAGE_GENERATED,
                actor="ImageAgent",
                payload={},
                timestamp=datetime.now().isoformat(),
                cost=Money(amount=20.0, currency="USD"),
            )
            await agent.handle_event(cost_event)

        # 验证预算已更新
        project_data = agent._project_cache.get("proj_e2e_001")
        assert project_data["budget"].spent.amount == 200.0

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 3. 再处理 2 个成本事件（总计 240 美元，使用率 88%）
        for i in range(2):
            cost_event = Event(
                event_id=f"evt_e2e_warning_{i}",
                project_id="proj_e2e_001",
                event_type=EventType.IMAGE_GENERATED,
                actor="ImageAgent",
                payload={},
                timestamp=datetime.now().isoformat(),
                cost=Money(amount=20.0, currency="USD"),
            )
            await agent.handle_event(cost_event)

        # 验证触发了预警事件
        events = agent.event_manager.get_published_events()
        warning_events = [
            e for e in events if e.event_type == EventType.COST_OVERRUN_WARNING
        ]
        assert len(warning_events) > 0

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 4. 触发失败事件
        failed_event = Event(
            event_id="evt_e2e_failed",
            project_id="proj_e2e_001",
            event_type=EventType.CONSISTENCY_FAILED,
            actor="ConsistencyAgent",
            payload={
                "task_id": "task_e2e_001",
                "error_type": "APIError",
                "error_message": "API timeout",
                "retry_count": 3,
                "cost_impact": 10.0,
                "severity": "medium",
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(failed_event)

        # 验证触发了人工介入
        project_data = agent._project_cache.get("proj_e2e_001")
        assert project_data["status"] == "PAUSED"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 5. 用户批准后恢复
        approved_event = Event(
            event_id="evt_e2e_approved",
            project_id="proj_e2e_001",
            event_type=EventType.USER_APPROVED,
            actor="AdminCLI",
            payload={
                "decided_by": "admin",
                "notes": "Approved",
                "decided_at": datetime.now().isoformat(),
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(approved_event)

        # 验证项目已恢复
        project_data = agent._project_cache.get("proj_e2e_001")
        assert project_data["status"] == "ACTIVE"

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 6. 完成项目
        finalized_event = Event(
            event_id="evt_e2e_finalized",
            project_id="proj_e2e_001",
            event_type=EventType.PROJECT_FINALIZED,
            actor="Orchestrator",
            payload={
                "shots": {
                    "shot_001": {"status": "FINAL_RENDERED"},
                    "shot_002": {"status": "FINAL_RENDERED"},
                    "shot_003": {"status": "FINAL_RENDERED"},
                },
                "artifacts": {
                    "artifact_001": {"cost": {"amount": 100.0, "currency": "USD"}},
                    "artifact_002": {"cost": {"amount": 80.0, "currency": "USD"}},
                    "artifact_003": {"cost": {"amount": 60.0, "currency": "USD"}},
                },
            },
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(finalized_event)

        # 验证项目已完成
        project_data = agent._project_cache.get("proj_e2e_001")
        assert project_data["status"] == "DELIVERED"

        # 验证总结报告
        summary = project_data["summary"]
        assert summary.project_id == "proj_e2e_001"
        assert summary.total_cost.amount == 240.0  # 100 + 80 + 60
        assert summary.budget_total.amount == 270.0
        assert summary.budget_compliance.is_compliant is True
        assert summary.shots_count == 3
        assert summary.quality_tier == "high"

        # 验证发布了 PROJECT_DELIVERED 事件
        events = agent.event_manager.get_published_events()
        delivered_events = [
            e for e in events if e.event_type == EventType.PROJECT_DELIVERED
        ]
        assert len(delivered_events) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
