"""
契约模型定义

基于 contracts 目录中的 JSON Schema 定义的 Pydantic 模型，
确保运行时类型安全和数据验证。
"""

from datetime import datetime
from typing import Optional, Dict, Any, List, Literal
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================================
# 枚举类型
# ============================================================================

class EventType(str, Enum):
    """事件类型枚举"""
    PROJECT_CREATED = "PROJECT_CREATED"
    SCENE_WRITTEN = "SCENE_WRITTEN"
    SHOT_PLANNED = "SHOT_PLANNED"
    KEYFRAME_REQUESTED = "KEYFRAME_REQUESTED"
    IMAGE_GENERATED = "IMAGE_GENERATED"
    DNA_BANK_UPDATED = "DNA_BANK_UPDATED"
    PREVIEW_VIDEO_REQUESTED = "PREVIEW_VIDEO_REQUESTED"
    PREVIEW_VIDEO_READY = "PREVIEW_VIDEO_READY"
    QA_REPORT = "QA_REPORT"
    CONSISTENCY_FAILED = "CONSISTENCY_FAILED"
    MUSIC_COMPOSED = "MUSIC_COMPOSED"
    VOICE_RENDERED = "VOICE_RENDERED"
    SHOT_APPROVED = "SHOT_APPROVED"
    FINAL_VIDEO_REQUESTED = "FINAL_VIDEO_REQUESTED"
    FINAL_VIDEO_READY = "FINAL_VIDEO_READY"
    PROJECT_FINALIZED = "PROJECT_FINALIZED"
    ALL_SHOTS_READY = "ALL_SHOTS_READY"
    HUMAN_GATE_TRIGGERED = "HUMAN_GATE_TRIGGERED"
    USER_APPROVAL_REQUIRED = "USER_APPROVAL_REQUIRED"
    USER_APPROVED = "USER_APPROVED"
    USER_REVISION_REQUESTED = "USER_REVISION_REQUESTED"
    USER_REJECTED = "USER_REJECTED"
    BUDGET_ALLOCATED = "BUDGET_ALLOCATED"
    STRATEGY_UPDATE = "STRATEGY_UPDATE"
    FORCE_ABORT = "FORCE_ABORT"
    COST_OVERRUN_WARNING = "COST_OVERRUN_WARNING"
    HUMAN_APPROVAL_REQUEST = "HUMAN_APPROVAL_REQUEST"
    PROMPT_ADJUSTMENT = "PROMPT_ADJUSTMENT"
    AUTO_FIX_REQUEST = "AUTO_FIX_REQUEST"
    USER_EDIT_REQUESTED = "USER_EDIT_REQUESTED"
    ERROR_CORRECTION_REQUESTED = "ERROR_CORRECTION_REQUESTED"
    IMAGE_EDITED = "IMAGE_EDITED"
    USER_ERROR_REPORTED = "USER_ERROR_REPORTED"
    VIDEO_GENERATED = "VIDEO_GENERATED"
    ERROR_DETECTED = "ERROR_DETECTED"
    ERROR_CORRECTED = "ERROR_CORRECTED"


class TaskType(str, Enum):
    """任务类型枚举"""
    WRITE_SCRIPT = "WRITE_SCRIPT"
    REWRITE_SCRIPT = "REWRITE_SCRIPT"
    PLAN_SHOTS = "PLAN_SHOTS"
    GENERATE_KEYFRAME = "GENERATE_KEYFRAME"
    UPSCALE_KEYFRAME = "UPSCALE_KEYFRAME"
    GENERATE_PREVIEW_VIDEO = "GENERATE_PREVIEW_VIDEO"
    GENERATE_FINAL_VIDEO = "GENERATE_FINAL_VIDEO"
    GENERATE_MUSIC = "GENERATE_MUSIC"
    GENERATE_VOICE = "GENERATE_VOICE"
    RUN_VISUAL_QA = "RUN_VISUAL_QA"
    RUN_AUDIO_QA = "RUN_AUDIO_QA"
    RUN_CROSS_MODAL_QA = "RUN_CROSS_MODAL_QA"
    PROMPT_TUNING = "PROMPT_TUNING"
    MODEL_SWAP_RETRY = "MODEL_SWAP_RETRY"
    EXTRACT_FEATURES = "EXTRACT_FEATURES"
    UPDATE_DNA_BANK = "UPDATE_DNA_BANK"
    ADJUST_PROMPTS = "ADJUST_PROMPTS"
    ASSEMBLE_FINAL = "ASSEMBLE_FINAL"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    GENERATE_STATIC_WITH_MOTION = "GENERATE_STATIC_WITH_MOTION"
    USE_STOCK_MUSIC = "USE_STOCK_MUSIC"
    USE_TTS_FALLBACK = "USE_TTS_FALLBACK"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProjectStatus(str, Enum):
    """项目状态枚举"""
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


# ============================================================================
# 共享模型
# ============================================================================

class Money(BaseModel):
    """金额模型"""
    amount: float = Field(..., ge=0)
    currency: str = Field(..., min_length=3, max_length=3)


class EventMetadata(BaseModel):
    """事件元数据"""
    cost: Optional[Money] = None
    latency_ms: Optional[int] = Field(None, ge=0)
    retry_count: Optional[int] = Field(None, ge=0)


