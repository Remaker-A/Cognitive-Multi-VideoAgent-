"""
ChefAgent EventManager 单元测试

测试事件发布功能和数据完整性
Validates: Requirements 1.5, 2.3, 2.4, 3.2, 4.6, 6.6, 8.8, 8.9
"""

import pytest
from datetime import datetime

from src.agents.chef_agent.event_manager import EventManager
from src.agents.chef_agent.models import (
    Budget,
    Money,
    StrategyDecision,
    HumanGateRequest,
    ProjectSummary,
    BudgetCompliance,
    EventType,
)


@pytest.fixture
def event_manager():
    """创建 EventManager 实例"""
    return EventManager(agent_name="TestChefAgent")


@pytest.fixture
def sample_budget():
    """创建示例 Budget"""
    return Budget(
        total=Money(amount=100.0, currency="USD"),
        spent=Money(amount=50.0, currency="USD"),
        estimated_remaining=Money(amount=50.0, currency="USD"),
    )


@pytest.fixture
def sample_strategy_decision():
    """创建示例 StrategyDecision"""
    return StrategyDecision(
        action="REDUCE_QUALITY",
        reason="Budget usage exceeds 80%",
        params={"target_tier": "balanced"},
    )


@pytest.fixture
def sample_human_gate_request():
    """创建示例 HumanGateRequest"""
    return HumanGateRequest(
        request_id="req_001",
        project_id="proj_001",
        reason="Max retries exceeded",
        context={"retry_count": 3, "error": "API timeout"},
        status="PENDING",
        created_at=datetime.now(),
        timeout_minutes=60,
    )


@pytest.fixture
def sample_project_summary():
    """创建示例 ProjectSummary"""
    return ProjectSummary(
        project_id="proj_001",
        total_cost=Money(amount=95.0, currency="USD"),
        budget_total=Money(amount=100.0, currency="USD"),
        budget_compliance=BudgetCompliance(is_compliant=True, overrun_amount=0.0),
        shots_count=10,
        duration=30.0,
        quality_tier="balanced",
        created_at=datetime.now(),
        completed_at=datetime.now(),
    )


class TestEventManagerBasics:
    """测试 EventManager 基础功能"""

    def test_initialization(self, event_manager):
        """测试：EventManager 正确初始化"""
        assert event_manager.agent_name == "TestChefAgent"
        assert event_manager.get_event_count() == 0
        assert len(event_manager.get_published_events()) == 0

    def test_generate_event_id(self, event_manager):
        """测试：生成唯一的事件 ID"""
        event_id1 = event_manager.generate_event_id()
        event_id2 = event_manager.generate_event_id()

        assert event_id1.startswith("evt_")
        assert event_id2.startswith("evt_")
        assert event_id1 != event_id2
        assert len(event_id1) == 16  # "evt_" + 12 hex chars


