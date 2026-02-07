# ChefAgent - 总监 Agent

ChefAgent 是 LivingAgentPipeline 系统的总监 Agent，负责项目全局决策和预算控制。

## 概述

ChefAgent 作为系统的"大脑"，协调整个视频生成流程，确保项目在预算范围内高质量完成。

### 核心职责

1. **预算管理**: 根据项目规格分配预算，实时监控预算使用情况
2. **策略调整**: 根据预算使用情况动态调整项目策略（如降低质量档位）
3. **失败评估**: 评估任务失败情况，决定是否需要人工介入
4. **人工决策处理**: 处理人工审批结果，恢复或终止项目
5. **项目完成确认**: 验证项目完成，进行成本核算和质量验收

## 架构

### 组件结构

```
ChefAgent
├── BudgetManager       # 预算管理器
├── StrategyAdjuster    # 策略调整器
├── FailureEvaluator    # 失败评估器
├── HumanGate          # 人工介入管理器
├── ProjectValidator   # 项目验证器
└── EventManager       # 事件管理器
```

### 事件订阅

ChefAgent 订阅以下事件类型：

- `PROJECT_CREATED`: 项目创建事件
- `CONSISTENCY_FAILED`: 一致性检查失败事件
- `COST_OVERRUN_WARNING`: 预算预警事件
- `USER_APPROVED`: 用户批准事件
- `USER_REVISION_REQUESTED`: 用户请求修订事件
- `USER_REJECTED`: 用户拒绝事件
- `PROJECT_FINALIZED`: 项目完成事件
- `IMAGE_GENERATED`: 图像生成事件（用于预算监控）
- `VIDEO_GENERATED`: 视频生成事件（用于预算监控）
- `MUSIC_COMPOSED`: 音乐生成事件（用于预算监控）
- `VOICE_RENDERED`: 语音生成事件（用于预算监控）

## 使用方法

### 基本使用

```python
from src.agents.chef_agent import ChefAgent
from src.agents.chef_agent.models import Event, EventType
import asyncio

async def main():
    # 创建 ChefAgent 实例
    agent = ChefAgent()
    
    # 处理项目创建事件
    event = Event(
        event_id="evt_001",
        project_id="proj_001",
        event_type=EventType.PROJECT_CREATED,
        actor="Orchestrator",
        payload={
            "duration": 30.0,
            "quality_tier": "balanced"
        },
        timestamp="2024-01-01T00:00:00"
    )
    
    await agent.handle_event(event)
    
    # 处理成本事件
    cost_event = Event(
        event_id="evt_002",
        project_id="proj_001",
        event_type=EventType.IMAGE_GENERATED,
        actor="ImageAgent",
        payload={},
        timestamp="2024-01-01T00:01:00",
        cost=Money(amount=10.0, currency="USD")
    )
    
    await agent.handle_event(cost_event)

if __name__ == "__main__":
    asyncio.run(main())
```

### 自定义配置

```python
from src.agents.chef_agent import ChefAgent, ChefAgentConfig
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建自定义配置
config = ChefAgentConfig(
    agent_name="ChefAgent-Production",
    base_budget_per_second=5.0,
    budget_warning_threshold=0.75,
    budget_exceeded_threshold=0.95,
    max_retry_count=5,
    max_retries=5,
    initial_retry_delay=2.0,
    retry_backoff_factor=2.0,
    cost_impact_threshold=30.0,
    human_gate_timeout_minutes=120
)

# 使用自定义配置和日志创建 Agent
agent = ChefAgent(config=config, logger=logger)
```

### 环境变量配置

ChefAgent 支持通过环境变量配置：

