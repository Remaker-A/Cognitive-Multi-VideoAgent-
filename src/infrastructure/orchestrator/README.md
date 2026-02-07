# Orchestrator

Orchestrator 是 LivingAgentPipeline v2.0 的任务编排中心，负责事件到任务的映射、任务调度、依赖检查、预算控制和用户审批流程管理。

## 核心特性

✅ **事件到任务映射**: 自动将事件转换为可执行任务
✅ **优先级任务队列**: 基于 Redis Sorted Set 的持久化队列
✅ **任务状态机**: 7 种状态的严格转换控制
✅ **依赖检查**: 自动检查任务依赖关系
✅ **分布式锁**: 保证并发任务的数据一致性
✅ **预算控制**: 实时检查和成本预测
✅ **用户审批**: 4 个默认审批检查点

## 快速开始

### 1. 安装依赖

```bash
pip install redis psycopg2-binary
```

### 2. 启动服务

```bash
docker-compose up -d
```

### 3. 基础使用

```python
import asyncio
from src.infrastructure.blackboard.factory import BlackboardFactory
from src.infrastructure.event_bus.factory import EventBusFactory
from src.infrastructure.orchestrator.factory import OrchestratorFactory

async def main():
    # 创建 Blackboard 和 Event Bus
    blackboard = BlackboardFactory.create()
    event_bus = await EventBusFactory.create()
    
    # 创建并启动 Orchestrator
    orchestrator = await OrchestratorFactory.create_and_start(
        blackboard,
        event_bus
    )
    
    # Orchestrator 现在会自动处理事件和调度任务
    
    # 停止
    await orchestrator.stop()

asyncio.run(main())
```

## 核心组件

### 1. Task 数据模型

**30+ 任务类型**:
- 剧本: `WRITE_SCRIPT`, `REVISE_SCRIPT`
- 分镜: `PLAN_SHOTS`, `REVISE_SHOTS`
- 图像: `GENERATE_KEYFRAME`, `EDIT_IMAGE`
- 视频: `GENERATE_PREVIEW_VIDEO`, `GENERATE_FINAL_VIDEO`
- QA: `RUN_VISUAL_QA`, `CHECK_CONSISTENCY`

**7 种状态**:
- `PENDING`: 等待执行
- `READY`: 依赖满足，可执行
- `RUNNING`: 执行中
- `COMPLETED`: 完成
- `FAILED`: 失败
- `CANCELLED`: 取消
- `WAITING_APPROVAL`: 等待审批

### 2. 优先级任务队列

```python
from src.infrastructure.orchestrator import PriorityTaskQueue

queue = PriorityTaskQueue(redis_client)

# 添加任务
queue.put(task)

# 获取最高优先级任务
next_task = queue.get()

# 查看队列大小
size = queue.size()
```

### 3. 事件映射

```python
from src.infrastructure.orchestrator import EventMapper

mapper = EventMapper()

# 映射事件到任务
tasks = mapper.map_event_to_tasks(event)
```

### 4. 任务调度

```python
from src.infrastructure.orchestrator import TaskScheduler

scheduler = TaskScheduler(blackboard, state_machine)

# 检查依赖
if scheduler.check_dependencies(task):
    # 获取锁
    if await scheduler.acquire_lock(task):
        # 分发任务
        await scheduler.dispatch_task(task)
```

### 5. 预算检查

```python
from src.infrastructure.orchestrator import BudgetChecker

checker = BudgetChecker(blackboard)

# 检查预算
if checker.check_budget(project_id, estimated_cost):
    # 执行任务
    pass

# 获取预算状态
status = checker.get_budget_status(project_id)
```

## 配置

### 环境变量

```bash
# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 任务队列配置
TASK_QUEUE_KEY=orchestrator:task_queue
MAX_CONCURRENT_TASKS=10

# 调度配置
SCHEDULER_INTERVAL=1
TASK_TIMEOUT=300

# 预算配置
BUDGET_CHECK_ENABLED=true
BUDGET_WARNING_THRESHOLD=0.9

# 审批配置
APPROVAL_ENABLED=true
APPROVAL_TIMEOUT=60
```

### 代码配置

```python
from src.infrastructure.orchestrator.config import OrchestratorConfig

config = OrchestratorConfig(
    redis_host="localhost",
    redis_port=6379,
    max_concurrent_tasks=10,
    scheduler_interval_seconds=1,
    budget_check_enabled=True
)

orchestrator = await OrchestratorFactory.create(
    blackboard,
    event_bus,
    config
)
```

## 工作流程

### 事件处理流程

```
Event -> Orchestrator.handle_event()
  ├─> 检查项目是否暂停
  ├─> 检查是否需要审批
  ├─> 映射事件到任务
  ├─> 检查预算
  └─> 添加到任务队列
```

### 任务调度流程

```
Orchestrator.dispatch_tasks()
  ├─> 获取待处理任务
  ├─> 检查依赖
  ├─> 获取锁
  ├─> 分发任务给 Agent
  └─> 检查超时
```

## 审批检查点

默认的 4 个审批检查点：

1. **SCENE_WRITTEN**: 剧本完成后审批
2. **SHOT_PLANNED**: 分镜规划后审批
3. **PREVIEW_VIDEO_READY**: 预览视频完成后审批
4. **FINAL_VIDEO_READY**: 最终视频完成后审批

## 数据库 Schema

### tasks 表

存储所有任务：

```sql
CREATE TABLE tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority INTEGER NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    dependencies JSONB DEFAULT '[]',
    estimated_cost DECIMAL(10, 4),
    actual_cost DECIMAL(10, 4),
    created_at TIMESTAMP NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);
```

## License

MIT
