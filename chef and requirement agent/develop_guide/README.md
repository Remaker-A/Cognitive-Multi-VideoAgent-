# {AgentName}

## 概述

{AgentName} 是 LivingAgentPipeline 系统中的一个核心 Agent，负责...

## 职责

- 职责 1 的详细说明
- 职责 2 的详细说明
- 职责 3 的详细说明

## 事件交互

### 订阅事件

| 事件类型 | 说明 | 触发条件 |
|---------|------|---------|
| `EVENT_TYPE_1` | 事件说明 | 触发条件 |
| `EVENT_TYPE_2` | 事件说明 | 触发条件 |

### 发布事件

| 事件类型 | 说明 | 发布时机 |
|---------|------|---------|
| `RESULT_EVENT_TYPE` | 结果事件说明 | 成功时 |
| `ERROR_OCCURRED` | 错误事件 | 失败时 |

## Blackboard 数据访问

### 读取数据

- 读取 1 的说明
- 读取 2 的说明

### 写入数据

- 写入 1 的说明
- 写入 2 的说明

## 配置

### 环境变量

```bash
# Agent 基础配置
AGENT_NAME={AgentName}
AGENT_MAX_RETRIES=3
AGENT_TIMEOUT_SECONDS=30

# Event Bus 配置
AGENT_EVENT_BUS_URL=redis://localhost:6379

# Blackboard 配置
AGENT_BLACKBOARD_URL=http://localhost:8000

# API 配置（如果需要）
AGENT_API_KEY=your_api_key_here
AGENT_API_ENDPOINT=https://api.example.com
```

### 配置示例 (`.env`)

```env
AGENT_NAME=MyCustomAgent
AGENT_MAX_RETRIES=5
AGENT_API_KEY=sk_test_12345
```

## 使用示例

### 基本用法

```python
import asyncio
from src.agents.your_agent import {AgentName}
from src.infrastructure.event_bus import EventBus

async def main():
    # 创建 Event Bus
    event_bus = EventBus(redis_url="redis://localhost:6379")
    await event_bus.connect()
    
    # 创建并注册 Agent
    agent = {AgentName}()
    event_bus.subscribe(agent, agent.subscribed_events)
    
    # 启动事件消费
    await event_bus.start_consuming()
    
    # Agent 现在会自动处理订阅的事件
    # ...
    
    # 清理
    await event_bus.stop_consuming()
    await event_bus.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
```

### 自定义配置

```python
from src.agents.your_agent import {AgentName}
from src.agents.your_agent.config import {AgentName}Config

# 创建自定义配置
config = {AgentName}Config(
    agent_name="CustomAgent",
    max_retries=5,
    timeout_seconds=60
)

# 创建 Agent
agent = {AgentName}(name=config.agent_name)
```

## 开发

### 运行测试

```bash
# 运行所有测试
pytest tests/test_{agent_name}.py -v

# 运行特定测试
pytest tests/test_{agent_name}.py::Test{AgentName}::test_handle_event_success -v

# 查看覆盖率
pytest tests/test_{agent_name}.py --cov=src.agents.your_agent --cov-report=html
```

### 调试

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 创建 Agent
agent = {AgentName}()
```

## 性能指标

| 指标 | 目标值 | 当前值 |
|-----|-------|--------|
| 事件处理延迟 | < 100ms | TBD |
| 成功率 | > 95% | TBD |
| 平均成本 | < $0.10 | TBD |

## 错误处理

### 常见错误

#### 错误 1: Blackboard 连接失败

**症状**: Agent 无法读取/写入数据

**解决方案**:
1. 检查 Blackboard 服务是否运行
2. 验证配置的 URL 是否正确
3. 检查网络连接

#### 错误 2: API 调用超时

**症状**: 外部 API 调用超时

**解决方案**:
1. 增加 `timeout_seconds` 配置
2. 检查 API 服务状态
3. 启用重试机制

### 重试策略

Agent 实现了三层错误恢复策略：

1. **Level 1**: 自动重试（最多 3 次）
2. **Level 2**: 降级策略（如适用）
3. **Level 3**: 发布错误事件，等待人工介入

## 监控

### 日志

Agent 会记录以下日志：

- `INFO`: 正常操作（事件接收、处理完成）
- `WARNING`: 警告信息（重试、降级）
- `ERROR`: 错误信息（处理失败）

### 指标

可以通过以下方式监控 Agent：

```python
# 查看事件处理统计
total_events = len(await event_bus.get_project_events(project_id))

# 查看错误日志
errors = project.error_log
```

## 贡献

在修改 {AgentName} 时，请遵循以下规范：

1. 更新测试以覆盖新功能
2. 保持测试覆盖率 > 80%
3. 更新文档
4. 遵循代码风格指南

## 参考资料

- [开发规范](file:///d:/下载/contracts/DEVELOPMENT_STANDARDS.md)
- [Event Bus 文档](file:///d:/文档/Kiro/VIdeoGen/src/infrastructure/event_bus/README.md)
- [契约指南](file:///d:/文档/Kiro/VIdeoGen/docs/CONTRACT_GUIDE.md)

---

**最后更新**: 2025-12-26