```bash
# Agent 配置
export CHEF_AGENT_NAME=ChefAgent-Production

# 预算配置
export CHEF_BASE_BUDGET_PER_SECOND=3.0
export CHEF_QUALITY_MULTIPLIER_HIGH=1.5
export CHEF_QUALITY_MULTIPLIER_BALANCED=1.0
export CHEF_QUALITY_MULTIPLIER_FAST=0.6

# 预算预警阈值
export CHEF_BUDGET_WARNING_THRESHOLD=0.8
export CHEF_BUDGET_EXCEEDED_THRESHOLD=1.0

# 失败评估配置
export CHEF_MAX_RETRY_COUNT=3
export CHEF_COST_IMPACT_THRESHOLD=20.0

# 错误恢复配置
export CHEF_MAX_RETRIES=3
export CHEF_INITIAL_RETRY_DELAY=1.0
export CHEF_RETRY_BACKOFF_FACTOR=2.0

# 人工介入配置
export CHEF_HUMAN_GATE_TIMEOUT_MINUTES=60
```

### 完整示例：处理项目生命周期

```python
from src.agents.chef_agent import ChefAgent
from src.agents.chef_agent.models import Event, EventType, Money
import asyncio
from datetime import datetime

async def handle_project_lifecycle():
    """处理完整的项目生命周期"""
    agent = ChefAgent()
    
    # 1. 创建项目
    print("1. Creating project...")
    create_event = Event(
        event_id="evt_001",
        project_id="proj_demo",
        event_type=EventType.PROJECT_CREATED,
        actor="Orchestrator",
        payload={
            "duration": 60.0,
            "quality_tier": "high"
        },
        timestamp=datetime.now().isoformat()
    )
    await agent.handle_event(create_event)
    print("   ✓ Project created with budget: $270.00")
    
    # 2. 处理成本事件
    print("\n2. Processing cost events...")
    for i in range(5):
        cost_event = Event(
            event_id=f"evt_cost_{i}",
            project_id="proj_demo",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageAgent",
            payload={},
            timestamp=datetime.now().isoformat(),
            cost=Money(amount=40.0, currency="USD")
        )
        await agent.handle_event(cost_event)
        print(f"   ✓ Processed cost event {i+1}: $40.00")
    
    # 3. 检查预算状态
    project_data = agent._project_cache.get("proj_demo")
    budget = project_data["budget"]
    usage_rate = budget.spent.amount / budget.total.amount
    print(f"\n3. Budget status:")
    print(f"   Spent: ${budget.spent.amount:.2f}")
    print(f"   Total: ${budget.total.amount:.2f}")
    print(f"   Usage: {usage_rate*100:.1f}%")
    
    # 4. 完成项目
    print("\n4. Finalizing project...")
    finalized_event = Event(
        event_id="evt_finalized",
        project_id="proj_demo",
        event_type=EventType.PROJECT_FINALIZED,
        actor="Orchestrator",
        payload={
            "shots": {
                "shot_001": {"status": "FINAL_RENDERED"},
                "shot_002": {"status": "FINAL_RENDERED"}
            },
            "artifacts": {
                "artifact_001": {"cost": {"amount": 100.0, "currency": "USD"}},
                "artifact_002": {"cost": {"amount": 100.0, "currency": "USD"}}
            }
        },
        timestamp=datetime.now().isoformat()
    )
    await agent.handle_event(finalized_event)
    
    # 5. 查看项目总结
    project_data = agent._project_cache.get("proj_demo")
    summary = project_data["summary"]
    print(f"\n5. Project summary:")
    print(f"   Status: {project_data['status']}")
    print(f"   Total cost: ${summary.total_cost.amount:.2f}")
    print(f"   Budget compliant: {summary.budget_compliance.is_compliant}")
    print(f"   Shots count: {summary.shots_count}")

if __name__ == "__main__":
    asyncio.run(handle_project_lifecycle())
```

## 事件处理流程

### 1. PROJECT_CREATED 事件

```
PROJECT_CREATED
    ↓
分配预算
    ↓
写入 Blackboard
    ↓
发布 BUDGET_ALLOCATED 事件
```

### 2. 成本事件（IMAGE_GENERATED, VIDEO_GENERATED 等）

```
成本事件
    ↓
更新预算使用情况
    ↓
检查预算状态
    ↓
├─ 使用率 >= 100% → 发布 BUDGET_EXCEEDED 事件
├─ 使用率 >= 80%  → 发布 COST_OVERRUN_WARNING 事件
└─ 使用率 < 80%   → 无操作
```

