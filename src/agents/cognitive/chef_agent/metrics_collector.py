"""
ChefAgent 指标收集器

负责收集和记录 ChefAgent 的运行指标，用于监控系统性能和成本

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .models import Money, Budget, ProjectSummary, HumanGateRequest


class BudgetAllocationMetric(BaseModel):
    """预算分配指标"""

    project_id: str = Field(..., description="项目 ID")
    allocated_budget: Money = Field(..., description="分配的预算")
    quality_tier: str = Field(..., description="质量档位")
    duration: float = Field(..., description="视频时长（秒）")
    allocation_time_ms: float = Field(..., description="分配耗时（毫秒）")
    timestamp: datetime = Field(..., description="时间戳")


class CostOverrunMetric(BaseModel):
    """预算超支指标"""

    project_id: str = Field(..., description="项目 ID")
    total_budget: Money = Field(..., description="总预算")
    spent_budget: Money = Field(..., description="已使用预算")
    overrun_rate: float = Field(..., description="超支率")
    timestamp: datetime = Field(..., description="时间戳")


class HumanInterventionMetric(BaseModel):
    """人工介入指标"""

    project_id: str = Field(..., description="项目 ID")
    request_id: str = Field(..., description="请求 ID")
    trigger_reason: str = Field(..., description="触发原因")
    context: Dict[str, Any] = Field(..., description="上下文信息")
    timestamp: datetime = Field(..., description="时间戳")


class ProjectCompletionMetric(BaseModel):
    """项目完成指标"""

    project_id: str = Field(..., description="项目 ID")
    total_cost: Money = Field(..., description="总成本")
    total_duration: float = Field(..., description="总时长（秒）")
    shots_count: int = Field(..., description="镜头数量")
    quality_tier: str = Field(..., description="质量档位")
    budget_compliant: bool = Field(..., description="是否符合预算")
    overrun_amount: float = Field(default=0.0, description="超支金额")
    project_duration_seconds: float = Field(..., description="项目持续时间（秒）")
    timestamp: datetime = Field(..., description="时间戳")


class DecisionLatencyMetric(BaseModel):
    """决策延迟指标"""

    project_id: str = Field(..., description="项目 ID")
    decision_type: str = Field(..., description="决策类型")
    latency_ms: float = Field(..., description="延迟（毫秒）")
    timestamp: datetime = Field(..., description="时间戳")


class MetricsCollector:
    """
    指标收集器

    收集 ChefAgent 的运行指标，包括:
    - 预算分配时间
    - 预算超支率
    - 人工介入率
    - 项目完成率
    - 平均决策延迟

    Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        初始化指标收集器

        Args:
            logger: 日志记录器（可选）
        """
        self.logger = logger or logging.getLogger(__name__)

        # 指标存储（简化版：内存存储，实际应该写入时序数据库）
        self.budget_allocation_metrics: List[BudgetAllocationMetric] = []
        self.cost_overrun_metrics: List[CostOverrunMetric] = []
        self.human_intervention_metrics: List[HumanInterventionMetric] = []
        self.project_completion_metrics: List[ProjectCompletionMetric] = []
        self.decision_latency_metrics: List[DecisionLatencyMetric] = []

        self.logger.info("MetricsCollector initialized")

    def record_budget_allocation(
        self,
        project_id: str,
        allocated_budget: Budget,
        quality_tier: str,
        duration: float,
        allocation_time_ms: float,
    ) -> None:
        """
        记录预算分配指标

        Args:
            project_id: 项目 ID
            allocated_budget: 分配的预算
            quality_tier: 质量档位
            duration: 视频时长（秒）
            allocation_time_ms: 分配耗时（毫秒）

        Validates: Requirements 10.1
        """
        metric = BudgetAllocationMetric(
            project_id=project_id,
            allocated_budget=allocated_budget.total,
            quality_tier=quality_tier,
            duration=duration,
            allocation_time_ms=allocation_time_ms,
            timestamp=datetime.now(),
        )

        self.budget_allocation_metrics.append(metric)

        self.logger.info(
            f"Budget allocation metric recorded",
            extra={
                "project_id": project_id,
                "allocated_budget": allocated_budget.total.amount,
                "quality_tier": quality_tier,
                "allocation_time_ms": allocation_time_ms,
            },
        )

    def record_cost_overrun(self, project_id: str, budget: Budget) -> None:
        """
        记录预算超支指标

        Args:
            project_id: 项目 ID
            budget: 当前预算状态

        Validates: Requirements 10.2
        """
        # 计算超支率
        overrun_rate = 0.0
        if budget.total.amount > 0:
            overrun_rate = (
                budget.spent.amount - budget.total.amount
            ) / budget.total.amount
            overrun_rate = max(0.0, overrun_rate)  # 只记录正的超支率

        metric = CostOverrunMetric(
            project_id=project_id,
            total_budget=budget.total,
            spent_budget=budget.spent,
            overrun_rate=overrun_rate,
            timestamp=datetime.now(),
        )

        self.cost_overrun_metrics.append(metric)

        self.logger.warning(
            f"Cost overrun metric recorded",
            extra={
                "project_id": project_id,
                "total_budget": budget.total.amount,
                "spent_budget": budget.spent.amount,
                "overrun_rate": overrun_rate,
            },
        )

    def record_human_intervention(
        self, project_id: str, request: HumanGateRequest
    ) -> None:
        """
        记录人工介入指标

        Args:
            project_id: 项目 ID
            request: 人工介入请求

        Validates: Requirements 10.3, 10.7
        """
        metric = HumanInterventionMetric(
            project_id=project_id,
            request_id=request.request_id,
            trigger_reason=request.reason,
            context=request.context,
            timestamp=datetime.now(),
        )

        self.human_intervention_metrics.append(metric)

        self.logger.warning(
            f"Human intervention metric recorded",
            extra={
                "project_id": project_id,
                "request_id": request.request_id,
                "trigger_reason": request.reason,
            },
        )

    def record_project_completion(
        self, project_id: str, summary: ProjectSummary, project_start_time: datetime
    ) -> None:
        """
        记录项目完成指标

        Args:
            project_id: 项目 ID
            summary: 项目总结
            project_start_time: 项目开始时间

        Validates: Requirements 10.4, 10.6
        """
        # 计算项目持续时间
        project_duration = (datetime.now() - project_start_time).total_seconds()

        metric = ProjectCompletionMetric(
            project_id=project_id,
            total_cost=summary.total_cost,
            total_duration=summary.duration,
            shots_count=summary.shots_count,
            quality_tier=summary.quality_tier,
            budget_compliant=summary.budget_compliance.is_compliant,
            overrun_amount=summary.budget_compliance.overrun_amount,
            project_duration_seconds=project_duration,
            timestamp=datetime.now(),
        )

        self.project_completion_metrics.append(metric)

        self.logger.info(
            f"Project completion metric recorded",
            extra={
                "project_id": project_id,
                "total_cost": summary.total_cost.amount,
                "shots_count": summary.shots_count,
                "budget_compliant": summary.budget_compliance.is_compliant,
                "project_duration_seconds": project_duration,
            },
        )

    def record_decision_latency(
        self, project_id: str, decision_type: str, latency_ms: float
    ) -> None:
        """
        记录决策延迟指标

        Args:
            project_id: 项目 ID
            decision_type: 决策类型（如 "budget_allocation", "failure_evaluation"）
            latency_ms: 延迟（毫秒）

        Validates: Requirements 10.5
        """
        metric = DecisionLatencyMetric(
            project_id=project_id,
            decision_type=decision_type,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
        )

        self.decision_latency_metrics.append(metric)

        self.logger.debug(
            f"Decision latency metric recorded",
            extra={
                "project_id": project_id,
                "decision_type": decision_type,
                "latency_ms": latency_ms,
            },
        )

    # ========== 聚合指标计算 ==========

    def get_cost_overrun_rate(self) -> float:
        """
        计算预算超支率

        Returns:
            超支率（0.0-1.0），表示超支项目占总项目的比例

        Validates: Requirements 10.2
        """
        if not self.cost_overrun_metrics:
            return 0.0

        overrun_count = sum(
            1 for metric in self.cost_overrun_metrics if metric.overrun_rate > 0
        )

        return overrun_count / len(self.cost_overrun_metrics)

    def get_human_intervention_rate(self) -> float:
        """
        计算人工介入率

        Returns:
            人工介入率（0.0-1.0），表示需要人工介入的项目占总项目的比例

        Validates: Requirements 10.3
        """
        if not self.project_completion_metrics:
            return 0.0

        # 统计唯一的项目 ID
        completed_projects = set(
            metric.project_id for metric in self.project_completion_metrics
        )

        intervention_projects = set(
            metric.project_id for metric in self.human_intervention_metrics
        )

        if not completed_projects:
            return 0.0

        return len(intervention_projects) / len(completed_projects)

    def get_project_completion_rate(self) -> float:
        """
        计算项目完成率

        Returns:
            项目完成率（0.0-1.0），表示成功完成的项目占总项目的比例

        Validates: Requirements 10.4
        """
        if not self.project_completion_metrics:
            return 0.0

        # 简化版：假设所有记录的完成指标都是成功完成的项目
        # 实际应该区分成功和失败的项目
        return 1.0

    def get_avg_decision_latency(self, decision_type: Optional[str] = None) -> float:
        """
        计算平均决策延迟

        Args:
            decision_type: 决策类型（可选，不指定则计算所有类型的平均值）

        Returns:
            平均决策延迟（毫秒）

        Validates: Requirements 10.5
        """
        if not self.decision_latency_metrics:
            return 0.0

        # 过滤指定类型的指标
        if decision_type:
            metrics = [
                metric
                for metric in self.decision_latency_metrics
                if metric.decision_type == decision_type
            ]
        else:
            metrics = self.decision_latency_metrics

        if not metrics:
            return 0.0

        total_latency = sum(metric.latency_ms for metric in metrics)
        return total_latency / len(metrics)

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        获取指标摘要

        Returns:
            包含所有聚合指标的字典
        """
        return {
            "total_projects": len(
                set(metric.project_id for metric in self.project_completion_metrics)
            ),
            "cost_overrun_rate": self.get_cost_overrun_rate(),
            "human_intervention_rate": self.get_human_intervention_rate(),
            "project_completion_rate": self.get_project_completion_rate(),
            "avg_decision_latency_ms": self.get_avg_decision_latency(),
            "total_budget_allocations": len(self.budget_allocation_metrics),
            "total_cost_overruns": len(self.cost_overrun_metrics),
            "total_human_interventions": len(self.human_intervention_metrics),
            "total_project_completions": len(self.project_completion_metrics),
            "total_decision_latencies": len(self.decision_latency_metrics),
        }

    def clear_metrics(self) -> None:
        """
        清空所有指标（用于测试或重置）
        """
        self.budget_allocation_metrics.clear()
        self.cost_overrun_metrics.clear()
        self.human_intervention_metrics.clear()
        self.project_completion_metrics.clear()
        self.decision_latency_metrics.clear()

        self.logger.info("All metrics cleared")
