"""
任务调度器

负责任务的依赖检查、锁获取和分发。
"""

import logging
from typing import List, Optional
import asyncio

from ..blackboard.blackboard import SharedBlackboard
from ..blackboard.lock import DistributedLock
from .task import Task, TaskStatus
from .state_machine import TaskStateMachine


logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    任务调度器
    
    Features:
    - 依赖检查
    - 分布式锁管理
    - 任务分发
    - 超时检测
    """
    
    def __init__(self, blackboard: SharedBlackboard, state_machine: TaskStateMachine):
        """
        初始化调度器
        
        Args:
            blackboard: Shared Blackboard 实例
            state_machine: 任务状态机
        """
        self.blackboard = blackboard
        self.state_machine = state_machine
        self.active_locks = {}  # task_id -> DistributedLock
    
    def check_dependencies(self, task: Task) -> bool:
        """
        检查任务依赖是否满足
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 依赖是否满足
        """
        if not task.dependencies:
            return True
        
        try:
            for dep_task_id in task.dependencies:
                # 从 Blackboard 获取依赖任务
                dep_task_data = self.blackboard.get_task(task.project_id, dep_task_id)
                
                if not dep_task_data:
                    logger.warning(f"Dependency task {dep_task_id} not found")
                    return False
                
                dep_status = dep_task_data.get('status')
                
                # 依赖任务必须已完成
                if dep_status != TaskStatus.COMPLETED.value:
                    logger.debug(
                        f"Task {task.task_id} waiting for dependency {dep_task_id} "
                        f"(status: {dep_status})"
                    )
                    return False
            
            logger.debug(f"All dependencies satisfied for task {task.task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to check dependencies: {e}")
            return False
    
    async def acquire_lock(self, task: Task) -> bool:
        """
        获取任务所需的锁
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否成功获取锁
        """
        if not task.requires_lock or not task.lock_key:
            return True
        
        try:
            lock = DistributedLock(
                self.blackboard.redis,
                task.lock_key,
                timeout=300  # 5 分钟超时
            )
            
            # 非阻塞获取锁
            if lock.acquire(blocking=False):
                self.active_locks[task.task_id] = lock
                logger.info(f"Acquired lock {task.lock_key} for task {task.task_id}")
                return True
            else:
                logger.debug(f"Failed to acquire lock {task.lock_key} for task {task.task_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error acquiring lock: {e}")
            return False
    
    def release_lock(self, task: Task) -> None:
        """
        释放任务的锁
        
        Args:
            task: 任务对象
        """
        if task.task_id in self.active_locks:
            try:
                lock = self.active_locks[task.task_id]
                lock.release()
                del self.active_locks[task.task_id]
                logger.info(f"Released lock for task {task.task_id}")
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")
    
    async def dispatch_task(self, task: Task) -> bool:
        """
        分发任务给 Agent
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否成功分发
        """
        try:
            # 转换状态为 RUNNING
            if not self.state_machine.transition(task, TaskStatus.RUNNING):
                logger.error(f"Failed to transition task {task.task_id} to RUNNING")
                return False
            
            # 更新 Blackboard
            self.blackboard.update_task(task.project_id, task.task_id, task.to_dict())
            
            # TODO: 实际分发给 Agent
            # agent = self.get_agent(task.assigned_to)
            # await agent.execute_task(task)
            
            logger.info(f"Dispatched task {task.task_id} to {task.assigned_to}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to dispatch task: {e}")
            return False
    
    def check_timeout(self, task: Task, timeout_seconds: int = 300) -> bool:
        """
        检查任务是否超时
        
        Args:
            task: 任务对象
            timeout_seconds: 超时时间（秒）
            
        Returns:
            bool: 是否超时
        """
        if task.status != TaskStatus.RUNNING or not task.started_at:
            return False
        
        from datetime import datetime, timedelta
        
        started_at = datetime.fromisoformat(task.started_at)
        now = datetime.utcnow()
        
        elapsed = (now - started_at).total_seconds()
        
        if elapsed > timeout_seconds:
            logger.warning(
                f"Task {task.task_id} timeout: {elapsed:.0f}s > {timeout_seconds}s"
            )
            return True
        
        return False
    
    async def can_dispatch(self, task: Task) -> bool:
        """
        检查任务是否可以分发
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否可以分发
        """
        # 检查状态
        if task.status != TaskStatus.READY:
            return False
        
        # 检查依赖
        if not self.check_dependencies(task):
            return False
        
        # 获取锁
        if not await self.acquire_lock(task):
            return False
        
        return True
