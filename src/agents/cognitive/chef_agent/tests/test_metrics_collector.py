"""
MetricsCollector 单元测试

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
"""

import pytest
from datetime import datetime, timedelta

from ..metrics_collector import MetricsCollector
from ...models import Money, Budget, ProjectSummary, BudgetCompliance, HumanGateRequest


@pytest.fixture
def metrics_collector():
    """创建 MetricsCollector 实例"""
    return MetricsCollector()


@pytest.fixture
def sample_budget():
    """创建示例预算"""
    return Budget(
        total=Money(amount=100.0, currency="USD"),
        spent=Money(amount=50.0, currency="USD"),
        estimated_remaining=Money(amount=50.0, currency="USD"),
    )


@pytest.fixture
def sample_overrun_budget():
    """创建超支预算"""
    return Budget(
        total=Money(amount=100.0, currency="USD"),
        spent=Money(amount=120.0, currency="USD"),
        estimated_remaining=Money(amount=0.0, currency="USD"),  # 超支时剩余为 0
    )


@pytest.fixture
def sample_human_gate_request():
    """创建示例人工介入请求"""
    return HumanGateRequest(
        request_id="req_001",
        project_id="proj_001",
        reason="Max retries exceeded",
        context={"error": "API timeout"},
        status="PENDING",
        created_at=datetime.now(),
        timeout_minutes=60,
    )


@pytest.fixture
def sample_project_summary():
    """创建示例项目总结"""
    return ProjectSummary(
        project_id="proj_001",
        total_cost=Money(amount=95.0, currency="USD"),
        budget_total=Money(amount=100.0, currency="USD"),
        budget_compliance=BudgetCompliance(is_compliant=True, overrun_amount=0.0),
        shots_count=5,
        duration=30.0,
        quality_tier="balanced",
        created_at=datetime.now() - timedelta(hours=1),
        completed_at=datetime.now(),
    )


