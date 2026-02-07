"""
Event Bus 工厂类

提供便捷的 Event Bus 实例创建方法
"""

from typing import Optional
import redis.asyncio as redis

from .event_bus import EventBus
from .config import EventBusConfig
from .persistence import EventPersistence
from ..blackboard.blackboard import SharedBlackboard


class EventBusFactory:
    """Event Bus 工厂"""
    
    @staticmethod
    async def create(
        config: Optional[EventBusConfig] = None,
        blackboard: Optional[SharedBlackboard] = None
    ) -> EventBus:
        """
        创建 Event Bus 实例
        
        Args:
            config: 配置对象，如果为 None 则使用默认配置
            blackboard: Blackboard 实例（用于事件持久化）
            
        Returns:
            EventBus: Event Bus 实例
        """
        if config is None:
            config = EventBusConfig()
        
        # 构建 Redis URL
        redis_url = config.redis_url
        if config.redis_password:
            # 插入密码到 URL
            parts = redis_url.split("://")
            redis_url = f"{parts[0]}://:{config.redis_password}@{parts[1]}"
        
        # 创建 Event Bus
        event_bus = EventBus(
            redis_url=redis_url,
            stream_prefix=config.stream_prefix,
            consumer_group=config.consumer_group
        )
        
        # 连接到 Redis
        await event_bus.connect()
        
        # 如果提供了 Blackboard，启用持久化
        if blackboard and config.enable_event_persistence:
            persistence = EventPersistence(blackboard)
            event_bus.persistence = persistence
        
        return event_bus
    
    @staticmethod
    async def create_for_testing() -> EventBus:
        """
        创建用于测试的 Event Bus 实例
        
        Returns:
            EventBus: 测试用 Event Bus 实例
        """
        config = EventBusConfig(
            redis_url="redis://localhost:6379/1",  # 使用不同的数据库
            stream_prefix="test_event_stream",
            consumer_group="test_group"
        )
        
        return await EventBusFactory.create(config)


class EventBusManager:
    """
    Event Bus 管理器
    
    提供 Event Bus 的生命周期管理
    """
    
    def __init__(self, event_bus: EventBus):
        """
        初始化管理器
        
        Args:
            event_bus: Event Bus 实例
        """
        self.event_bus = event_bus
        self._started = False
    
    async def start(self):
        """启动 Event Bus"""
        if not self._started:
            await self.event_bus.start_consuming()
            self._started = True
    
    async def stop(self):
        """停止 Event Bus"""
        if self._started:
            await self.event_bus.stop_consuming()
            await self.event_bus.disconnect()
            self._started = False
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.start()
        return self.event_bus
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.stop()