# ============================================================================
# 事件模型
# ============================================================================

class Event(BaseModel):
    """事件模型"""
    event_id: str = Field(..., min_length=1)
    project_id: str = Field(..., min_length=1)
    type: EventType
    actor: str = Field(..., min_length=1, description="Agent name / UI / system component")
    causation_id: Optional[str] = Field(None, description="Previous event_id in the causal chain")
    timestamp: datetime
    payload: Dict[str, Any] = Field(..., description="Event-specific payload")
    blackboard_pointer: Optional[str] = Field(None, description="JSON pointer-like path in Blackboard")
    metadata: EventMetadata
    
    class Config:
        use_enum_values = True


# ============================================================================
# 任务模型
# ============================================================================

class Task(BaseModel):
    """任务模型"""
    task_id: str = Field(..., min_length=1)
    project_id: Optional[str] = Field(None, min_length=1)
    type: TaskType
    status: TaskStatus
    assigned_to: str = Field(..., min_length=1)
    priority: int = Field(..., ge=1, le=5)
    dependencies: List[str] = Field(default_factory=list)
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    retry_count: int = Field(0, ge=0)
    max_retries: int = Field(3, ge=0)
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_cost: Money
    actual_cost: Optional[Money] = None
    causation_event_id: Optional[str] = None
    requires_lock: bool = False
    lock_key: Optional[str] = Field(None, description="e.g. global_style | dna_bank | shots/S01")
    last_error: Optional[str] = None
    
    class Config:
        use_enum_values = True


# ============================================================================
# Blackboard RPC 模型
# ============================================================================

class BlackboardRequest(BaseModel):
    """Blackboard RPC 请求"""
    id: str = Field(..., min_length=1)
    method: str = Field(..., min_length=1)
    params: Dict[str, Any]


class BlackboardResponse(BaseModel):
    """Blackboard RPC 成功响应"""
    id: str = Field(..., min_length=1)
    ok: Literal[True] = True
    result: Dict[str, Any]


class BlackboardErrorDetail(BaseModel):
    """Blackboard 错误详情"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class BlackboardErrorResponse(BaseModel):
    """Blackboard RPC 错误响应"""
    id: str = Field(..., min_length=1)
    ok: Literal[False] = False
    error: BlackboardErrorDetail


# ============================================================================
# 辅助函数
# ============================================================================

def create_event(
    event_id: str,
    project_id: str,
    event_type: EventType,
    actor: str,
    payload: Dict[str, Any],
    causation_id: Optional[str] = None,
    blackboard_pointer: Optional[str] = None,
    cost: Optional[Money] = None,
    latency_ms: Optional[int] = None,
    retry_count: Optional[int] = None,
) -> Event:
    """创建符合契约的事件对象"""
    return Event(
        event_id=event_id,
        project_id=project_id,
        type=event_type,
        actor=actor,
        causation_id=causation_id,
        timestamp=datetime.now(),
        payload=payload,
        blackboard_pointer=blackboard_pointer,
        metadata=EventMetadata(
            cost=cost,
            latency_ms=latency_ms,
            retry_count=retry_count or 0,
        ),
    )


def create_task(
    task_id: str,
    task_type: TaskType,
    assigned_to: str,
    input_data: Dict[str, Any],
    priority: int = 3,
    project_id: Optional[str] = None,
    dependencies: Optional[List[str]] = None,
    estimated_cost: Optional[Money] = None,
    causation_event_id: Optional[str] = None,
    requires_lock: bool = False,
    lock_key: Optional[str] = None,
) -> Task:
    """创建符合契约的任务对象"""
    return Task(
        task_id=task_id,
        project_id=project_id,
        type=task_type,
        status=TaskStatus.PENDING,
        assigned_to=assigned_to,
        priority=priority,
        dependencies=dependencies or [],
        input=input_data,
        retry_count=0,
        max_retries=3,
        created_at=datetime.now(),
        estimated_cost=estimated_cost or Money(amount=0.0, currency="USD"),
        causation_event_id=causation_event_id,
        requires_lock=requires_lock,
        lock_key=lock_key,
    )


def create_blackboard_request(
    request_id: str,
    method: str,
    params: Dict[str, Any],
) -> BlackboardRequest:
    """创建符合契约的 Blackboard RPC 请求"""
    return BlackboardRequest(
        id=request_id,
        method=method,
        params=params,
    )


def create_blackboard_response(
    request_id: str,
    result: Dict[str, Any],
) -> BlackboardResponse:
    """创建符合契约的 Blackboard RPC 响应"""
    return BlackboardResponse(
        id=request_id,
        ok=True,
        result=result,
    )


def create_blackboard_error_response(
    request_id: str,
    error_code: str,
    error_message: str,
    error_details: Optional[Dict[str, Any]] = None,
) -> BlackboardErrorResponse:
    """创建符合契约的 Blackboard RPC 错误响应"""
    return BlackboardErrorResponse(
        id=request_id,
        ok=False,
        error=BlackboardErrorDetail(
            code=error_code,
            message=error_message,
            details=error_details,
        ),
    )
