"""
Event Bus 使用示例
"""

import asyncio
from datetime import datetime

from src.infrastructure.event_bus import (
    Event,
    EventType,
    EventBus,
    EventSubscriber
)
from src.infrastructure.event_bus.factory import EventBusFactory, EventBusManager


# ========== 示例 1: 基础使用 ==========

async def example_basic_usage():
    """基础使用示例"""
    print("=== Example 1: Basic Usage ===\n")
    
    # 创建 Event Bus
    event_bus = await EventBusFactory.create()
    
    # 创建事件
    event = Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser",
        payload={
            "title": "Rain and Warmth",
            "duration": 30,
            "aspect_ratio": "9:16"
        },
        metadata={
            "cost": 0.0,
            "latency_ms": 100
        }
    )
    
    # 发布事件
    event_id = await event_bus.publish(event)
    print(f"Published event: {event_id}")
    
    await event_bus.disconnect()


# ========== 示例 2: 订阅和处理事件 ==========

class ScriptWriterAgent(EventSubscriber):
    """剧本编写 Agent"""
    
    def __init__(self):
        super().__init__("ScriptWriter")
    
    async def handle_event(self, event: Event):
        """处理 PROJECT_CREATED 事件"""
        print(f"[{self.name}] Received event: {event.type.value}")
        print(f"  Project: {event.project_id}")
        print(f"  Payload: {event.payload}")
        
        # 模拟剧本编写
        await asyncio.sleep(0.5)
        
        # 发布 SCENE_WRITTEN 事件
        # (在实际应用中，需要访问 Event Bus 实例)
        print(f"[{self.name}] Script written!")


async def example_subscribe_and_handle():
    """订阅和处理事件示例"""
    print("\n=== Example 2: Subscribe and Handle ===\n")
    
    event_bus = await EventBusFactory.create()
    
    # 创建订阅者
    script_writer = ScriptWriterAgent()
    
    # 订阅事件
    event_bus.subscribe(script_writer, [EventType.PROJECT_CREATED])
    
    # 发布事件
    event = Event(
        project_id="PROJ-002",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser",
        payload={"title": "Test Project"}
    )
    
    await event_bus.publish(event)
    
    # 等待事件处理
    await asyncio.sleep(1)
    
    await event_bus.disconnect()


# ========== 示例 3: 链路追踪 ==========

async def example_causation_tracking():
    """链路追踪示例"""
    print("\n=== Example 3: Causation Tracking ===\n")
    
    event_bus = await EventBusFactory.create()
    
    # 创建事件链
    event1 = Event(
        event_id="EV-001",
        project_id="PROJ-003",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser"
    )
    
    event2 = Event(
        event_id="EV-002",
        project_id="PROJ-003",
        type=EventType.SCENE_WRITTEN,
        actor="ScriptWriter",
        causation_id="EV-001"  # 由 EV-001 引起
    )
    
    event3 = Event(
        event_id="EV-003",
        project_id="PROJ-003",
        type=EventType.SHOT_PLANNED,
        actor="ShotDirector",
        causation_id="EV-002"  # 由 EV-002 引起
    )
    
    # 发布事件
    await event_bus.publish(event1)
    await event_bus.publish(event2)
    await event_bus.publish(event3)
    
    # 获取链路
    chain = event_bus.get_causation_chain("EV-003")
    
    print("Causation Chain:")
    for i, event in enumerate(chain, 1):
        print(f"  {i}. {event.event_id} ({event.type.value}) by {event.actor}")
    
    await event_bus.disconnect()


# ========== 示例 4: 事件重放 ==========

