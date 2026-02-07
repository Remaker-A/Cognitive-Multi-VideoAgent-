"""
事件到任务映射器

负责将事件映射为具体的任务。
"""

import logging
from typing import List, Dict, Any

from ..event_bus.event import Event, EventType
from .task import Task, TaskType, TaskPriority


logger = logging.getLogger(__name__)


# 事件到任务的映射表
EVENT_TASK_MAPPING = {
    EventType.PROJECT_CREATED: [
        {"type": TaskType.WRITE_SCRIPT, "agent": "ScriptWriter", "priority": TaskPriority.CRITICAL}
    ],
    EventType.SCENE_WRITTEN: [
        {"type": TaskType.PLAN_SHOTS, "agent": "ShotDirector", "priority": TaskPriority.HIGH}
    ],
    EventType.SHOT_PLANNED: [
        {"type": TaskType.GENERATE_KEYFRAME, "agent": "ImageGenAgent", "priority": TaskPriority.HIGH}
    ],
    EventType.IMAGE_GENERATED: [
        {"type": TaskType.EXTRACT_FEATURES, "agent": "ArtDirector", "priority": TaskPriority.NORMAL},
        {"type": TaskType.RUN_VISUAL_QA, "agent": "ConsistencyGuardian", "priority": TaskPriority.NORMAL}
    ],
    EventType.DNA_BANK_UPDATED: [
        {"type": TaskType.ADJUST_PROMPTS, "agent": "PromptEngineer", "priority": TaskPriority.NORMAL}
    ],
    EventType.KEYFRAME_REQUESTED: [
        {"type": TaskType.GENERATE_KEYFRAME, "agent": "ImageGenAgent", "priority": TaskPriority.HIGH}
    ],
    EventType.PREVIEW_VIDEO_REQUESTED: [
        {"type": TaskType.GENERATE_PREVIEW_VIDEO, "agent": "VideoGenAgent", "priority": TaskPriority.HIGH}
    ],
    EventType.PREVIEW_VIDEO_READY: [
        {"type": TaskType.RUN_VIDEO_QA, "agent": "ConsistencyGuardian", "priority": TaskPriority.NORMAL}
    ],
    EventType.SHOT_APPROVED: [
        {"type": TaskType.GENERATE_FINAL_VIDEO, "agent": "VideoGenAgent", "priority": TaskPriority.HIGH}
    ],
    EventType.FINAL_VIDEO_REQUESTED: [
        {"type": TaskType.GENERATE_FINAL_VIDEO, "agent": "VideoGenAgent", "priority": TaskPriority.CRITICAL}
    ],
    EventType.CONSISTENCY_FAILED: [
        {"type": TaskType.ADJUST_PROMPTS, "agent": "PromptEngineer", "priority": TaskPriority.HIGH}
    ],
    EventType.IMAGE_EDIT_REQUESTED: [
        {"type": TaskType.EDIT_IMAGE, "agent": "ImageGenAgent", "priority": TaskPriority.HIGH}
    ],
}


class EventMapper:
    """
    事件到任务映射器
    
    负责将事件转换为可执行的任务。
    """
    
    def __init__(self):
        """初始化映射器"""
        self.mapping = EVENT_TASK_MAPPING
    
    def map_event_to_tasks(self, event: Event) -> List[Task]:
        """
        将事件映射为任务列表
        
        Args:
            event: 事件对象
            
        Returns:
            List[Task]: 任务列表
        """
        # 获取映射模板
        task_templates = self.mapping.get(event.type, [])
        
        if not task_templates:
            logger.debug(f"No task mapping for event type: {event.type.value}")
            return []
        
        tasks = []
        for template in task_templates:
            # 创建任务
            task = Task(
                project_id=event.project_id,
                type=template["type"],
                assigned_to=template["agent"],
                priority=template["priority"],
                input=self.extract_task_input(event),
                causation_event_id=event.event_id
            )
            
            # 设置锁（如果需要）
            if self._requires_lock(task.type):
                task.requires_lock = True
                task.lock_key = self._get_lock_key(task)
            
            tasks.append(task)
            logger.info(f"Mapped event {event.type.value} to task {task.type.value}")
        
        return tasks
    
    def extract_task_input(self, event: Event) -> Dict[str, Any]:
        """
        从事件中提取任务输入
        
        Args:
            event: 事件对象
            
        Returns:
            Dict: 任务输入数据
        """
        # 基础输入
        task_input = {
            "project_id": event.project_id,
            "event_type": event.type.value,
            "event_id": event.event_id,
            "payload": event.payload
        }
        
        # 根据事件类型提取特定数据
        if event.type == EventType.SHOT_PLANNED:
            task_input["shot_id"] = event.payload.get("shot_id")
            task_input["shot_spec"] = event.payload.get("shot_spec")
        
        elif event.type == EventType.IMAGE_GENERATED:
            task_input["shot_id"] = event.payload.get("shot_id")
            task_input["artifact_url"] = event.payload.get("artifact_url")
            task_input["keyframe_type"] = event.payload.get("keyframe_type")
        
        elif event.type == EventType.CONSISTENCY_FAILED:
            task_input["shot_id"] = event.payload.get("shot_id")
            task_input["failure_reason"] = event.payload.get("reason")
            task_input["qa_report"] = event.payload.get("qa_report")
        
        return task_input
    
    def _requires_lock(self, task_type: TaskType) -> bool:
        """
        判断任务是否需要锁
        
        Args:
            task_type: 任务类型
            
        Returns:
            bool: 是否需要锁
        """
        # 需要锁的任务类型
        lock_required_tasks = [
            TaskType.UPDATE_DNA_BANK,
            TaskType.ADJUST_PROMPTS,
            TaskType.PLAN_SHOTS,
        ]
        
        return task_type in lock_required_tasks
    
    def _get_lock_key(self, task: Task) -> str:
        """
        获取锁的键名
        
        Args:
            task: 任务对象
            
        Returns:
            str: 锁键名
        """
        if task.type == TaskType.UPDATE_DNA_BANK:
            character_id = task.input.get("character_id", "unknown")
            return f"project:{task.project_id}:dna_bank:{character_id}"
        
        elif task.type == TaskType.ADJUST_PROMPTS:
            return f"project:{task.project_id}:prompts"
        
        elif task.type == TaskType.PLAN_SHOTS:
            return f"project:{task.project_id}:shots"
        
        return f"project:{task.project_id}:task:{task.task_id}"
    
    def add_custom_mapping(
        self,
        event_type: EventType,
        task_type: TaskType,
        agent: str,
        priority: int = TaskPriority.NORMAL
    ) -> None:
        """
        添加自定义映射
        
        Args:
            event_type: 事件类型
            task_type: 任务类型
            agent: 负责的 Agent
            priority: 优先级
        """
        if event_type not in self.mapping:
            self.mapping[event_type] = []
        
        self.mapping[event_type].append({
            "type": task_type,
            "agent": agent,
            "priority": priority
        })
        
        logger.info(f"Added custom mapping: {event_type.value} -> {task_type.value}")
