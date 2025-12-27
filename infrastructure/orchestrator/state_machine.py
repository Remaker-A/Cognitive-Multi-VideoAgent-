"""
任务状态机

管理任务状态转换和验证。
"""

import logging
from typing import Optional

from .task import Task, TaskStatus


logger = logging.getLogger(__name__)


# 允许的状态转换
ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.READY, TaskStatus.CANCELLED],
    TaskStatus.READY: [TaskStatus.RUNNING, TaskStatus.WAITING_APPROVAL, TaskStatus.CANCELLED],
    TaskStatus.RUNNING: [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED],
    TaskStatus.FAILED: [TaskStatus.PENDING, TaskStatus.CANCELLED],  # 允许重试
    TaskStatus.WAITING_APPROVAL: [TaskStatus.READY, TaskStatus.CANCELLED],
    TaskStatus.COMPLETED: [],  # 终止状态
    TaskStatus.CANCELLED: [],  # 终止状态
}


class TaskStateMachine:
    """
    任务状态机
    
    管理任务状态转换，确保状态转换的合法性。
    """
    
    def __init__(self):
        """初始化状态机"""
        self.transitions = ALLOWED_TRANSITIONS
    
    def can_transition(self, current: TaskStatus, target: TaskStatus) -> bool:
        """
        检查是否可以转换到目标状态
        
        Args:
            current: 当前状态
            target: 目标状态
            
        Returns:
            bool: 是否可以转换
        """
        allowed = self.transitions.get(current, [])
        return target in allowed
    
    def transition(self, task: Task, new_status: TaskStatus, error_message: Optional[str] = None) -> bool:
        """
        转换任务状态
        
        Args:
            task: 任务对象
            new_status: 新状态
            error_message: 错误信息（如果失败）
            
        Returns:
            bool: 是否成功转换
        """
        if not self.can_transition(task.status, new_status):
            logger.warning(
                f"Invalid state transition for task {task.task_id}: "
                f"{task.status.value} -> {new_status.value}"
            )
            return False
        
        old_status = task.status
        task.status = new_status
        
        # 设置错误信息
        if error_message:
            task.error_message = error_message
        
        # 触发状态变更回调
        self.on_state_change(task, old_status, new_status)
        
        logger.info(
            f"Task {task.task_id} transitioned: {old_status.value} -> {new_status.value}"
        )
        
        return True
    
    def on_state_change(self, task: Task, old_status: TaskStatus, new_status: TaskStatus) -> None:
        """
        状态变更回调
        
        Args:
            task: 任务对象
            old_status: 旧状态
            new_status: 新状态
        """
        from datetime import datetime
        
        # 更新时间戳
        if new_status == TaskStatus.RUNNING and not task.started_at:
            task.started_at = datetime.utcnow().isoformat()
        
        elif new_status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            if not task.completed_at:
                task.completed_at = datetime.utcnow().isoformat()
        
        # 重试逻辑
        if new_status == TaskStatus.FAILED and task.can_retry():
            logger.info(f"Task {task.task_id} can be retried ({task.retry_count}/{task.max_retries})")
        
        # 记录状态变更
        logger.debug(f"Task {task.task_id} state changed: {old_status.value} -> {new_status.value}")
    
    def is_terminal(self, status: TaskStatus) -> bool:
        """
        检查是否为终止状态
        
        Args:
            status: 任务状态
            
        Returns:
            bool: 是否为终止状态
        """
        return status in [TaskStatus.COMPLETED, TaskStatus.CANCELLED]
    
    def get_next_states(self, current: TaskStatus) -> list:
        """
        获取当前状态可以转换到的状态列表
        
        Args:
            current: 当前状态
            
        Returns:
            list: 可转换的状态列表
        """
        return self.transitions.get(current, [])