async def example_event_replay():
    """事件重放示例"""
    print("\n=== Example 4: Event Replay ===\n")
    
    event_bus = await EventBusFactory.create()
    
    project_id = "PROJ-004"
    
    # 发布一系列事件
    events_to_publish = [
        (EventType.PROJECT_CREATED, "RequirementParser"),
        (EventType.SCENE_WRITTEN, "ScriptWriter"),
        (EventType.SHOT_PLANNED, "ShotDirector"),
        (EventType.IMAGE_GENERATED, "ImageGenAgent"),
        (EventType.PREVIEW_VIDEO_READY, "VideoGenAgent")
    ]
    
    for event_type, actor in events_to_publish:
        event = Event(
            project_id=project_id,
            type=event_type,
            actor=actor
        )
        await event_bus.publish(event)
    
    # 等待事件写入 Redis
    await asyncio.sleep(1)
    
    # 重放事件
    replayed_events = await event_bus.replay_events(project_id)
    
    print(f"Replayed {len(replayed_events)} events:")
    for event in replayed_events:
        print(f"  - {event.type.value} by {event.actor} at {event.timestamp}")
    
    await event_bus.disconnect()


# ========== 示例 5: 使用管理器 ==========

async def example_with_manager():
    """使用管理器示例"""
    print("\n=== Example 5: With Manager ===\n")
    
    event_bus = await EventBusFactory.create()
    
    # 使用管理器自动管理生命周期
    async with EventBusManager(event_bus) as bus:
        # Event Bus 已启动
        
        event = Event(
            project_id="PROJ-005",
            type=EventType.PROJECT_CREATED,
            actor="TestAgent"
        )
        
        await bus.publish(event)
        print("Event published through manager")
        
        await asyncio.sleep(0.5)
    
    # Event Bus 已自动停止和断开
    print("Manager automatically stopped Event Bus")


# ========== 示例 6: 多订阅者 ==========

class ImageGenAgent(EventSubscriber):
    """图像生成 Agent"""
    
    def __init__(self):
        super().__init__("ImageGenAgent")
    
    async def handle_event(self, event: Event):
        print(f"[{self.name}] Processing {event.type.value}")
        await asyncio.sleep(0.3)
        print(f"[{self.name}] Generated image for shot {event.payload.get('shot_id')}")


class ConsistencyGuardian(EventSubscriber):
    """一致性守护 Agent"""
    
    def __init__(self):
        super().__init__("ConsistencyGuardian")
    
    async def handle_event(self, event: Event):
        print(f"[{self.name}] Checking consistency for {event.type.value}")
        await asyncio.sleep(0.2)
        print(f"[{self.name}] Consistency check passed")


async def example_multiple_subscribers():
    """多订阅者示例"""
    print("\n=== Example 6: Multiple Subscribers ===\n")
    
    event_bus = await EventBusFactory.create()
    
    # 创建多个订阅者
    image_gen = ImageGenAgent()
    consistency = ConsistencyGuardian()
    
    # 订阅同一事件类型
    event_bus.subscribe(image_gen, [EventType.KEYFRAME_REQUESTED])
    event_bus.subscribe(consistency, [EventType.IMAGE_GENERATED])
    
    # 发布事件
    event1 = Event(
        project_id="PROJ-006",
        type=EventType.KEYFRAME_REQUESTED,
        actor="ShotDirector",
        payload={"shot_id": "S01"}
    )
    
    await event_bus.publish(event1)
    await asyncio.sleep(0.5)
    
    # ImageGenAgent 处理后发布新事件
    event2 = Event(
        project_id="PROJ-006",
        type=EventType.IMAGE_GENERATED,
        actor="ImageGenAgent",
        causation_id=event1.event_id,
        payload={"shot_id": "S01", "artifact_url": "s3://..."}
    )
    
    await event_bus.publish(event2)
    await asyncio.sleep(0.5)
    
    await event_bus.disconnect()


# ========== 主函数 ==========

async def main():
    """运行所有示例"""
    print("\n" + "="*60)
    print("  Event Bus Usage Examples")
    print("="*60)
    
    await example_basic_usage()
    await example_subscribe_and_handle()
    await example_causation_tracking()
    await example_event_replay()
    await example_with_manager()
    await example_multiple_subscribers()
    
    print("\n" + "="*60)
    print("  All Examples Complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
