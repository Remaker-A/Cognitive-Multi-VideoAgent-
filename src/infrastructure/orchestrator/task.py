"""
Task 数据模型

定义任务的数据结构、类型、状态和优先级。
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class TaskType(str, Enum):
    """任务类型枚举"""
    # 剧本相关
    WRITE_SCRIPT = "WRITE_SCRIPT"
    REVISE_SCRIPT = "REVISE_SCRIPT"
    
    # 分镜相关
    PLAN_SHOTS = "PLAN_SHOTS"
    REVISE_SHOTS = "REVISE_SHOTS"
    
    # 图像生成
    GENERATE_KEYFRAME = "GENERATE_KEYFRAME"
    GENERATE_KEYFRAME_START = "GENERATE_KEYFRAME_START"
    GENERATE_KEYFRAME_MID = "GENERATE_KEYFRAME_MID"
    GENERATE_KEYFRAME_END = "GENERATE_KEYFRAME_END"
    
    # 图像编辑
    EDIT_IMAGE = "EDIT_IMAGE"
    INPAINT_IMAGE = "INPAINT_IMAGE"
    
    # DNA 和特征
    EXTRACT_FEATURES = "EXTRACT_FEATURES"
    UPDATE_DNA_BANK = "UPDATE_DNA_BANK"
    
    # 提示词
    ADJUST_PROMPTS = "ADJUST_PROMPTS"
    OPTIMIZE_PROMPTS = "OPTIMIZE_PROMPTS"
    
    # 视频生成
    GENERATE_PREVIEW_VIDEO = "GENERATE_PREVIEW_VIDEO"
    GENERATE_FINAL_VIDEO = "GENERATE_FINAL_VIDEO"
    
    # QA 检测
    RUN_VISUAL_QA = "RUN_VISUAL_QA"
    RUN_VIDEO_QA = "RUN_VIDEO_QA"
    CHECK_CONSISTENCY = "CHECK_CONSISTENCY"
    
    # 音频
    COMPOSE_MUSIC = "COMPOSE_MUSIC"
    RENDER_VOICE = "RENDER_VOICE"
    
    # 编辑
    ASSEMBLE_FINAL = "ASSEMBLE_FINAL"
    ADD_EFFECTS = "ADD_EFFECTS"
    
    # 审批
    REQUEST_APPROVAL = "REQUEST_APPROVAL"
    HANDLE_REVISION = "HANDLE_REVISION"


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "PENDING"              # 等待执行
    READY = "READY"                  # 依赖满足，可执行
    RUNNING = "RUNNING"              # 执行中
    COMPLETED = "COMPLETED"          # 完成
    FAILED = "FAILED"                # 失败
    CANCELLED = "CANCELLED"          # 取消
    WAITING_APPROVAL = "WAITING_APPROVAL"  # 等待审批


class TaskPriority(int, Enum):
    """任务优先级枚举"""
    CRITICAL = 10    # 关键任务
    HIGH = 8         # 高优先级
    NORMAL = 5       # 普通优先级
    LOW = 3          # 低优先级
    BACKGROUND = 1   # 后台任务


@dataclass
class Task:
    """
    任务数据模型
    
    表示系统中的一个可执行任务，包含输入输出、依赖关系、
    预算信息和执行状态等。
    """
    # 基础信息
    task_id: str = field(default_factory=lambda: f"TASK-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}")
    project_id: str = ""
    type: TaskType = TaskType.WRITE_SCRIPT
    assigned_to: str = ""  # Agent 名称
    status: TaskStatus = TaskStatus.PENDING
    priority: int = TaskPriority.NORMAL
    
    # 输入输出
    input: Dict[str, Any] = field(default_factory=dict)
    output: Optional[Dict[str, Any]] = None
    
    # 依赖和锁
    dependencies: List[str] = field(default_factory=list)  # 依赖的任务 ID
    requires_lock: bool = False
    lock_key: Optional[str] = None
    
    # 预算和成本
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    # 链路追踪
    causation_event_id: str = ""
    
    # 重试机制
    retry_count: int = 0
    max_retries: int = 3
    
    # 错误信息
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "task_id": self.task_id,
            "project_id": self.project_id,
            "type": self.type.value if isinstance(self.type, TaskType) else self.type,
            "assigned_to": self.assigned_to,
            "status": self.status.value if isinstance(self.status, TaskStatus) else self.status,
            "priority": self.priority,
            "input": self.input,
            "output": self.output,
            "dependencies": self.dependencies,
            "requires_lock": self.requires_lock,
            "lock_key": self.lock_key,
            "estimated_cost": self.estimated_cost,
            "actual_cost": self.actual_cost,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "causation_event_id": self.causation_event_id,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "error_message": self.error_message
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Task':
        """从字典创建"""
        task_type = TaskType(data["type"]) if isinstance(data["type"], str) else data["type"]
        task_status = TaskStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        
        return cls(
            task_id=data.get("task_id", ""),
            project_id=data.get("project_id", ""),
            type=task_type,
            assigned_to=data.get("assigned_to", ""),
            status=task_status,
            priority=data.get("priority", TaskPriority.NORMAL),
            input=data.get("input", {}),
            output=data.get("output"),
            dependencies=data.get("dependencies", []),
            requires_lock=data.get("requires_lock", False),
            lock_key=data.get("lock_key"),
            estimated_cost=data.get("estimated_cost", 0.0),
            actual_cost=data.get("actual_cost", 0.0),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            causation_event_id=data.get("causation_event_id", ""),
            retry_count=data.get("retry_count", 0),
            max_retries=data.get("max_retries", 3),
            error_message=data.get("error_message")
        )
    
    def can_retry(self) -> bool:
        """是否可以重试"""
        return self.retry_count < self.max_retries
    
    def is_terminal_status(self) -> bool:
        """是否为终止状态"""
        return self.status in [
            TaskStatus.COMPLETED,
            TaskStatus.CANCELLED,
            TaskStatus.FAILED
        ]
    
    def __repr__(self) -> str:
        return f"Task(id={self.task_id}, type={self.type.value}, status={self.status.value}, priority={self.priority})"
