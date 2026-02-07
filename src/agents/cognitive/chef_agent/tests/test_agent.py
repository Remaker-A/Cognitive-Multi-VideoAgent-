"""
ChefAgent 主类测试

测试 ChefAgent 的初始化、事件订阅和事件处理功能
"""

import pytest
from datetime import datetime
from src.agents.cognitive.chef_agent.agent import ChefAgent
from src.agents.cognitive.chef_agent.models import Event, EventType, Money
from src.agents.cognitive.chef_agent.config import ChefAgentConfig


class TestChefAgentInitialization:
    """测试 ChefAgent 初始化"""

    def test_initialization_with_default_config(self):
        """测试使用默认配置初始化"""
        agent = ChefAgent()

        assert agent.config is not None
        assert agent.budget_manager is not None
        assert agent.strategy_adjuster is not None
        assert agent.failure_evaluator is not None
        assert agent.human_gate is not None
        assert agent.project_validator is not None
        assert agent.event_manager is not None

    def test_initialization_with_custom_config(self):
        """测试使用自定义配置初始化"""
        config = ChefAgentConfig(base_budget_per_second=5.0, max_retry_count=5)
        agent = ChefAgent(config=config)

        assert agent.config.base_budget_per_second == 5.0
        assert agent.config.max_retry_count == 5

    def test_subscribed_events(self):
        """测试订阅的事件类型"""
        agent = ChefAgent()
        subscribed = agent.get_subscribed_events()

        # 验证订阅了所有必需的事件
        assert EventType.PROJECT_CREATED in subscribed
        assert EventType.CONSISTENCY_FAILED in subscribed
        assert EventType.COST_OVERRUN_WARNING in subscribed
        assert EventType.USER_APPROVED in subscribed
        assert EventType.USER_REVISION_REQUESTED in subscribed
        assert EventType.USER_REJECTED in subscribed
        assert EventType.PROJECT_FINALIZED in subscribed
        assert EventType.IMAGE_GENERATED in subscribed
        assert EventType.VIDEO_GENERATED in subscribed

    def test_is_subscribed(self):
        """测试事件订阅检查"""
        agent = ChefAgent()

        assert agent.is_subscribed(EventType.PROJECT_CREATED) is True
        assert agent.is_subscribed(EventType.CONSISTENCY_FAILED) is True
        assert agent.is_subscribed(EventType.ERROR_OCCURRED) is False


