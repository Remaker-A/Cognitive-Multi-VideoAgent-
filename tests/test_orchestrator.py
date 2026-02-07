"""
Orchestrator 单元测试

测试任务调度、状态机、预算检查等核心功能。
"""

import pytest
import asyncio
from datetime import datetime

from src.infrastructure.orchestrator import (
    Task, TaskType, TaskStatus, TaskPriority,
    PriorityTaskQueue, TaskStateMachine, EventMapper
)
from src.infrastructure.event_bus import Event, EventType


class TestTask:
    """Task 数据模型测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            assigned_to="ImageGenAgent",
            priority=TaskPriority.HIGH
        )
        
        assert task.project_id == "PROJ-001"
        assert task.type == TaskType.GENERATE_KEYFRAME
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.HIGH
    
    def test_task_serialization(self):
        """测试任务序列化"""
        task = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            assigned_to="ImageGenAgent"
        )
        
        # 转换为字典
        task_dict = task.to_dict()
        assert task_dict["project_id"] == "PROJ-001"
        assert task_dict["type"] == "GENERATE_KEYFRAME"
        
        # 从字典创建
        task2 = Task.from_dict(task_dict)
        assert task2.project_id == task.project_id
        assert task2.type == task.type
    
    def test_task_retry(self):
        """测试任务重试"""
        task = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            max_retries=3
        )
        
        assert task.can_retry() is True
        
        task.retry_count = 3
        assert task.can_retry() is False


class TestTaskStateMachine:
    """任务状态机测试"""
    
    def test_valid_transitions(self):
        """测试有效的状态转换"""
        sm = TaskStateMachine()
        
        # PENDING -> READY
        assert sm.can_transition(TaskStatus.PENDING, TaskStatus.READY) is True
        
        # READY -> RUNNING
        assert sm.can_transition(TaskStatus.READY, TaskStatus.RUNNING) is True
        
        # RUNNING -> COMPLETED
        assert sm.can_transition(TaskStatus.RUNNING, TaskStatus.COMPLETED) is True
        
        # FAILED -> PENDING (重试)
        assert sm.can_transition(TaskStatus.FAILED, TaskStatus.PENDING) is True
    
    def test_invalid_transitions(self):
        """测试无效的状态转换"""
        sm = TaskStateMachine()
        
        # PENDING -> COMPLETED (不允许)
        assert sm.can_transition(TaskStatus.PENDING, TaskStatus.COMPLETED) is False
        
        # COMPLETED -> RUNNING (不允许)
        assert sm.can_transition(TaskStatus.COMPLETED, TaskStatus.RUNNING) is False
    
    def test_transition_with_task(self):
        """测试任务状态转换"""
        sm = TaskStateMachine()
        task = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME
        )
        
        # PENDING -> READY
        result = sm.transition(task, TaskStatus.READY)
        assert result is True
        assert task.status == TaskStatus.READY
        
        # READY -> RUNNING
        result = sm.transition(task, TaskStatus.RUNNING)
        assert result is True
        assert task.status == TaskStatus.RUNNING
        assert task.started_at is not None


class TestEventMapper:
    """事件映射器测试"""
    
    def test_map_project_created(self):
        """测试 PROJECT_CREATED 事件映射"""
        mapper = EventMapper()
        
        event = Event(
            project_id="PROJ-001",
            type=EventType.PROJECT_CREATED,
            actor="RequirementParser",
            payload={"title": "Test Project"}
        )
        
        tasks = mapper.map_event_to_tasks(event)
        
        assert len(tasks) == 1
        assert tasks[0].type == TaskType.WRITE_SCRIPT
        assert tasks[0].assigned_to == "ScriptWriter"
    
    def test_map_shot_planned(self):
        """测试 SHOT_PLANNED 事件映射"""
        mapper = EventMapper()
        
        event = Event(
            project_id="PROJ-001",
            type=EventType.SHOT_PLANNED,
            actor="ShotDirector",
            payload={"shot_id": "S01"}
        )
        
        tasks = mapper.map_event_to_tasks(event)
        
        assert len(tasks) == 1
        assert tasks[0].type == TaskType.GENERATE_KEYFRAME
        assert tasks[0].assigned_to == "ImageGenAgent"
    
    def test_map_image_generated(self):
        """测试 IMAGE_GENERATED 事件映射（多任务）"""
        mapper = EventMapper()
        
        event = Event(
            project_id="PROJ-001",
            type=EventType.IMAGE_GENERATED,
            actor="ImageGenAgent",
            payload={"shot_id": "S01", "artifact_url": "s3://..."}
        )
        
        tasks = mapper.map_event_to_tasks(event)
        
        # 应该生成两个任务
        assert len(tasks) == 2
        task_types = [t.type for t in tasks]
        assert TaskType.EXTRACT_FEATURES in task_types
        assert TaskType.RUN_VISUAL_QA in task_types


@pytest.mark.asyncio
class TestPriorityTaskQueue:
    """优先级任务队列测试"""
    
    async def test_queue_put_get(self, redis_client):
        """测试任务入队和出队"""
        queue = PriorityTaskQueue(redis_client, "test_queue")
        queue.clear()
        
        task = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            priority=5
        )
        
        # 入队
        result = queue.put(task)
        assert result is True
        
        # 出队
        retrieved_task = queue.get()
        assert retrieved_task is not None
        assert retrieved_task.task_id == task.task_id
        
        queue.clear()
    
    async def test_queue_priority_ordering(self, redis_client):
        """测试优先级排序"""
        queue = PriorityTaskQueue(redis_client, "test_queue")
        queue.clear()
        
        # 添加不同优先级的任务
        task_low = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            priority=3
        )
        task_high = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            priority=10
        )
        task_medium = Task(
            project_id="PROJ-001",
            type=TaskType.GENERATE_KEYFRAME,
            priority=5
        )
        
        queue.put(task_low)
        queue.put(task_high)
        queue.put(task_medium)
        
        # 获取任务，应该按优先级排序
        first = queue.get()
        assert first.priority == 10  # 最高优先级
        
        second = queue.get()
        assert second.priority == 5
        
        third = queue.get()
        assert third.priority == 3
        
        queue.clear()
    
    async def test_queue_size(self, redis_client):
        """测试队列大小"""
        queue = PriorityTaskQueue(redis_client, "test_queue")
        queue.clear()
        
        assert queue.size() == 0
        assert queue.is_empty() is True
        
        task = Task(project_id="PROJ-001", type=TaskType.GENERATE_KEYFRAME)
        queue.put(task)
        
        assert queue.size() == 1
        assert queue.is_empty() is False
        
        queue.clear()


# Pytest fixtures
@pytest.fixture
def redis_client():
    """Redis 客户端 fixture"""
    import redis
    client = redis.Redis(host='localhost', port=6379, db=15)  # 使用测试数据库
    yield client
    # 清理
    client.flushdb()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