### 3. CONSISTENCY_FAILED 事件

```
CONSISTENCY_FAILED
    ↓
评估失败情况
    ↓
├─ 重试次数 >= 3 次      → 触发 HUMAN_GATE
├─ 成本影响 > $20        → 触发 HUMAN_GATE
├─ 严重程度 = critical   → 触发 HUMAN_GATE
└─ 其他情况              → AUTO_RETRY
```

### 4. 人工决策事件

```
USER_APPROVED
    ↓
恢复项目执行

USER_REVISION_REQUESTED
    ↓
创建修订任务

USER_REJECTED
    ↓
标记项目为失败
```

### 5. PROJECT_FINALIZED 事件

```
PROJECT_FINALIZED
    ↓
验证项目完成
    ↓
计算总成本
    ↓
检查预算合规性
    ↓
生成总结报告
    ↓
发布 PROJECT_DELIVERED 事件
```

## 预算管理

### 预算分配公式

```
基准预算 = duration * base_budget_per_second
质量乘数 = {
    "high": 1.5,
    "balanced": 1.0,
    "fast": 0.6
}
总预算 = 基准预算 * 质量乘数
```

### 预算状态

- **OK**: 使用率 < 80%
- **WARNING**: 使用率 >= 80%
- **EXCEEDED**: 使用率 >= 100%

### 默认成本估算

当事件不包含成本信息时，使用以下默认值：

- 图像生成: $0.05
- 视频生成: $0.50/秒
- 音乐生成: $0.02/秒
- 语音生成: $0.02/秒

## 失败评估

### 触发 HUMAN_GATE 的条件

1. 重试次数达到 3 次
2. 成本影响超过 $20
3. 严重程度为 critical

### 自动重试条件

- 重试次数 < 3 次
- 成本影响 <= $20
- 严重程度不是 critical

## 错误恢复策略

ChefAgent 实现了三层错误恢复策略，确保系统的可靠性和可用性。

### Level 1: 自动重试（90% 场景）

**触发条件**:
- 临时网络错误
- API 超时
- 可恢复的业务逻辑错误

**处理策略**:
- 使用指数退避策略重试（最多 3 次）
- 初始延迟: 1.0 秒
- 退避因子: 2.0（每次重试延迟翻倍）

**示例**:
```python
# ChefAgent 自动处理重试
async def handle_event_with_retry():
    result = await agent.retry_with_backoff(
        func=some_operation,
        max_retries=3,
        initial_delay=1.0
    )
```

### Level 2: 策略降级（9% 场景）

**触发条件**:
- Level 1 重试失败
- 预算不足
- 质量要求可降低

**处理策略**:
- 降低质量档位（high → balanced → fast）
- 发布 STRATEGY_UPDATE 事件
- 更新 Blackboard 中的质量配置

**示例**:
```python
# 预算不足时自动降级
error = Exception("Budget exceeded")
context = {
    "project_id": "proj_001",
    "budget": budget
}

result = await agent.handle_with_fallback(error, context)
# result["action"] == "QUALITY_REDUCED"
# result["new_tier"] == "balanced"
```

### Level 3: 人工介入（1% 场景）

**触发条件**:
- Level 2 降级失败
- 关键质量指标不达标
- 成本影响超过阈值

**处理策略**:
- 创建 HumanGateRequest
- 发布 HUMAN_GATE_TRIGGERED 事件
- 暂停项目执行
- 等待人工决策

**示例**:
```python
# 升级到人工介入
await agent.escalate_to_human(
    error=error,
    context={
        "project_id": "proj_001",
        "event_id": "evt_001",
        "retry_count": 3
    }
)
```

## 故障排查

### 常见问题

#### 1. 预算分配失败

**症状**: 项目创建后没有预算信息

**可能原因**:
- 配置错误（base_budget_per_second 未设置）
- 项目时长或质量档位无效

