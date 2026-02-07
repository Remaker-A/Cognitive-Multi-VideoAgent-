"""
Event Bus 单元测试
"""

import pytest
import asyncio
from datetime import datetime

from src.infrastructure.event_bus import (
    Event,
    EventType,
    EventBus,
    EventSubscriber
)


class MockSubscriber(EventSubscriber):
    """Mock subscriber for testing"""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.received_events = []
    
    async def handle_event(self, event: Event):
        """Handle event by storing it"""
        self.received_events.append(event)


class TestEvent:
    """Event 测试"""
    
    def test_event_creation(self):
        """测试事件创建"""
        event = Event(
            project_id="TEST-001",
            type=EventType.PROJECT_CREATED,
            actor="TestAgent",
            payload={"title": "Test Project"}
        )
        
        assert event.project_id == "TEST-001"
        assert event.type == EventType.PROJECT_CREATED
        assert event.actor == "TestAgent"
        assert event.payload["title"] == "Test Project"
        assert event.event_id.startswith("EV-")
    
    def test_event_serialization(self):
        """测试事件序列化"""
        event = Event(
            event_id="EV-TEST-001",
            project_id="TEST-001",
            type=EventType.SCENE_WRITTEN,
            actor="ScriptWriter",
            causation_id="EV-TEST-000",
            payload={"script": "Test script"}
        )
        
        # 转换为字典
        event_dict = event.to_dict()
        
        assert event_dict["event_id"] == "EV-TEST-001"
        assert event_dict["type"] == "SCENE_WRITTEN"
        assert event_dict["causation_id"] == "EV-TEST-000"
        
        # 从字典恢复
        restored_event = Event.from_dict(event_dict)
        
        assert restored_event.event_id == event.event_id
        assert restored_event.type == event.type
        assert restored_event.payload == event.payload


@pytest.mark.asyncio
class TestEventBus:
    """Event Bus 测试"""
    
    async def test_connect_disconnect(self):
        """测试连接和断开"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        
        await event_bus.connect()
        assert event_bus.redis_client is not None
        
        await event_bus.disconnect()
    
    async def test_publish_event(self):
        """测试发布事件"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        await event_bus.connect()
        
        event = Event(
            project_id="TEST-002",
            type=EventType.PROJECT_CREATED,
            actor="TestAgent",
            payload={"test": "data"}
        )
        
        event_id = await event_bus.publish(event)
        
        assert event_id == event.event_id
        assert event in event_bus.event_history
        
        await event_bus.disconnect()
    
    async def test_subscribe_and_notify(self):
        """测试订阅和通知"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        await event_bus.connect()
        
        # 创建订阅者
        subscriber = MockSubscriber("TestSubscriber")
        event_bus.subscribe(subscriber, [EventType.PROJECT_CREATED])
        
        # 发布事件
        event = Event(
            project_id="TEST-003",
            type=EventType.PROJECT_CREATED,
            actor="TestAgent"
        )
        
        await event_bus.publish(event)
        
        # 等待事件处理
        await asyncio.sleep(0.1)
        
        # 验证订阅者收到事件
        assert len(subscriber.received_events) == 1
        assert subscriber.received_events[0].event_id == event.event_id
        
        await event_bus.disconnect()
    
    async def test_unsubscribe(self):
        """测试取消订阅"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        await event_bus.connect()
        
        subscriber = MockSubscriber("TestSubscriber")
        event_bus.subscribe(subscriber, [EventType.PROJECT_CREATED])
        event_bus.unsubscribe(subscriber, [EventType.PROJECT_CREATED])
        
        # 发布事件
        event = Event(
            project_id="TEST-004",
            type=EventType.PROJECT_CREATED,
            actor="TestAgent"
        )
        
        await event_bus.publish(event)
        await asyncio.sleep(0.1)
        
        # 验证订阅者未收到事件
        assert len(subscriber.received_events) == 0
        
        await event_bus.disconnect()
    
    async def test_causation_chain(self):
        """测试链路追踪"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        await event_bus.connect()
        
        # 创建事件链
        event1 = Event(
            event_id="EV-CHAIN-001",
            project_id="TEST-005",
            type=EventType.PROJECT_CREATED,
            actor="Agent1"
        )
        
        event2 = Event(
            event_id="EV-CHAIN-002",
            project_id="TEST-005",
            type=EventType.SCENE_WRITTEN,
            actor="Agent2",
            causation_id="EV-CHAIN-001"
        )
        
        event3 = Event(
            event_id="EV-CHAIN-003",
            project_id="TEST-005",
            type=EventType.SHOT_PLANNED,
            actor="Agent3",
            causation_id="EV-CHAIN-002"
        )
        
        await event_bus.publish(event1)
        await event_bus.publish(event2)
        await event_bus.publish(event3)
        
        # 获取链路
        chain = event_bus.get_causation_chain("EV-CHAIN-003")
        
        assert len(chain) == 3
        assert chain[0].event_id == "EV-CHAIN-001"
        assert chain[1].event_id == "EV-CHAIN-002"
        assert chain[2].event_id == "EV-CHAIN-003"
        
        await event_bus.disconnect()
    
    async def test_replay_events(self):
        """测试事件重放"""
        event_bus = EventBus(redis_url="redis://localhost:6379/1")
        await event_bus.connect()
        
        project_id = "TEST-006"
        
        # 发布多个事件
        for i in range(5):
            event = Event(
                project_id=project_id,
                type=EventType.IMAGE_GENERATED,
                actor=f"Agent{i}",
                payload={"index": i}
            )
            await event_bus.publish(event)
        
        # 等待事件写入 Redis
        await asyncio.sleep(0.5)
        
        # 重放事件
        replayed_events = await event_bus.replay_events(project_id)
        
        assert len(replayed_events) >= 5
        
        await event_bus.disconnect()


def test_event_types():
    """测试事件类型枚举"""
    # 验证所有关键事件类型存在
    assert EventType.PROJECT_CREATED
    assert EventType.SCENE_WRITTEN
    assert EventType.SHOT_PLANNED
    assert EventType.IMAGE_GENERATED
    assert EventType.USER_APPROVAL_REQUIRED
    assert EventType.USER_APPROVED
    assert EventType.CONSISTENCY_FAILED
    assert EventType.FINAL_VIDEO_READY


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
