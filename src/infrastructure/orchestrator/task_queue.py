"""
优先级任务队列

基于 Redis Sorted Set 实现的持久化优先级队列。
"""

import json
import logging
from typing import List, Optional
import redis

from .task import Task, TaskStatus


logger = logging.getLogger(__name__)


class PriorityTaskQueue:
    """
    优先级任务队列
    
    Features:
    - 基于 Redis Sorted Set 的持久化队列
    - 优先级排序（高优先级先执行）
    - 任务去重
    - 批量操作
    """
    
    def __init__(self, redis_client: redis.Redis, queue_key: str = "task_queue"):
        """
        初始化任务队列
        
        Args:
            redis_client: Redis 客户端
            queue_key: Redis 队列键名
        """
        self.redis = redis_client
        self.queue_key = queue_key
    
    def put(self, task: Task) -> bool:
        """
        添加任务到队列
        
        Args:
            task: 任务对象
            
        Returns:
            bool: 是否成功添加
        """
        try:
            # 计算 score: priority * 1000000 + timestamp
            # 这样可以保证高优先级任务先执行，同优先级按时间排序
            import time
            score = task.priority * 1000000 + int(time.time())
            
            # 序列化任务
            task_data = json.dumps(task.to_dict())
            
            # 添加到 Sorted Set
            self.redis.zadd(
                self.queue_key,
                {task_data: score}
            )
            
            logger.debug(f"Added task {task.task_id} to queue with priority {task.priority}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add task to queue: {e}")
            return False
    
    def get(self) -> Optional[Task]:
        """
        获取并移除最高优先级任务
        
        Returns:
            Task: 任务对象，如果队列为空则返回 None
        """
        try:
            # 获取最高优先级的任务（score 最大）
            items = self.redis.zrevrange(self.queue_key, 0, 0)
            
            if not items:
                return None
            
            task_data = items[0]
            
            # 从队列移除
            self.redis.zrem(self.queue_key, task_data)
            
            # 反序列化
            task_dict = json.loads(task_data)
            task = Task.from_dict(task_dict)
            
            logger.debug(f"Got task {task.task_id} from queue")
            return task
            
        except Exception as e:
            logger.error(f"Failed to get task from queue: {e}")
            return None
    
    def peek(self) -> Optional[Task]:
        """
        查看最高优先级任务（不移除）
        
        Returns:
            Task: 任务对象，如果队列为空则返回 None
        """
        try:
            items = self.redis.zrevrange(self.queue_key, 0, 0)
            
            if not items:
                return None
            
            task_dict = json.loads(items[0])
            return Task.from_dict(task_dict)
            
        except Exception as e:
            logger.error(f"Failed to peek task: {e}")
            return None
    
    def remove(self, task_id: str) -> bool:
        """
        移除指定任务
        
        Args:
            task_id: 任务 ID
            
        Returns:
            bool: 是否成功移除
        """
        try:
            # 获取所有任务
            all_tasks = self.redis.zrange(self.queue_key, 0, -1)
            
            for task_data in all_tasks:
                task_dict = json.loads(task_data)
                if task_dict.get("task_id") == task_id:
                    self.redis.zrem(self.queue_key, task_data)
                    logger.debug(f"Removed task {task_id} from queue")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to remove task: {e}")
            return False
    
    def get_by_project(self, project_id: str) -> List[Task]:
        """
        获取指定项目的所有任务
        
        Args:
            project_id: 项目 ID
            
        Returns:
            List[Task]: 任务列表
        """
        try:
            all_tasks = self.redis.zrange(self.queue_key, 0, -1)
            
            project_tasks = []
            for task_data in all_tasks:
                task_dict = json.loads(task_data)
                if task_dict.get("project_id") == project_id:
                    project_tasks.append(Task.from_dict(task_dict))
            
            return project_tasks
            
        except Exception as e:
            logger.error(f"Failed to get tasks by project: {e}")
            return []
    
    def size(self) -> int:
        """
        获取队列大小
        
        Returns:
            int: 队列中的任务数量
        """
        try:
            return self.redis.zcard(self.queue_key)
        except Exception as e:
            logger.error(f"Failed to get queue size: {e}")
            return 0
    
    def is_empty(self) -> bool:
        """
        检查队列是否为空
        
        Returns:
            bool: 队列是否为空
        """
        return self.size() == 0
    
    def clear(self) -> bool:
        """
        清空队列
        
        Returns:
            bool: 是否成功清空
        """
        try:
            self.redis.delete(self.queue_key)
            logger.info("Cleared task queue")
            return True
        except Exception as e:
            logger.error(f"Failed to clear queue: {e}")
            return False
    
    def get_all(self) -> List[Task]:
        """
        获取所有任务（不移除）
        
        Returns:
            List[Task]: 所有任务列表
        """
        try:
            all_tasks_data = self.redis.zrevrange(self.queue_key, 0, -1)
            
            tasks = []
            for task_data in all_tasks_data:
                task_dict = json.loads(task_data)
                tasks.append(Task.from_dict(task_dict))
            
            return tasks
            
        except Exception as e:
            logger.error(f"Failed to get all tasks: {e}")
            return []
