# LivingAgentPipeline - Event Bus Infrastructure

这是 LivingAgentPipeline v2.0 统一 Agent 系统的 Event Bus 基础设施实现。

## 项目概述

LivingAgentPipeline 是一个基于事件驱动架构的多 Agent AI 视频生成系统。本仓库实现了系统的核心消息传递基础设施 - Event Bus。

### 核心特性

- ✅ **事件驱动架构**: Agent 之间通过事件异步通信，实现松耦合
- ✅ **Redis Streams**: 基于 Redis Streams 实现高性能消息队列
- ✅ **事件持久化**: 所有事件持久化存储，支持审计和重放
- ✅ **因果链追踪**: 通过 causation_id 追踪完整的事件链路
- ✅ **消费者组**: 支持负载均衡和故障恢复
- ✅ **类型安全**: 使用 Python 类型提示和 Pydantic 验证

## 快速开始

### 1. 克隆仓库

```bash
git clone <repository-url>
cd livingagent-pipeline
```

### 2. 安装依赖

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 启动 Redis

```bash
docker-compose up -d
```

### 4. 运行示例

```bash
python examples/event_bus_example.py
```

详细步骤请参考 [QUICKSTART.md](QUICKSTART.md)

## 项目结构

```
.
├── src/
│   └── infrastructure/
│       └── event_bus/
│           ├── __init__.py
│           ├── event.py           # 事件数据模型
│           ├── event_bus.py       # Event Bus 核心实现
│           ├── subscriber.py      # 订阅者基类
│           ├── config.py          # 配置管理
│           └── README.md          # 详细文档
├── tests/
│   └── infrastructure/
│       └── test_event_bus.py      # 单元测试
├── examples/
│   └── event_bus_example.py       # 使用示例
├── .kiro/
│   └── specs/
│       └── unified-agent-system-design/
│           ├── requirements.md    # 需求文档
│           ├── design.md          # 设计文档
│           └── tasks.md           # 任务列表
├── docker-compose.yml             # Docker 配置
├── requirements.txt               # Python 依赖
├── QUICKSTART.md                  # 快速启动指南
└── README.md                      # 本文件
```

## 架构设计

### 事件驱动架构

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Agent A   │         │  Event Bus  │         │   Agent B   │
│             │         │             │         │             │
│  publish()  │────────>│   Redis     │────────>│  handle()   │
│             │         │  Streams    │         │             │
└─────────────┘         └─────────────┘         └─────────────┘
```

### 核心组件

1. **Event**: 标准化的事件数据模型
2. **EventBus**: 事件发布/订阅管理
3. **EventSubscriber**: Agent 订阅者基类
4. **Redis Streams**: 消息队列和持久化

详细设计请参考 [Design Document](.kiro/specs/unified-agent-system-design/design.md)

## 使用示例

### 发布事件

```python
from src.infrastructure.event_bus import EventBus, Event, EventType

# 创建 Event Bus
bus = EventBus()
await bus.connect()

# 发布事件
event = Event(
    project_id="PROJ-001",
    type=EventType.IMAGE_GENERATED,
    actor="ImageGenAgent",
    payload={"artifact_url": "s3://bucket/image.png"}
)

event_id = await bus.publish(event)
```

### 订阅事件

```python
from src.infrastructure.event_bus import EventSubscriber

class MyAgent(EventSubscriber):
    def __init__(self):
        super().__init__("MyAgent")
    
    async def handle_event(self, event: Event):
        print(f"Received: {event.type.value}")

# 订阅
agent = MyAgent()
bus.subscribe(agent, [EventType.IMAGE_GENERATED])
```

更多示例请参考 [examples/event_bus_example.py](examples/event_bus_example.py)

## 测试

运行单元测试：

```bash
pytest tests/infrastructure/test_event_bus.py -v
```

运行性能测试：

```bash
python tests/infrastructure/benchmark_event_bus.py
```

## 配置

通过环境变量或 `.env` 文件配置：

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置
vim .env
```

主要配置项：

- `REDIS_URL`: Redis 连接地址
- `EVENT_STREAM_PREFIX`: Stream 键前缀
- `EVENT_CONSUMER_GROUP`: 消费者组名称
- `EVENT_MAX_STREAM_LENGTH`: Stream 最大长度

详细配置请参考 [src/infrastructure/event_bus/README.md](src/infrastructure/event_bus/README.md)

## 文档

- [快速启动指南](QUICKSTART.md)
- [Event Bus 详细文档](src/infrastructure/event_bus/README.md)
- [需求文档](.kiro/specs/unified-agent-system-design/requirements.md)
- [设计文档](.kiro/specs/unified-agent-system-design/design.md)
- [任务列表](.kiro/specs/unified-agent-system-design/tasks.md)

## 开发路线图

当前实现的是 **Phase 1: 核心基础设施** 中的任务 2：

- [x] 任务 2: 搭建 Event Bus 基础设施
  - [x] 选择并配置消息队列（Redis Streams）
  - [x] 实现事件发布/订阅机制
  - [x] 实现事件持久化和重放功能
  - [x] 实现 causation_id 链路追踪
  - [x] 编写 Event Bus API

下一步任务：

- [ ] 任务 1: 搭建 Shared Blackboard 基础设施
- [ ] 任务 3: 实现 Orchestrator 核心功能
- [ ] 任务 4: 实现 Storage Service

完整任务列表请参考 [tasks.md](.kiro/specs/unified-agent-system-design/tasks.md)

## 性能指标

- **吞吐量**: > 1000 events/sec
- **延迟**: < 10ms (本地订阅者)
- **持久化**: 所有事件持久化到 Redis
- **可靠性**: 至少一次消费保证

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

- 项目文档: [Design Document](.kiro/specs/unified-agent-system-design/design.md)
- Issue Tracker: [GitHub Issues](https://github.com/your-repo/issues)

## 致谢

本项目基于以下设计文档开发：

- [LivingAgentPipeline v2.0 统一设计文档](.kiro/specs/unified-agent-system-design/design.md)
- [需求文档](.kiro/specs/unified-agent-system-design/requirements.md)

---

**Status**: ✅ Task 2 Complete - Event Bus Infrastructure Implemented

**Next**: Task 1 - Shared Blackboard Infrastructure
