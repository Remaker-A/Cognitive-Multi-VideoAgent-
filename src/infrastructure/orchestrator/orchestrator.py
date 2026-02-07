"""
核心 Orchestrator

任务编排器，整合所有组件。
"""

import logging
import asyncio
from typing import Optional

from ..blackboard.blackboard import SharedBlackboard
from ..event_bus.event_bus import EventBus
from ..event_bus.event import Event, EventType
from .task_queue import PriorityTaskQueue
from .event_mapper import EventMapper
from .scheduler import TaskScheduler
from .state_machine import TaskStateMachine
from .budget_checker import BudgetChecker
from .approval_manager import ApprovalManager
from .config import OrchestratorConfig


logger = logging.getLogger(__name__)


class Orchestrator:
    """
    任务编排器
    
    Features:
    - 事件处理
    - 任务创建和调度
    - 预算控制
    - 用户审批管理
    """
    
    def __init__(
        self,
        blackboard: SharedBlackboard,
        event_bus: EventBus,
        config: Optional[OrchestratorConfig] = None
    ):
        """
        初始化 Orchestrator
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            config: 配置对象
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.config = config or OrchestratorConfig()
        
        # 初始化组件
        self.task_queue = PriorityTaskQueue(
            blackboard.redis,
            self.config.task_queue_key
        )
        self.event_mapper = EventMapper()
        self.state_machine = TaskStateMachine()
        self.scheduler = TaskScheduler(blackboard, self.state_machine)
        self.budget_checker = BudgetChecker(blackboard)
        self.approval_manager = ApprovalManager(blackboard, event_bus)
        
        # 运行状态
        self._running = False
        self._event_loop_task = None
        self._scheduler_task = None
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件并创建任务
        
        Args:
            event: 事件对象
        """
        try:
            logger.info(f"Handling event: {event.type.value} for project {event.project_id}")
            
            # 检查项目是否暂停
            if self.approval_manager.is_paused(event.project_id):
                logger.info(f"Project {event.project_id} is paused, skipping event")
                return
            
            # 检查是否需要审批
            if self.approval_manager.check_approval_required(event):
                await self.approval_manager.request_approval(event)
                return
            
            # 映射事件到任务
            tasks = self.event_mapper.map_event_to_tasks(event)
            
            if not tasks:
                logger.debug(f"No tasks created for event {event.type.value}")
                return
            
            # 处理每个任务
            for task in tasks:
                # TODO: 选择模型
                # task.input['model'] = await self.model_router.select_model(...)
                
                # TODO: 估算成本
                # task.estimated_cost = await self.model_router.estimate_cost(task)
                
                # 检查预算
                if self.config.budget_check_enabled:
                    if not self.budget_checker.check_budget(
                        task.project_id,
                        task.estimated_cost
                    ):
                        logger.warning(
                            f"Insufficient budget for task {task.task_id}, skipping"
                        )
                        continue
                
                # 添加到队列
                self.task_queue.put(task)
                
                # 写入 Blackboard
                # TODO: 实现 create_task 方法
                # self.blackboard.create_task(task.to_dict())
                
                logger.info(
                    f"Created task {task.task_id} ({task.type.value}) "
                    f"for project {task.project_id}"
                )
        
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def dispatch_tasks(self) -> None:
        """调度和分发任务"""
        try:
            # 获取所有待处理任务
            all_tasks = self.task_queue.get_all()
            
            for task in all_tasks:
                # 检查是否可以分发
                if await self.scheduler.can_dispatch(task):
                    # 从队列移除
                    self.task_queue.remove(task.task_id)
                    
                    # 分发任务
                    await self.scheduler.dispatch_task(task)
                
                # 检查超时
                if self.scheduler.check_timeout(task, self.config.task_timeout_seconds):
                    logger.warning(f"Task {task.task_id} timeout, marking as failed")
                    self.state_machine.transition(
                        task,
                        TaskStatus.FAILED,
                        "Task timeout"
                    )
                    self.scheduler.release_lock(task)
        
        except Exception as e:
            logger.error(f"Error dispatching tasks: {e}", exc_info=True)
    
    async def start_event_loop(self) -> None:
        """启动事件处理循环"""
        logger.info("Starting event loop")
        
        # 订阅所有事件类型
        from ..event_bus.subscriber import EventSubscriber
        
        class OrchestratorSubscriber(EventSubscriber):
            def __init__(self, orchestrator):
                super().__init__("Orchestrator")
                self.orchestrator = orchestrator
            
            async def handle_event(self, event: Event):
                await self.orchestrator.handle_event(event)
        
        subscriber = OrchestratorSubscriber(self)
        
        # 订阅所有事件类型
        self.event_bus.subscribe(subscriber, list(EventType))
        
        # 启动消费
        await self.event_bus.start_consuming()
    
    async def start_scheduler(self) -> None:
        """启动任务调度循环"""
        logger.info("Starting task scheduler")
        
        while self._running:
            try:
                await self.dispatch_tasks()
                await asyncio.sleep(self.config.scheduler_interval_seconds)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                await asyncio.sleep(1)
    
    async def start(self) -> None:
        """启动 Orchestrator"""
        if self._running:
            logger.warning("Orchestrator already running")
            return
        
        self._running = True
        
        # 启动事件循环
        self._event_loop_task = asyncio.create_task(self.start_event_loop())
        
        # 启动调度器
        self._scheduler_task = asyncio.create_task(self.start_scheduler())
        
        logger.info("Orchestrator started")
    
    async def stop(self) -> None:
        """停止 Orchestrator"""
        if not self._running:
            return
        
        self._running = False
        
        # 停止事件循环
        if self._event_loop_task:
            await self.event_bus.stop_consuming()
            self._event_loop_task.cancel()
            try:
                await self._event_loop_task
            except asyncio.CancelledError:
                pass
        
        # 停止调度器
        if self._scheduler_task:
            self._scheduler_task.cancel()
            try:
                await self._scheduler_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Orchestrator stopped")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()