class TestChefAgentEventHandling:
    """测试 ChefAgent 事件处理"""

    @pytest.mark.asyncio
    async def test_handle_project_created_event(self):
        """测试处理 PROJECT_CREATED 事件"""
        agent = ChefAgent()

        event = Event(
            event_id="evt_test_001",
            project_id="proj_test_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )

        await agent.handle_event(event)

        # 验证预算已分配
        project_data = agent._project_cache.get("proj_test_001")
        assert project_data is not None
        assert project_data["budget"].total.amount == 90.0  # 30 * 3.0 * 1.0
        assert project_data["quality_tier"] == "balanced"
        assert project_data["status"] == "ACTIVE"

        # 验证发布了 BUDGET_ALLOCATED 事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.BUDGET_ALLOCATED

    @pytest.mark.asyncio
    async def test_handle_cost_event(self):
        """测试处理成本事件"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_002",
            project_id="proj_test_002",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 发送成本事件
        cost_event = Event(
            event_id="evt_test_003",
            project_id="proj_test_002",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=10.0, currency="USD"),
        )
        await agent.handle_event(cost_event)

        # 验证预算已更新
        project_data = agent._project_cache.get("proj_test_002")
        assert project_data["budget"].spent.amount == 10.0

        # 验证没有发布预警事件（使用率 < 80%）
        events = agent.event_manager.get_published_events()
        assert len(events) == 0

    @pytest.mark.asyncio
    async def test_handle_cost_event_with_warning(self):
        """测试处理成本事件并触发预警"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_004",
            project_id="proj_test_003",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 发送大额成本事件（超过 80%）
        cost_event = Event(
            event_id="evt_test_005",
            project_id="proj_test_003",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=75.0, currency="USD"),  # 75/90 = 83%
        )
        await agent.handle_event(cost_event)

        # 验证发布了预警事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.COST_OVERRUN_WARNING

    @pytest.mark.asyncio
    async def test_handle_consistency_failed_event(self):
        """测试处理 CONSISTENCY_FAILED 事件"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_006",
            project_id="proj_test_004",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        # 发送失败事件（重试次数达到 3 次）
        failed_event = Event(
            event_id="evt_test_007",
            project_id="proj_test_004",
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

        # 验证触发了人工介入
        project_data = agent._project_cache.get("proj_test_004")
        assert project_data["status"] == "PAUSED"
        assert project_data["human_gate_request"] is not None

        # 验证发布了 HUMAN_GATE_TRIGGERED 事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.HUMAN_GATE_TRIGGERED

    @pytest.mark.asyncio
    async def test_handle_unsubscribed_event(self):
        """测试处理未订阅的事件"""
        agent = ChefAgent()

        event = Event(
            event_id="evt_test_008",
            project_id="proj_test_005",
            event_type=EventType.ERROR_OCCURRED,
            actor="TestAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
        )

        # 应该忽略未订阅的事件
        await agent.handle_event(event)

        # 验证没有发布任何事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


class TestChefAgentErrorRecovery:
    """测试 ChefAgent 三层错误恢复策略"""

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_on_first_try(self):
        """测试第一次尝试就成功"""
        agent = ChefAgent()

        call_count = 0

        async def successful_func():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await agent.retry_with_backoff(successful_func)

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_with_backoff_success_after_retries(self):
        """测试重试后成功"""
        agent = ChefAgent()

        call_count = 0

        async def eventually_successful_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary error")
            return "success"

        result = await agent.retry_with_backoff(
            eventually_successful_func,
            max_retries=3,
            initial_delay=0.01,  # 使用短延迟加快测试
        )

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_with_backoff_all_retries_failed(self):
        """测试所有重试都失败"""
        agent = ChefAgent()

        call_count = 0

        async def always_failing_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")

        with pytest.raises(ValueError, match="Persistent error"):
            await agent.retry_with_backoff(
                always_failing_func, max_retries=3, initial_delay=0.01
            )

        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_with_backoff_exponential_delay(self):
        """测试指数退避延迟"""
        import time

        agent = ChefAgent()

        call_times = []

        async def failing_func():
            call_times.append(time.time())
            raise Exception("Test error")

        try:
            await agent.retry_with_backoff(
                failing_func, max_retries=3, initial_delay=0.1
            )
        except Exception:
            pass

        # 验证调用了 3 次
        assert len(call_times) == 3

        # 验证延迟递增（允许一些误差）
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert delay1 >= 0.09  # 第一次延迟约 0.1 秒

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert delay2 >= 0.18  # 第二次延迟约 0.2 秒

    @pytest.mark.asyncio
    async def test_handle_with_fallback_budget_error(self):
        """测试预算错误的降级处理"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_fallback_001",
            project_id="proj_test_fallback_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "high"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        # 模拟预算不足错误
        project_data = agent._project_cache.get("proj_test_fallback_001")
        budget = project_data["budget"]

        # 设置预算使用率超过 80%
        budget.spent.amount = budget.total.amount * 0.85
        project_data["budget"] = budget
        agent._project_cache["proj_test_fallback_001"] = project_data

        error = Exception("Budget exceeded")
        context = {"project_id": "proj_test_fallback_001", "budget": budget}

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        result = await agent.handle_with_fallback(error, context)

        # 验证降级成功
        assert result["action"] == "QUALITY_REDUCED"
        assert result["new_tier"] == "balanced"  # high -> balanced

        # 验证项目质量档位已更新
        updated_project = agent._project_cache.get("proj_test_fallback_001")
        assert updated_project["quality_tier"] == "balanced"

        # 验证发布了策略更新事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.STRATEGY_UPDATE

    @pytest.mark.asyncio
    async def test_handle_with_fallback_non_budget_error(self):
        """测试非预算错误无法降级"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_fallback_002",
            project_id="proj_test_fallback_002",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        error = Exception("Network error")
        context = {"project_id": "proj_test_fallback_002"}

        # 非预算错误应该抛出异常
        with pytest.raises(Exception, match="Network error"):
            await agent.handle_with_fallback(error, context)

    @pytest.mark.asyncio
    async def test_escalate_to_human(self):
        """测试升级到人工介入"""
        agent = ChefAgent()

        # 先创建项目
        create_event = Event(
            event_id="evt_test_escalate_001",
            project_id="proj_test_escalate_001",
            event_type=EventType.PROJECT_CREATED,
            actor="TestOrchestrator",
            payload={"duration": 30.0, "quality_tier": "balanced"},
            timestamp=datetime.now().isoformat(),
        )
        await agent.handle_event(create_event)

        # 清空已发布的事件
        agent.event_manager.clear_published_events()

        error = Exception("Critical error")
        context = {
            "project_id": "proj_test_escalate_001",
            "event_id": "evt_test_escalate_001",
            "retry_count": 3,
        }

        await agent.escalate_to_human(error, context)

        # 验证项目已暂停
        project_data = agent._project_cache.get("proj_test_escalate_001")
        assert project_data["status"] == "PAUSED"
        assert project_data["human_gate_request"] is not None

        # 验证发布了 HUMAN_GATE_TRIGGERED 事件
        events = agent.event_manager.get_published_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.HUMAN_GATE_TRIGGERED

        # 验证请求包含错误信息
        request = project_data["human_gate_request"]
        assert "Error recovery failed" in request.reason
        assert request.context["error_type"] == "Exception"
        assert request.context["error_message"] == "Critical error"
        assert (
            request.context["escalation_level"]
            == "Level 3 - Human Intervention Required"
        )

    @pytest.mark.asyncio
    async def test_event_handling_with_error_recovery(self):
        """测试事件处理中的错误恢复流程"""
        agent = ChefAgent()

        # 创建一个会失败的事件处理场景
        # 这里我们模拟一个不存在的项目的成本事件
        cost_event = Event(
            event_id="evt_test_recovery_001",
            project_id="proj_nonexistent",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=10.0, currency="USD"),
        )

        # 事件处理应该通过错误恢复机制处理
        # 由于项目不存在，会触发错误恢复
        await agent.handle_event(cost_event)

        # 验证错误被记录（通过日志）
        # 实际测试中应该检查日志输出或错误事件
