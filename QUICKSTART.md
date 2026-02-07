# Event Bus 快速启动指南

本指南帮助你快速搭建和测试 Event Bus 基础设施。

## 前置要求

- Python 3.9+
- Docker 和 Docker Compose（用于运行 Redis）
- Git

## 步骤 1: 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 步骤 2: 启动 Redis

使用 Docker Compose 启动 Redis：

```bash
docker-compose up -d
```

验证 Redis 是否运行：

```bash
docker ps
```

你应该看到两个容器：
- `livingagent-redis`: Redis 服务器（端口 6379）
- `livingagent-redis-commander`: Redis 管理界面（端口 8081）

访问 Redis Commander: http://localhost:8081

## 步骤 3: 运行示例

运行 Event Bus 示例程序：

```bash
python examples/event_bus_example.py
```

你应该看到类似以下的输出：

```
2025-11-23 10:00:00 - __main__ - INFO - === Creating Event Bus ===
2025-11-23 10:00:00 - event_bus - INFO - Connected to Redis at redis://localhost:6379
2025-11-23 10:00:00 - __main__ - INFO - === Creating Agents ===
2025-11-23 10:00:00 - __main__ - INFO - === Subscribing Agents ===
2025-11-23 10:00:00 - event_bus - INFO - ScriptWriter subscribed to ['PROJECT_CREATED']
...
```

## 步骤 4: 运行测试

运行单元测试：

```bash
pytest tests/infrastructure/test_event_bus.py -v
```

预期输出：

```
tests/infrastructure/test_event_bus.py::test_event_creation PASSED
tests/infrastructure/test_event_bus.py::test_subscribe_and_publish PASSED
tests/infrastructure/test_event_bus.py::test_multiple_subscribers PASSED
tests/infrastructure/test_event_bus.py::test_causation_tracking PASSED
tests/infrastructure/test_event_bus.py::test_event_replay PASSED
tests/infrastructure/test_event_bus.py::test_unsubscribe PASSED
tests/infrastructure/test_event_bus.py::test_event_filtering PASSED
```

## 步骤 5: 查看 Redis 数据

在 Redis Commander (http://localhost:8081) 中，你可以看到：

1. **Event Streams**: 以 `event_stream:` 为前缀的 Stream
2. **Consumer Groups**: 每个 Stream 的消费者组
3. **Event Data**: 点击 Stream 查看事件详情

## 验证功能

### 1. 事件发布和订阅

创建一个简单的测试脚本 `test_publish.py`：

```python
import asyncio
from src.infrastructure.event_bus import EventBus, Event, EventType, EventSubscriber

class TestAgent(EventSubscriber):
    def __init__(self):
        super().__init__("TestAgent")
    
    async def handle_event(self, event: Event):
        print(f"Received: {event.type.value} - {event.payload}")

async def main():
    bus = EventBus()
    await bus.connect()
    
    agent = TestAgent()
    bus.subscribe(agent, [EventType.PROJECT_CREATED])
    
    event = Event(
        project_id="TEST-001",
        type=EventType.PROJECT_CREATED,
        actor="System",
        payload={"message": "Hello Event Bus!"}
    )
    
    await bus.publish(event)
    await asyncio.sleep(1)
    await bus.disconnect()

asyncio.run(main())
```

运行：

```bash
python test_publish.py
```

### 2. 因果链追踪

修改上面的脚本，发布多个相关事件：

```python
# 发布第一个事件
event1 = Event(
    project_id="TEST-001",
    type=EventType.PROJECT_CREATED,
    actor="System"
)
event1_id = await bus.publish(event1)

# 发布第二个事件（由第一个事件触发）
event2 = Event(
    project_id="TEST-001",
    type=EventType.SCENE_WRITTEN,
    actor="ScriptWriter",
    causation_id=event1_id
)
event2_id = await bus.publish(event2)

# 获取因果链
chain = bus.get_causation_chain(event2_id)
print(f"Causation chain: {[e.type.value for e in chain]}")
```

### 3. 事件重放

```python
# 重放项目的所有事件
events = await bus.replay_events("TEST-001")
print(f"Total events: {len(events)}")
for event in events:
    print(f"  {event.type.value} at {event.timestamp}")
```

## 常见问题

### Q: Redis 连接失败

**A**: 确保 Docker 容器正在运行：

```bash
docker-compose ps
docker-compose logs redis
```

### Q: 测试失败

**A**: 清理 Redis 数据后重试：

```bash
docker-compose down -v
docker-compose up -d
```

### Q: 如何查看事件详情？

**A**: 使用 Redis Commander (http://localhost:8081) 或 Redis CLI：

```bash
docker exec -it livingagent-redis redis-cli
> XRANGE event_stream:PROJECT_CREATED - +
```

### Q: 如何停止服务？

**A**: 停止 Docker 容器：

```bash
docker-compose down
```

保留数据：

```bash
docker-compose stop
```

## 下一步

1. 阅读 [Event Bus README](src/infrastructure/event_bus/README.md) 了解详细功能
2. 查看 [Design Document](.kiro/specs/unified-agent-system-design/design.md) 了解系统架构
3. 开始实现其他 Agent（参考 [Tasks](.kiro/specs/unified-agent-system-design/tasks.md)）

## 性能测试

运行性能测试脚本：

```python
import asyncio
import time
from src.infrastructure.event_bus import EventBus, Event, EventType

async def benchmark():
    bus = EventBus()
    await bus.connect()
    
    # 发布 1000 个事件
    start = time.time()
    for i in range(1000):
        event = Event(
            project_id=f"BENCH-{i}",
            type=EventType.PROJECT_CREATED,
            actor="Benchmark"
        )
        await bus.publish(event)
    
    elapsed = time.time() - start
    print(f"Published 1000 events in {elapsed:.2f}s")
    print(f"Throughput: {1000/elapsed:.0f} events/sec")
    
    await bus.disconnect()

asyncio.run(benchmark())
```

预期吞吐量：> 1000 events/sec

## 监控

使用 Redis Commander 监控：

1. **Stream 长度**: 查看每个 Stream 的消息数量
2. **Consumer Groups**: 查看消费者状态
3. **Pending Messages**: 查看未确认的消息

## 故障排查

启用调试日志：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

查看 Redis 日志：

```bash
docker-compose logs -f redis
```

## 清理

完全清理环境：

```bash
# 停止并删除容器和数据
docker-compose down -v

# 删除虚拟环境
deactivate
rm -rf venv
```

## 支持

如有问题，请查看：
- [Event Bus README](src/infrastructure/event_bus/README.md)
- [Design Document](.kiro/specs/unified-agent-system-design/design.md)
- [GitHub Issues](https://github.com/your-repo/issues)