class TestMetricsCollector:
    """MetricsCollector 测试类"""

    def test_initialization(self, metrics_collector):
        """测试初始化"""
        assert metrics_collector is not None
        assert len(metrics_collector.budget_allocation_metrics) == 0
        assert len(metrics_collector.cost_overrun_metrics) == 0
        assert len(metrics_collector.human_intervention_metrics) == 0
        assert len(metrics_collector.project_completion_metrics) == 0
        assert len(metrics_collector.decision_latency_metrics) == 0

    def test_record_budget_allocation(self, metrics_collector, sample_budget):
        """
        测试记录预算分配指标

        Validates: Requirements 10.1
        """
        metrics_collector.record_budget_allocation(
            project_id="proj_001",
            allocated_budget=sample_budget,
            quality_tier="balanced",
            duration=30.0,
            allocation_time_ms=15.5,
        )

        assert len(metrics_collector.budget_allocation_metrics) == 1

        metric = metrics_collector.budget_allocation_metrics[0]
        assert metric.project_id == "proj_001"
        assert metric.allocated_budget.amount == 100.0
        assert metric.quality_tier == "balanced"
        assert metric.duration == 30.0
        assert metric.allocation_time_ms == 15.5
        assert metric.timestamp is not None

    def test_record_cost_overrun(self, metrics_collector, sample_overrun_budget):
        """
        测试记录预算超支指标

        Validates: Requirements 10.2
        """
        metrics_collector.record_cost_overrun(
            project_id="proj_001", budget=sample_overrun_budget
        )

        assert len(metrics_collector.cost_overrun_metrics) == 1

        metric = metrics_collector.cost_overrun_metrics[0]
        assert metric.project_id == "proj_001"
        assert metric.total_budget.amount == 100.0
        assert metric.spent_budget.amount == 120.0
        assert metric.overrun_rate == 0.2  # (120 - 100) / 100 = 0.2
        assert metric.timestamp is not None

    def test_record_cost_overrun_no_overrun(self, metrics_collector, sample_budget):
        """测试记录预算未超支的情况"""
        metrics_collector.record_cost_overrun(
            project_id="proj_001", budget=sample_budget
        )

        assert len(metrics_collector.cost_overrun_metrics) == 1

        metric = metrics_collector.cost_overrun_metrics[0]
        assert metric.overrun_rate == 0.0  # 未超支，超支率为 0

    def test_record_human_intervention(
        self, metrics_collector, sample_human_gate_request
    ):
        """
        测试记录人工介入指标

        Validates: Requirements 10.3, 10.7
        """
        metrics_collector.record_human_intervention(
            project_id="proj_001", request=sample_human_gate_request
        )

        assert len(metrics_collector.human_intervention_metrics) == 1

        metric = metrics_collector.human_intervention_metrics[0]
        assert metric.project_id == "proj_001"
        assert metric.request_id == "req_001"
        assert metric.trigger_reason == "Max retries exceeded"
        assert metric.context == {"error": "API timeout"}
        assert metric.timestamp is not None

    def test_record_project_completion(self, metrics_collector, sample_project_summary):
        """
        测试记录项目完成指标

        Validates: Requirements 10.4, 10.6
        """
        project_start_time = datetime.now() - timedelta(hours=2)

        metrics_collector.record_project_completion(
            project_id="proj_001",
            summary=sample_project_summary,
            project_start_time=project_start_time,
        )

        assert len(metrics_collector.project_completion_metrics) == 1

        metric = metrics_collector.project_completion_metrics[0]
        assert metric.project_id == "proj_001"
        assert metric.total_cost.amount == 95.0
        assert metric.total_duration == 30.0
        assert metric.shots_count == 5
        assert metric.quality_tier == "balanced"
        assert metric.budget_compliant is True
        assert metric.overrun_amount == 0.0
        assert metric.project_duration_seconds > 0  # 应该大于 0
        assert metric.timestamp is not None

    def test_record_decision_latency(self, metrics_collector):
        """
        测试记录决策延迟指标

        Validates: Requirements 10.5
        """
        metrics_collector.record_decision_latency(
            project_id="proj_001", decision_type="budget_allocation", latency_ms=25.3
        )

        assert len(metrics_collector.decision_latency_metrics) == 1

        metric = metrics_collector.decision_latency_metrics[0]
        assert metric.project_id == "proj_001"
        assert metric.decision_type == "budget_allocation"
        assert metric.latency_ms == 25.3
        assert metric.timestamp is not None

    def test_get_cost_overrun_rate(
        self, metrics_collector, sample_budget, sample_overrun_budget
    ):
        """
        测试计算预算超支率

        Validates: Requirements 10.2
        """
        # 记录 2 个项目，1 个超支
        metrics_collector.record_cost_overrun("proj_001", sample_overrun_budget)
        metrics_collector.record_cost_overrun("proj_002", sample_budget)

        overrun_rate = metrics_collector.get_cost_overrun_rate()
        assert overrun_rate == 0.5  # 1/2 = 0.5

    def test_get_cost_overrun_rate_empty(self, metrics_collector):
        """测试空指标时的超支率"""
        overrun_rate = metrics_collector.get_cost_overrun_rate()
        assert overrun_rate == 0.0

    def test_get_human_intervention_rate(
        self, metrics_collector, sample_human_gate_request, sample_project_summary
    ):
        """
        测试计算人工介入率

        Validates: Requirements 10.3
        """
        # 记录 2 个完成的项目
        metrics_collector.record_project_completion(
            "proj_001", sample_project_summary, datetime.now() - timedelta(hours=1)
        )

        summary_2 = sample_project_summary.model_copy()
        summary_2.project_id = "proj_002"
        metrics_collector.record_project_completion(
            "proj_002", summary_2, datetime.now() - timedelta(hours=1)
        )

        # 记录 1 个人工介入
        metrics_collector.record_human_intervention(
            "proj_001", sample_human_gate_request
        )

        intervention_rate = metrics_collector.get_human_intervention_rate()
        assert intervention_rate == 0.5  # 1/2 = 0.5

    def test_get_human_intervention_rate_empty(self, metrics_collector):
        """测试空指标时的人工介入率"""
        intervention_rate = metrics_collector.get_human_intervention_rate()
        assert intervention_rate == 0.0

    def test_get_project_completion_rate(
        self, metrics_collector, sample_project_summary
    ):
        """
        测试计算项目完成率

        Validates: Requirements 10.4
        """
        metrics_collector.record_project_completion(
            "proj_001", sample_project_summary, datetime.now() - timedelta(hours=1)
        )

        completion_rate = metrics_collector.get_project_completion_rate()
        assert completion_rate == 1.0  # 简化版：所有记录的项目都是成功的

    def test_get_project_completion_rate_empty(self, metrics_collector):
        """测试空指标时的项目完成率"""
        completion_rate = metrics_collector.get_project_completion_rate()
        assert completion_rate == 0.0

    def test_get_avg_decision_latency(self, metrics_collector):
        """
        测试计算平均决策延迟

        Validates: Requirements 10.5
        """
        # 记录多个决策延迟
        metrics_collector.record_decision_latency("proj_001", "budget_allocation", 10.0)
        metrics_collector.record_decision_latency("proj_001", "budget_allocation", 20.0)
        metrics_collector.record_decision_latency(
            "proj_001", "failure_evaluation", 30.0
        )

        # 测试所有类型的平均延迟
        avg_latency = metrics_collector.get_avg_decision_latency()
        assert avg_latency == 20.0  # (10 + 20 + 30) / 3 = 20

        # 测试特定类型的平均延迟
        avg_budget_latency = metrics_collector.get_avg_decision_latency(
            "budget_allocation"
        )
        assert avg_budget_latency == 15.0  # (10 + 20) / 2 = 15

        avg_failure_latency = metrics_collector.get_avg_decision_latency(
            "failure_evaluation"
        )
        assert avg_failure_latency == 30.0

    def test_get_avg_decision_latency_empty(self, metrics_collector):
        """测试空指标时的平均决策延迟"""
        avg_latency = metrics_collector.get_avg_decision_latency()
        assert avg_latency == 0.0

    def test_get_metrics_summary(
        self,
        metrics_collector,
        sample_budget,
        sample_human_gate_request,
        sample_project_summary,
    ):
        """测试获取指标摘要"""
        # 记录各种指标
        metrics_collector.record_budget_allocation(
            "proj_001", sample_budget, "balanced", 30.0, 15.0
        )
        metrics_collector.record_cost_overrun("proj_001", sample_budget)
        metrics_collector.record_human_intervention(
            "proj_001", sample_human_gate_request
        )
        metrics_collector.record_project_completion(
            "proj_001", sample_project_summary, datetime.now() - timedelta(hours=1)
        )
        metrics_collector.record_decision_latency("proj_001", "budget_allocation", 25.0)

        summary = metrics_collector.get_metrics_summary()

        assert summary["total_projects"] == 1
        assert summary["total_budget_allocations"] == 1
        assert summary["total_cost_overruns"] == 1
        assert summary["total_human_interventions"] == 1
        assert summary["total_project_completions"] == 1
        assert summary["total_decision_latencies"] == 1
        assert "cost_overrun_rate" in summary
        assert "human_intervention_rate" in summary
        assert "project_completion_rate" in summary
        assert "avg_decision_latency_ms" in summary

    def test_clear_metrics(self, metrics_collector, sample_budget):
        """测试清空指标"""
        # 记录一些指标
        metrics_collector.record_budget_allocation(
            "proj_001", sample_budget, "balanced", 30.0, 15.0
        )
        metrics_collector.record_decision_latency("proj_001", "budget_allocation", 25.0)

        assert len(metrics_collector.budget_allocation_metrics) == 1
        assert len(metrics_collector.decision_latency_metrics) == 1

        # 清空指标
        metrics_collector.clear_metrics()

        assert len(metrics_collector.budget_allocation_metrics) == 0
        assert len(metrics_collector.cost_overrun_metrics) == 0
        assert len(metrics_collector.human_intervention_metrics) == 0
        assert len(metrics_collector.project_completion_metrics) == 0
        assert len(metrics_collector.decision_latency_metrics) == 0

    def test_multiple_projects_metrics(
        self,
        metrics_collector,
        sample_budget,
        sample_overrun_budget,
        sample_project_summary,
    ):
        """测试多个项目的指标收集"""
        # 项目 1: 正常完成
        metrics_collector.record_budget_allocation(
            "proj_001", sample_budget, "balanced", 30.0, 15.0
        )
        metrics_collector.record_project_completion(
            "proj_001", sample_project_summary, datetime.now() - timedelta(hours=1)
        )

        # 项目 2: 超支
        metrics_collector.record_budget_allocation(
            "proj_002", sample_overrun_budget, "high", 60.0, 20.0
        )
        metrics_collector.record_cost_overrun("proj_002", sample_overrun_budget)

        summary_2 = sample_project_summary.model_copy()
        summary_2.project_id = "proj_002"
        summary_2.budget_compliance = BudgetCompliance(
            is_compliant=False, overrun_amount=20.0
        )
        metrics_collector.record_project_completion(
            "proj_002", summary_2, datetime.now() - timedelta(hours=2)
        )

        # 验证指标
        assert len(metrics_collector.budget_allocation_metrics) == 2
        assert len(metrics_collector.cost_overrun_metrics) == 1
        assert len(metrics_collector.project_completion_metrics) == 2

        summary = metrics_collector.get_metrics_summary()
        assert summary["total_projects"] == 2
        assert summary["cost_overrun_rate"] == 1.0  # 1/1 = 1.0 (只有一个记录了超支)
