"""
ChefAgent 数据模型

Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class Money(BaseModel):
    """货币金额"""

    amount: float = Field(..., ge=0, description="金额")
    currency: str = Field(default="USD", description="货币单位")


class Budget(BaseModel):
    """
    预算对象

    Requirements: 1.1, 2.1
    """

    total: Money = Field(..., description="总预算")
    spent: Money = Field(..., description="已使用预算")
    estimated_remaining: Money = Field(..., description="预计剩余预算")
    breakdown: Dict[str, Money] = Field(default_factory=dict, description="成本分解")


class BudgetStatus(str, Enum):
    """预算状态"""

    OK = "OK"
    WARNING = "WARNING"
    EXCEEDED = "EXCEEDED"


class FailureReport(BaseModel):
    """
    失败报告

    Requirements: 4.1
    """

    task_id: str = Field(..., description="任务 ID")
    error_type: str = Field(..., description="错误类型")
    error_message: str = Field(..., description="错误消息")
    retry_count: int = Field(..., ge=0, description="重试次数")
    cost_impact: float = Field(..., ge=0, description="成本影响（美元）")
    severity: str = Field(..., description="严重程度: low, medium, high, critical")
    timestamp: datetime = Field(..., description="时间戳")


class EscalationDecision(BaseModel):
    """
    升级决策

    Requirements: 4.2, 4.3, 4.4, 4.5
    """

    action: str = Field(..., description="操作: AUTO_RETRY, HUMAN_GATE")
    reason: str = Field(..., description="原因")
    priority: str = Field(..., description="优先级: low, medium, high, critical")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class StrategyDecision(BaseModel):
    """
    策略决策

    Requirements: 3.1
    """

    action: str = Field(
        ..., description="操作: CONTINUE, REDUCE_QUALITY, INCREASE_BUDGET"
    )
    reason: str = Field(..., description="原因")
    params: Dict[str, Any] = Field(default_factory=dict, description="参数")


class UserDecision(BaseModel):
    """
    用户决策

    Requirements: 5.1, 5.2, 5.3
    """

    action: str = Field(..., description="操作: approve, revise, reject")
    notes: Optional[str] = Field(None, description="备注")
    decided_at: datetime = Field(..., description="决策时间")
    decided_by: str = Field(..., description="决策人")


class HumanGateRequest(BaseModel):
    """
    人工介入请求

    Requirements: 4.6, 5.4
    """

    request_id: str = Field(..., description="请求 ID")
    project_id: str = Field(..., description="项目 ID")
    reason: str = Field(..., description="触发原因")
    context: Dict[str, Any] = Field(..., description="上下文信息")
    status: str = Field(..., description="状态: PENDING, APPROVED, REJECTED, TIMEOUT")
    created_at: datetime = Field(..., description="创建时间")
    timeout_minutes: int = Field(default=60, description="超时时间（分钟）")
    decision: Optional[UserDecision] = Field(None, description="用户决策")


class ProjectAction(BaseModel):
    """项目操作"""

    action: str = Field(..., description="操作类型")
    reason: str = Field(..., description="原因")
    params: Dict[str, Any] = Field(default_factory=dict, description="参数")


class BudgetCompliance(BaseModel):
    """
    预算合规性

    Requirements: 6.3, 6.4
    """

    is_compliant: bool = Field(..., description="是否合规")
    overrun_amount: float = Field(default=0.0, description="超支金额")


class ValidationResult(BaseModel):
    """
    验证结果

    Requirements: 6.1
    """

    is_valid: bool = Field(..., description="是否有效")
    reason: Optional[str] = Field(None, description="原因")


class ProjectSummary(BaseModel):
    """
    项目总结

    Requirements: 6.5
    """

    project_id: str = Field(..., description="项目 ID")
    total_cost: Money = Field(..., description="总成本")
    budget_total: Money = Field(..., description="预算总额")
    budget_compliance: BudgetCompliance = Field(..., description="预算合规性")
    shots_count: int = Field(..., description="镜头数量")
    duration: float = Field(..., description="视频时长（秒）")
    quality_tier: str = Field(..., description="质量档位")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: datetime = Field(..., description="完成时间")


class EventType(str, Enum):
    """事件类型"""

    PROJECT_CREATED = "PROJECT_CREATED"
    BUDGET_ALLOCATED = "BUDGET_ALLOCATED"
    COST_OVERRUN_WARNING = "COST_OVERRUN_WARNING"
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    STRATEGY_UPDATE = "STRATEGY_UPDATE"
    CONSISTENCY_FAILED = "CONSISTENCY_FAILED"
    HUMAN_GATE_TRIGGERED = "HUMAN_GATE_TRIGGERED"
    USER_APPROVED = "USER_APPROVED"
    USER_REVISION_REQUESTED = "USER_REVISION_REQUESTED"
    USER_REJECTED = "USER_REJECTED"
    PROJECT_FINALIZED = "PROJECT_FINALIZED"
    PROJECT_DELIVERED = "PROJECT_DELIVERED"
    IMAGE_GENERATED = "IMAGE_GENERATED"
    VIDEO_GENERATED = "VIDEO_GENERATED"
    MUSIC_COMPOSED = "MUSIC_COMPOSED"
    VOICE_RENDERED = "VOICE_RENDERED"
    ERROR_OCCURRED = "ERROR_OCCURRED"


class Event(BaseModel):
    """事件对象"""

    event_id: str = Field(..., description="事件 ID")
    project_id: str = Field(..., description="项目 ID")
    event_type: EventType = Field(..., description="事件类型")
    actor: str = Field(..., description="发布者")
    payload: Dict[str, Any] = Field(..., description="事件数据")
    causation_id: Optional[str] = Field(None, description="因果关系 ID")
    timestamp: str = Field(..., description="时间戳")
    cost: Optional[Money] = Field(None, description="成本")
    latency_ms: Optional[int] = Field(None, description="延迟（毫秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
