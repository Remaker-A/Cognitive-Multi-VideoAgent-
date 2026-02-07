"""
ChefAgent 事件管理器

负责发布 ChefAgent 相关的事件到事件总线

Requirements: 1.5, 2.3, 2.4, 3.2, 4.6, 6.6, 8.8, 8.9
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .models import (
    Event,
    EventType,
    Money,
    Budget,
    StrategyDecision,
    HumanGateRequest,
    ProjectSummary,
)


class EventManager:
    """
    ChefAgent 事件管理器

    职责:
    - 发布预算相关事件 (BUDGET_ALLOCATED, COST_OVERRUN_WARNING, BUDGET_EXCEEDED)
    - 发布策略调整事件 (STRATEGY_UPDATE)
    - 发布人工介入事件 (HUMAN_GATE_TRIGGERED)
    - 发布项目完成事件 (PROJECT_DELIVERED)
    - 确保所有事件包含完整的因果链和成本信息
    """

    def __init__(
        self, agent_name: str = "ChefAgent", logger: Optional[logging.Logger] = None
    ):
        """
        初始化事件管理器

        Args:
            agent_name: Agent 名称
            logger: 日志记录器（可选）
        """
        self.agent_name = agent_name
        self.logger = logger or logging.getLogger(__name__)
        self._published_events: list[Event] = []

    def generate_event_id(self) -> str:
        """
        生成唯一的事件 ID

        Returns:
            事件 ID，格式为 evt_{12位十六进制}
        """
        return f"evt_{uuid.uuid4().hex[:12]}"

    async def publish_budget_allocated(
        self,
        project_id: str,
        budget: Budget,
        quality_tier: str,
        duration: float,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 BUDGET_ALLOCATED 事件

        当预算分配完成时发布此事件

        Args:
            project_id: 项目 ID
            budget: 分配的预算对象
            quality_tier: 质量档位
            duration: 项目时长（秒）
            causation_id: 因果关系 ID（触发此事件的事件 ID）
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 1.5, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "budget": {
                "total": {
                    "amount": budget.total.amount,
                    "currency": budget.total.currency,
                },
                "spent": {
                    "amount": budget.spent.amount,
                    "currency": budget.spent.currency,
                },
                "estimated_remaining": {
                    "amount": budget.estimated_remaining.amount,
                    "currency": budget.estimated_remaining.currency,
                },
            },
            "quality_tier": quality_tier,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.BUDGET_ALLOCATED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.info(
            f"Published BUDGET_ALLOCATED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "budget_total": budget.total.amount,
                "quality_tier": quality_tier,
                "duration": duration,
            },
        )

        return event

    async def publish_cost_overrun_warning(
        self,
        project_id: str,
        budget: Budget,
        usage_rate: float,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 COST_OVERRUN_WARNING 事件

        当预算使用率超过 80% 时发布此事件

        Args:
            project_id: 项目 ID
            budget: 当前预算状态
            usage_rate: 预算使用率（0.0-1.0）
            causation_id: 因果关系 ID
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 2.3, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "budget": {
                "total": {
                    "amount": budget.total.amount,
                    "currency": budget.total.currency,
                },
                "spent": {
                    "amount": budget.spent.amount,
                    "currency": budget.spent.currency,
                },
                "estimated_remaining": {
                    "amount": budget.estimated_remaining.amount,
                    "currency": budget.estimated_remaining.currency,
                },
            },
            "usage_rate": usage_rate,
            "warning_threshold": 0.8,
            "message": f"Budget usage has reached {usage_rate * 100:.1f}%",
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.COST_OVERRUN_WARNING,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.warning(
            f"Published COST_OVERRUN_WARNING event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "usage_rate": usage_rate,
                "spent": budget.spent.amount,
                "total": budget.total.amount,
            },
        )

        return event

    async def publish_budget_exceeded(
        self,
        project_id: str,
        budget: Budget,
        usage_rate: float,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 BUDGET_EXCEEDED 事件

        当预算使用率超过 100% 时发布此事件

        Args:
            project_id: 项目 ID
            budget: 当前预算状态
            usage_rate: 预算使用率（0.0-1.0）
            causation_id: 因果关系 ID
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 2.4, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "budget": {
                "total": {
                    "amount": budget.total.amount,
                    "currency": budget.total.currency,
                },
                "spent": {
                    "amount": budget.spent.amount,
                    "currency": budget.spent.currency,
                },
                "estimated_remaining": {
                    "amount": budget.estimated_remaining.amount,
                    "currency": budget.estimated_remaining.currency,
                },
            },
            "usage_rate": usage_rate,
            "overrun_amount": budget.spent.amount - budget.total.amount,
            "message": (
                f"Budget exceeded: spent ${budget.spent.amount:.2f} "
                f"of ${budget.total.amount:.2f}"
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.BUDGET_EXCEEDED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.error(
            f"Published BUDGET_EXCEEDED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "usage_rate": usage_rate,
                "spent": budget.spent.amount,
                "total": budget.total.amount,
                "overrun": budget.spent.amount - budget.total.amount,
            },
        )

        return event

    async def publish_strategy_update(
        self,
        project_id: str,
        decision: StrategyDecision,
        old_quality_tier: str,
        new_quality_tier: str,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 STRATEGY_UPDATE 事件

        当策略调整决策被应用时发布此事件

        Args:
            project_id: 项目 ID
            decision: 策略决策对象
            old_quality_tier: 原质量档位
            new_quality_tier: 新质量档位
            causation_id: 因果关系 ID
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 3.2, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "decision": {
                "action": decision.action,
                "reason": decision.reason,
                "params": decision.params,
            },
            "old_quality_tier": old_quality_tier,
            "new_quality_tier": new_quality_tier,
            "message": f"Strategy updated: {old_quality_tier} -> {new_quality_tier}",
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.STRATEGY_UPDATE,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.info(
            f"Published STRATEGY_UPDATE event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "action": decision.action,
                "old_tier": old_quality_tier,
                "new_tier": new_quality_tier,
                "reason": decision.reason,
            },
        )

        return event

    async def publish_human_gate_triggered(
        self,
        project_id: str,
        request: HumanGateRequest,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 HUMAN_GATE_TRIGGERED 事件

        当需要人工介入时发布此事件

        Args:
            project_id: 项目 ID
            request: 人工介入请求对象
            causation_id: 因果关系 ID
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 4.6, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "request": {
                "request_id": request.request_id,
                "project_id": request.project_id,
                "reason": request.reason,
                "context": request.context,
                "status": request.status,
                "created_at": request.created_at.isoformat(),
                "timeout_minutes": request.timeout_minutes,
            },
            "message": f"Human intervention required: {request.reason}",
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.HUMAN_GATE_TRIGGERED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.warning(
            f"Published HUMAN_GATE_TRIGGERED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "request_id": request.request_id,
                "reason": request.reason,
                "timeout_minutes": request.timeout_minutes,
            },
        )

        return event

    async def publish_project_delivered(
        self,
        project_id: str,
        summary: ProjectSummary,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Event:
        """
        发布 PROJECT_DELIVERED 事件

        当项目完成并通过验证时发布此事件

        Args:
            project_id: 项目 ID
            summary: 项目总结报告
            causation_id: 因果关系 ID
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据

        Returns:
            发布的事件对象

        Validates: Requirements 6.6, 8.8, 8.9
        """
        event_id = self.generate_event_id()

        # 构建事件 payload
        payload = {
            "summary": {
                "project_id": summary.project_id,
                "total_cost": {
                    "amount": summary.total_cost.amount,
                    "currency": summary.total_cost.currency,
                },
                "budget_total": {
                    "amount": summary.budget_total.amount,
                    "currency": summary.budget_total.currency,
                },
                "budget_compliance": {
                    "is_compliant": summary.budget_compliance.is_compliant,
                    "overrun_amount": summary.budget_compliance.overrun_amount,
                },
                "shots_count": summary.shots_count,
                "duration": summary.duration,
                "quality_tier": summary.quality_tier,
                "created_at": summary.created_at.isoformat(),
                "completed_at": summary.completed_at.isoformat(),
            },
            "message": (
                f"Project delivered: {summary.shots_count} shots, "
                f"${summary.total_cost.amount:.2f} total cost"
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.PROJECT_DELIVERED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            timestamp=datetime.now().isoformat(),
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {},
        )

        # 记录事件
        self._published_events.append(event)

        # 记录日志
        self.logger.info(
            f"Published PROJECT_DELIVERED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "total_cost": summary.total_cost.amount,
                "budget_compliant": summary.budget_compliance.is_compliant,
                "shots_count": summary.shots_count,
                "duration": summary.duration,
            },
        )

        return event

    def get_published_events(self) -> list[Event]:
        """
        获取已发布的事件列表

        Returns:
            事件列表
        """
        return self._published_events.copy()

    def clear_published_events(self) -> None:
        """清空已发布的事件列表"""
        self._published_events.clear()

    def get_event_count(self) -> int:
        """
        获取已发布的事件数量

        Returns:
            事件数量
        """
        return len(self._published_events)