class TestBudgetAllocatedEvent:
    """测试 BUDGET_ALLOCATED 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_budget_allocated_basic(self, event_manager, sample_budget):
        """测试：发布基本的 BUDGET_ALLOCATED 事件"""
        project_id = "proj_test_001"

        event = await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.BUDGET_ALLOCATED
        assert event.actor == "TestChefAgent"
        assert event.timestamp is not None

    @pytest.mark.asyncio
    async def test_budget_allocated_event_payload(self, event_manager, sample_budget):
        """测试：BUDGET_ALLOCATED 事件 payload 包含完整数据"""
        project_id = "proj_test_002"

        event = await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="high",
            duration=60.0,
        )

        # 验证 payload 结构
        assert "budget" in event.payload
        assert "quality_tier" in event.payload
        assert "duration" in event.payload
        assert "timestamp" in event.payload

        # 验证预算数据
        budget_data = event.payload["budget"]
        assert budget_data["total"]["amount"] == 100.0
        assert budget_data["total"]["currency"] == "USD"
        assert budget_data["spent"]["amount"] == 50.0
        assert budget_data["estimated_remaining"]["amount"] == 50.0

        # 验证其他字段
        assert event.payload["quality_tier"] == "high"
        assert event.payload["duration"] == 60.0

    @pytest.mark.asyncio
    async def test_budget_allocated_with_causation(self, event_manager, sample_budget):
        """测试：BUDGET_ALLOCATED 事件包含因果关系 ID"""
        project_id = "proj_test_003"
        causation_id = "evt_trigger_001"
        cost = Money(amount=0.01, currency="USD")
        latency_ms = 100

        event = await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms,
        )

        # 验证因果链和成本信息 (Requirements 8.8, 8.9)
        assert event.causation_id == causation_id
        assert event.cost == cost
        assert event.cost.amount == 0.01
        assert event.latency_ms == 100


class TestCostOverrunWarningEvent:
    """测试 COST_OVERRUN_WARNING 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_cost_overrun_warning_basic(
        self, event_manager, sample_budget
    ):
        """测试：发布基本的 COST_OVERRUN_WARNING 事件"""
        project_id = "proj_test_004"
        usage_rate = 0.85

        event = await event_manager.publish_cost_overrun_warning(
            project_id=project_id, budget=sample_budget, usage_rate=usage_rate
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.COST_OVERRUN_WARNING
        assert event.actor == "TestChefAgent"

    @pytest.mark.asyncio
    async def test_cost_overrun_warning_payload(self, event_manager, sample_budget):
        """测试：COST_OVERRUN_WARNING 事件 payload 包含完整数据"""
        project_id = "proj_test_005"
        usage_rate = 0.82

        event = await event_manager.publish_cost_overrun_warning(
            project_id=project_id, budget=sample_budget, usage_rate=usage_rate
        )

        # 验证 payload 结构
        assert "budget" in event.payload
        assert "usage_rate" in event.payload
        assert "warning_threshold" in event.payload
        assert "message" in event.payload

        # 验证数据
        assert event.payload["usage_rate"] == 0.82
        assert event.payload["warning_threshold"] == 0.8
        assert "82.0%" in event.payload["message"]


class TestBudgetExceededEvent:
    """测试 BUDGET_EXCEEDED 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_budget_exceeded_basic(self, event_manager):
        """测试：发布基本的 BUDGET_EXCEEDED 事件"""
        project_id = "proj_test_006"
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=110.0, currency="USD"),
            estimated_remaining=Money(amount=0.0, currency="USD"),
        )
        usage_rate = 1.1

        event = await event_manager.publish_budget_exceeded(
            project_id=project_id, budget=budget, usage_rate=usage_rate
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.BUDGET_EXCEEDED
        assert event.actor == "TestChefAgent"

    @pytest.mark.asyncio
    async def test_budget_exceeded_payload(self, event_manager):
        """测试：BUDGET_EXCEEDED 事件 payload 包含超支金额"""
        project_id = "proj_test_007"
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=120.0, currency="USD"),
            estimated_remaining=Money(amount=0.0, currency="USD"),
        )
        usage_rate = 1.2

        event = await event_manager.publish_budget_exceeded(
            project_id=project_id, budget=budget, usage_rate=usage_rate
        )

        # 验证 payload 结构
        assert "budget" in event.payload
        assert "usage_rate" in event.payload
        assert "overrun_amount" in event.payload
        assert "message" in event.payload

        # 验证超支金额
        assert event.payload["overrun_amount"] == 20.0
        assert event.payload["usage_rate"] == 1.2
        assert "$120.00" in event.payload["message"]
        assert "$100.00" in event.payload["message"]


class TestStrategyUpdateEvent:
    """测试 STRATEGY_UPDATE 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_strategy_update_basic(
        self, event_manager, sample_strategy_decision
    ):
        """测试：发布基本的 STRATEGY_UPDATE 事件"""
        project_id = "proj_test_008"

        event = await event_manager.publish_strategy_update(
            project_id=project_id,
            decision=sample_strategy_decision,
            old_quality_tier="high",
            new_quality_tier="balanced",
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.STRATEGY_UPDATE
        assert event.actor == "TestChefAgent"

    @pytest.mark.asyncio
    async def test_strategy_update_payload(
        self, event_manager, sample_strategy_decision
    ):
        """测试：STRATEGY_UPDATE 事件 payload 包含完整决策信息"""
        project_id = "proj_test_009"

        event = await event_manager.publish_strategy_update(
            project_id=project_id,
            decision=sample_strategy_decision,
            old_quality_tier="high",
            new_quality_tier="balanced",
        )

        # 验证 payload 结构
        assert "decision" in event.payload
        assert "old_quality_tier" in event.payload
        assert "new_quality_tier" in event.payload
        assert "message" in event.payload

        # 验证决策数据
        decision_data = event.payload["decision"]
        assert decision_data["action"] == "REDUCE_QUALITY"
        assert decision_data["reason"] == "Budget usage exceeds 80%"
        assert decision_data["params"]["target_tier"] == "balanced"

        # 验证质量档位变更
        assert event.payload["old_quality_tier"] == "high"
        assert event.payload["new_quality_tier"] == "balanced"
        assert "high -> balanced" in event.payload["message"]


class TestHumanGateTriggeredEvent:
    """测试 HUMAN_GATE_TRIGGERED 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_human_gate_triggered_basic(
        self, event_manager, sample_human_gate_request
    ):
        """测试：发布基本的 HUMAN_GATE_TRIGGERED 事件"""
        project_id = "proj_test_010"

        event = await event_manager.publish_human_gate_triggered(
            project_id=project_id, request=sample_human_gate_request
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.HUMAN_GATE_TRIGGERED
        assert event.actor == "TestChefAgent"

    @pytest.mark.asyncio
    async def test_human_gate_triggered_payload(
        self, event_manager, sample_human_gate_request
    ):
        """测试：HUMAN_GATE_TRIGGERED 事件 payload 包含完整请求信息"""
        project_id = "proj_test_011"

        event = await event_manager.publish_human_gate_triggered(
            project_id=project_id, request=sample_human_gate_request
        )

        # 验证 payload 结构
        assert "request" in event.payload
        assert "message" in event.payload

        # 验证请求数据
        request_data = event.payload["request"]
        assert request_data["request_id"] == "req_001"
        assert request_data["project_id"] == "proj_001"
        assert request_data["reason"] == "Max retries exceeded"
        assert request_data["status"] == "PENDING"
        assert request_data["timeout_minutes"] == 60
        assert "context" in request_data
        assert request_data["context"]["retry_count"] == 3


class TestProjectDeliveredEvent:
    """测试 PROJECT_DELIVERED 事件发布"""

    @pytest.mark.asyncio
    async def test_publish_project_delivered_basic(
        self, event_manager, sample_project_summary
    ):
        """测试：发布基本的 PROJECT_DELIVERED 事件"""
        project_id = "proj_test_012"

        event = await event_manager.publish_project_delivered(
            project_id=project_id, summary=sample_project_summary
        )

        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.PROJECT_DELIVERED
        assert event.actor == "TestChefAgent"

    @pytest.mark.asyncio
    async def test_project_delivered_payload(
        self, event_manager, sample_project_summary
    ):
        """测试：PROJECT_DELIVERED 事件 payload 包含完整总结信息"""
        project_id = "proj_test_013"

        event = await event_manager.publish_project_delivered(
            project_id=project_id, summary=sample_project_summary
        )

        # 验证 payload 结构
        assert "summary" in event.payload
        assert "message" in event.payload

        # 验证总结数据
        summary_data = event.payload["summary"]
        assert summary_data["project_id"] == "proj_001"
        assert summary_data["total_cost"]["amount"] == 95.0
        assert summary_data["budget_total"]["amount"] == 100.0
        assert summary_data["budget_compliance"]["is_compliant"] is True
        assert summary_data["budget_compliance"]["overrun_amount"] == 0.0
        assert summary_data["shots_count"] == 10
        assert summary_data["duration"] == 30.0
        assert summary_data["quality_tier"] == "balanced"

        # 验证消息
        assert "10 shots" in event.payload["message"]
        assert "$95.00" in event.payload["message"]


class TestEventTracking:
    """测试事件跟踪功能"""

    @pytest.mark.asyncio
    async def test_event_tracking(self, event_manager, sample_budget):
        """测试：事件被正确跟踪"""
        project_id = "proj_test_014"

        # 初始状态
        assert event_manager.get_event_count() == 0

        # 发布第一个事件
        await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
        )

        assert event_manager.get_event_count() == 1

        # 发布第二个事件
        await event_manager.publish_cost_overrun_warning(
            project_id=project_id, budget=sample_budget, usage_rate=0.85
        )

        assert event_manager.get_event_count() == 2

        # 获取事件列表
        events = event_manager.get_published_events()
        assert len(events) == 2
        assert events[0].event_type == EventType.BUDGET_ALLOCATED
        assert events[1].event_type == EventType.COST_OVERRUN_WARNING

    @pytest.mark.asyncio
    async def test_clear_published_events(self, event_manager, sample_budget):
        """测试：清空已发布的事件"""
        project_id = "proj_test_015"

        # 发布一些事件
        await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
        )
        await event_manager.publish_cost_overrun_warning(
            project_id=project_id, budget=sample_budget, usage_rate=0.85
        )

        assert event_manager.get_event_count() == 2

        # 清空事件
        event_manager.clear_published_events()

        assert event_manager.get_event_count() == 0
        assert len(event_manager.get_published_events()) == 0


class TestEventCausationAndCost:
    """测试事件因果链和成本信息 (Requirements 8.8, 8.9)"""

    @pytest.mark.asyncio
    async def test_all_events_support_causation_id(
        self,
        event_manager,
        sample_budget,
        sample_strategy_decision,
        sample_human_gate_request,
        sample_project_summary,
    ):
        """测试：所有事件都支持因果关系 ID"""
        project_id = "proj_test_016"
        causation_id = "evt_trigger_002"

        # 测试所有事件类型
        event1 = await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
            causation_id=causation_id,
        )

        event2 = await event_manager.publish_cost_overrun_warning(
            project_id=project_id,
            budget=sample_budget,
            usage_rate=0.85,
            causation_id=causation_id,
        )

        event3 = await event_manager.publish_budget_exceeded(
            project_id=project_id,
            budget=sample_budget,
            usage_rate=1.1,
            causation_id=causation_id,
        )

        event4 = await event_manager.publish_strategy_update(
            project_id=project_id,
            decision=sample_strategy_decision,
            old_quality_tier="high",
            new_quality_tier="balanced",
            causation_id=causation_id,
        )

        event5 = await event_manager.publish_human_gate_triggered(
            project_id=project_id,
            request=sample_human_gate_request,
            causation_id=causation_id,
        )

        event6 = await event_manager.publish_project_delivered(
            project_id=project_id,
            summary=sample_project_summary,
            causation_id=causation_id,
        )

        # 验证所有事件都包含因果关系 ID
        for event in [event1, event2, event3, event4, event5, event6]:
            assert event.causation_id == causation_id

    @pytest.mark.asyncio
    async def test_all_events_support_cost_and_latency(
        self,
        event_manager,
        sample_budget,
        sample_strategy_decision,
        sample_human_gate_request,
        sample_project_summary,
    ):
        """测试：所有事件都支持成本和延迟信息"""
        project_id = "proj_test_017"
        cost = Money(amount=0.02, currency="USD")
        latency_ms = 200

        # 测试所有事件类型
        event1 = await event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
            cost=cost,
            latency_ms=latency_ms,
        )

        event2 = await event_manager.publish_cost_overrun_warning(
            project_id=project_id,
            budget=sample_budget,
            usage_rate=0.85,
            cost=cost,
            latency_ms=latency_ms,
        )

        event3 = await event_manager.publish_budget_exceeded(
            project_id=project_id,
            budget=sample_budget,
            usage_rate=1.1,
            cost=cost,
            latency_ms=latency_ms,
        )

        event4 = await event_manager.publish_strategy_update(
            project_id=project_id,
            decision=sample_strategy_decision,
            old_quality_tier="high",
            new_quality_tier="balanced",
            cost=cost,
            latency_ms=latency_ms,
        )

        event5 = await event_manager.publish_human_gate_triggered(
            project_id=project_id,
            request=sample_human_gate_request,
            cost=cost,
            latency_ms=latency_ms,
        )

        event6 = await event_manager.publish_project_delivered(
            project_id=project_id,
            summary=sample_project_summary,
            cost=cost,
            latency_ms=latency_ms,
        )

        # 验证所有事件都包含成本和延迟信息
        for event in [event1, event2, event3, event4, event5, event6]:
            assert event.cost == cost
            assert event.cost.amount == 0.02
            assert event.latency_ms == 200