**解决方法**:
```python
# 检查配置
config = ChefAgentConfig()
print(f"Base budget: {config.base_budget_per_second}")

# 验证项目参数
assert duration > 0
assert quality_tier in ["high", "balanced", "fast"]
```

#### 2. 事件未被处理

**症状**: 发送事件后没有响应

**可能原因**:
- 事件类型未订阅
- 项目 ID 不存在
- 事件格式错误

**解决方法**:
```python
# 检查事件订阅
subscribed = agent.get_subscribed_events()
print(f"Subscribed events: {[e.value for e in subscribed]}")

# 验证事件格式
assert event.event_id is not None
assert event.project_id is not None
assert event.event_type in subscribed
```

#### 3. 人工介入超时

**症状**: 人工介入请求长时间未处理

**可能原因**:
- 超时时间设置过短
- Admin CLI 未正确配置
- 事件总线连接失败

**解决方法**:
```python
# 调整超时时间
config = ChefAgentConfig(
    human_gate_timeout_minutes=120  # 增加到 2 小时
)

# 检查人工介入请求状态
request = project_data.get("human_gate_request")
if request:
    is_timeout = agent.human_gate.check_timeout(request)
    print(f"Request timeout: {is_timeout}")
```

#### 4. 预算计算不准确

**症状**: 预算使用率与实际不符

**可能原因**:
- 成本事件缺少 cost 字段
- 默认成本估算不准确
- 预算更新逻辑错误

**解决方法**:
```python
# 确保成本事件包含 cost 字段
cost_event = Event(
    event_id="evt_001",
    project_id="proj_001",
    event_type=EventType.IMAGE_GENERATED,
    actor="ImageAgent",
    payload={},
    timestamp=datetime.now().isoformat(),
    cost=Money(amount=10.0, currency="USD")  # 明确指定成本
)

# 检查预算状态
project_data = agent._project_cache.get("proj_001")
budget = project_data["budget"]
print(f"Spent: ${budget.spent.amount:.2f}")
print(f"Total: ${budget.total.amount:.2f}")
```

### 调试技巧

#### 启用详细日志

```python
import logging

# 设置日志级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 创建 Agent
agent = ChefAgent()
```

#### 检查项目缓存

```python
# 查看所有项目
for project_id, project_data in agent._project_cache.items():
    print(f"Project: {project_id}")
    print(f"  Status: {project_data['status']}")
    print(f"  Budget: ${project_data['budget'].spent.amount:.2f} / ${project_data['budget'].total.amount:.2f}")
    print(f"  Quality: {project_data['quality_tier']}")
```

#### 查看已发布的事件

```python
# 获取已发布的事件
events = agent.event_manager.get_published_events()
for event in events:
    print(f"Event: {event.event_type.value}")
    print(f"  Project: {event.project_id}")
    print(f"  Timestamp: {event.timestamp}")
```

## Admin CLI 工具

ChefAgent 提供了一个命令行工具（Admin CLI），用于在开发环境中模拟人工决策流程。

### 安装

Admin CLI 工具位于 `tools/admin_cli.py`，无需额外安装。

### 使用方法

#### 1. 查看待审批项目列表

```bash
python tools/admin_cli.py list
```

输出示例：
```
Pending Human Gate Requests:
1. Project: proj_001
   Request ID: req_001
   Reason: Max retries exceeded
   Created: 2024-01-01 10:00:00
   Budget: $50.00 / $90.00 (55.6%)
```

#### 2. 查看项目详情

```bash
python tools/admin_cli.py status proj_001
```

输出示例：
```
Project Status: proj_001
Status: PAUSED
Budget: $50.00 / $90.00 (55.6%)
Quality Tier: balanced
Duration: 30.0s

Human Gate Request:
  Request ID: req_001
  Reason: Max retries exceeded
  Created: 2024-01-01 10:00:00
  Status: PENDING
```

#### 3. 批准项目

```bash
python tools/admin_cli.py approve proj_001 --notes "Looks good, proceed"
```

这将发布 `USER_APPROVED` 事件，ChefAgent 会恢复项目执行。

