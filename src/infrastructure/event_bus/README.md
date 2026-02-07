# Event Bus

Event Bus 是 LivingAgentPipeline v2.0 的核心通信层，基于 Redis Streams 实现，提供异步事件发布/订阅、事件持久化、链路追踪和事件重放功能。

## 技术栈

- **Redis Streams**: 消息队列和事件持久化
- **PostgreSQL**: 长期事件存储和分析
- **asyncio**: 异步事件处理

## 核心特性

✅ **异步事件发布/订阅**: 基于 Redis Streams 的高性能消息传递
✅ **事件持久化**: 支持 Redis + PostgreSQL 双层存储
✅ **链路追踪**: 完整的 causation_id 追踪链
✅ **事件重放**: 支持按项目、时间、类型重放事件
✅ **多订阅者**: 一个事件可被多个 Agent 订阅
✅ **消费者组**: Redis Streams 消费者组保证消息不丢失
✅ **事件统计**: 自动统计事件指标和成本

## 快速开始

### 1. 安装依赖

```bash
pip install redis[asyncio] pydantic
```

### 2. 启动 Redis

```bash
docker-compose up -d redis
```

### 3. 基础使用

```python
import asyncio
from src.infrastructure.event_bus import Event, EventType
from src.infrastructure.event_bus.factory import EventBusFactory

async def main():
    # 创建 Event Bus
    event_bus = await EventBusFactory.create()
    
    # 创建事件
    event = Event(
        project_id="PROJ-001",
        type=EventType.PROJECT_CREATED,
        actor="RequirementParser",
        payload={"title": "My Project"}
    )
    
    # 发布事件
    await event_bus.publish(event)
    
    # 断开连接
    await event_bus.disconnect()

asyncio.run(main())
```

## 核心功能

### 事件发布

```python
event = Event(
    project_id="PROJ-001",
    type=EventType.SCENE_WRITTEN,
    actor="ScriptWriter",
    causation_id="EV-001",  # 链路追踪
    payload={
        "script": "Scene description...",
        "duration": 30
    },
    metadata={
        "cost": 0.05,
        "latency_ms": 1200
    }
)

event_id = await event_bus.publish(event)
```

### 事件订阅

```python
from src.infrastructure.event_bus import EventSubscriber

class MyAgent(EventSubscriber):
    def __init__(self):
        super().__init__("MyAgent")
    
    async def handle_event(self, event: Event):
        print(f"Received: {event.type.value}")
        # 处理事件逻辑

# 订阅事件
agent = MyAgent()
event_bus.subscribe(agent, [
    EventType.PROJECT_CREATED,
    EventType.SCENE_WRITTEN
])

# 启动消费
await event_bus.start_consuming()
```

### 链路追踪

```python
# 获取事件的完整链路
chain = event_bus.get_causation_chain("EV-12345")

for event in chain:
    print(f"{event.event_id} -> {event.type.value} by {event.actor}")
```

### 事件重放

```python
from datetime import datetime, timedelta

# 重放最近 24 小时的事件
start_time = datetime.utcnow() - timedelta(hours=24)
events = await event_bus.replay_events(
    project_id="PROJ-001",
    start_time=start_time,
    event_types=[EventType.IMAGE_GENERATED]
)

for event in events:
    print(f"{event.timestamp}: {event.type.value}")
```

### 事件持久化

```python
from src.infrastructure.event_bus.persistence import EventPersistence
from src.infrastructure.blackboard.factory import BlackboardFactory

# 创建 Blackboard
blackboard = BlackboardFactory.create()

# 创建持久化层
persistence = EventPersistence(blackboard)

# 持久化事件
await persistence.persist_event(event)

# 查询事件
events = await persistence.get_events(
    project_id="PROJ-001",
    event_types=[EventType.IMAGE_GENERATED],
    limit=100
)

# 获取统计
stats = await persistence.get_event_statistics("PROJ-001")
print(stats)
```

## 更多示例

查看 `examples/event_bus_usage.py` 获取完整的使用示例。

## 测试

```bash
pytest tests/test_event_bus.py -v
```

## License

MIT