#### 4. 拒绝项目

```bash
python tools/admin_cli.py reject proj_001 --notes "Quality issues cannot be resolved"
```

这将发布 `USER_REJECTED` 事件，ChefAgent 会标记项目为失败状态。

#### 5. 请求修订

```bash
python tools/admin_cli.py revise proj_001 --notes "Please adjust the quality parameters"
```

这将发布 `USER_REVISION_REQUESTED` 事件，ChefAgent 会创建修订任务。

### Admin CLI 命令参考

| 命令 | 描述 | 参数 |
|------|------|------|
| `list` | 显示所有待审批项目 | 无 |
| `status <project_id>` | 显示项目详情 | `project_id`: 项目 ID |
| `approve <project_id>` | 批准项目 | `project_id`: 项目 ID<br>`--notes`: 批准备注（可选） |
| `reject <project_id>` | 拒绝项目 | `project_id`: 项目 ID<br>`--notes`: 拒绝原因（可选） |
| `revise <project_id>` | 请求修订 | `project_id`: 项目 ID<br>`--notes`: 修订说明（可选） |

### 配置 Admin CLI

Admin CLI 使用环境变量配置事件总线连接：

```bash
# 事件总线配置
export EVENT_BUS_URL=http://localhost:8080
export EVENT_BUS_API_KEY=your_api_key
```

### 在开发环境中使用

在开发环境中，Admin CLI 是测试人工决策流程的主要工具：

1. 启动 ChefAgent
2. 触发失败事件（例如，通过集成测试）
3. 使用 `admin_cli.py list` 查看待审批项目
4. 使用 `admin_cli.py approve/reject/revise` 处理人工决策
5. 观察 ChefAgent 的响应

### 示例工作流程

```bash
# 1. 查看待审批项目
python tools/admin_cli.py list

# 2. 查看项目详情
python tools/admin_cli.py status proj_001

# 3. 批准项目
python tools/admin_cli.py approve proj_001 --notes "Approved after review"

# 4. 验证项目已恢复
python tools/admin_cli.py status proj_001
```

## 测试

### 运行单元测试

```bash
# 运行所有单元测试
python -m pytest src/agents/chef_agent/tests/test_agent.py -v

# 运行特定测试类
python -m pytest src/agents/chef_agent/tests/test_agent.py::TestChefAgentInitialization -v

# 运行特定测试方法
python -m pytest src/agents/chef_agent/tests/test_agent.py::TestChefAgentInitialization::test_initialization_with_default_config -v
```

### 运行集成测试

```bash
# 运行所有集成测试
python -m pytest src/agents/chef_agent/tests/test_integration.py -v

# 运行特定测试类
python -m pytest src/agents/chef_agent/tests/test_integration.py::TestBudgetManagementWorkflow -v
```

### 运行属性基测试

```bash
# 运行所有属性基测试
python -m pytest src/agents/chef_agent/tests/ -k "property" -v

# 运行特定属性测试
python -m pytest src/agents/chef_agent/tests/test_budget_manager.py::test_property_budget_allocation_consistency -v
```

### 运行所有测试

```bash
# 运行所有测试并显示覆盖率
python -m pytest src/agents/chef_agent/tests/ -v --cov=src/agents/chef_agent --cov-report=html

# 运行所有测试（快速模式）
python -m pytest src/agents/chef_agent/tests/ -v -x
```

### 运行示例

```bash
# 运行 ChefAgent 示例
python examples/chef_agent_example.py

# 运行指标收集示例
python examples/metrics_collector_example.py
```

## 开发规范

### 代码风格

- 使用 Black 格式化代码
- 使用 Flake8 检查代码质量
- 使用 mypy 进行类型检查

### 测试要求

- 单元测试覆盖率 >= 80%
- 所有属性基测试必须通过
- 集成测试覆盖关键流程

## 依赖

- Python >= 3.8
- Pydantic >= 2.0
- pytest >= 7.0
- pytest-asyncio >= 0.21

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请联系开发团队。
