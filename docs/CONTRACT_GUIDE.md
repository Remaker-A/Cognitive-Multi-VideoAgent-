# 契约遵守开发指南

本文档说明如何在开发中遵守 `contracts` 目录中定义的契约规范。

## 快速开始

### 1. 导入契约模型

```python
from src.contracts import (
    EventType,
    TaskType,
    Money,
    create_event,
    create_task,
    create_blackboard_request,
)
```

### 2. 创建符合契约的事件

```python
event = create_event(
    event_id="evt_001",
    project_id="proj_001",
    event_type=EventType.IMAGE_GENERATED,
    actor="ImageGeneratorAgent",
    payload={"image_url": "s3://bucket/image.png"},
    cost=Money(amount=0.05, currency="USD"),
    latency_ms=1500,
)
```

### 3. 创建符合契约的任务

```python
task = create_task(
    task_id="task_001",
    task_type=TaskType.GENERATE_KEYFRAME,
    assigned_to="ImageGeneratorAgent",
    input_data={"prompt": "A beautiful sunset"},
    priority=3,
    estimated_cost=Money(amount=0.10, currency="USD"),
)
```

## 核心原则

### ✅ 必须遵守

1. **使用 Pydantic 模型**: 所有事件、任务、RPC 请求都使用 `src/contracts/models.py` 中定义的模型
2. **包含所有必需字段**: 不得省略契约中定义的必需字段
3. **使用正确的枚举值**: 事件类型、任务类型等必须使用枚举中定义的值
4. **维护因果链**: 事件应包含 `causation_id` 链接到触发它的事件
5. **记录成本和延迟**: 在事件元数据中记录操作成本和延迟

### ❌ 禁止操作

1. **不要手动构造字典**: 使用辅助函数 `create_event()`, `create_task()` 等
2. **不要使用未定义的枚举值**: 所有枚举值必须在契约中定义
3. **不要跳过验证**: 在边界处（API、事件发布）必须验证数据
4. **不要破坏因果链**: 确保 `causation_id` 正确链接

## 工具使用

### 契约验证脚本

验证 JSON 数据是否符合契约：

```bash
python scripts/validate_contracts.py --type event --data event.json
python scripts/validate_contracts.py --type task --data task.json
```

### 运行测试

```bash
# 运行契约遵守测试
pytest tests/test_contract_compliance.py -v

# 运行所有测试
pytest tests/ -v
```

### 查看示例

```bash
# 运行契约使用示例
python examples/contract_usage_examples.py
```

## 常见场景

### 场景 1: 发布事件

```python
from src.contracts import EventType, create_event, Money

# 创建事件
event = create_event(
    event_id=generate_id(),
    project_id=project_id,
    event_type=EventType.KEYFRAME_REQUESTED,
    actor="OrchestratorAgent",
    payload={"shot_id": "S01"},
    causation_id=previous_event_id,  # 链接因果链
    blackboard_pointer="/projects/proj_001/shots/S01",
)

# 发布到事件总线
event_bus.publish(event.dict())
```

### 场景 2: 创建任务

```python
from src.contracts import TaskType, create_task, Money

# 创建任务
task = create_task(
    task_id=generate_id(),
    task_type=TaskType.GENERATE_KEYFRAME,
    assigned_to="ImageGeneratorAgent",
    input_data={
        "shot_id": "S01",
        "prompt": "探险家走进森林",
    },
    priority=4,
    dependencies=[],  # 无依赖
    estimated_cost=Money(amount=0.10, currency="USD"),
    causation_event_id=event.event_id,
)

# 保存到数据库
task_repository.save(task.dict())
```

### 场景 3: Blackboard RPC 调用

```python
from src.contracts import create_blackboard_request, create_blackboard_response

# 创建请求
request = create_blackboard_request(
    request_id=generate_id(),
    method="get_project",
    params={"project_id": "proj_001"},
)

# 发送请求
response_data = blackboard_client.call(request.dict())

# 解析响应
if response_data["ok"]:
    result = response_data["result"]
else:
    error = response_data["error"]
    raise Exception(f"{error['code']}: {error['message']}")
```

### 场景 4: 任务依赖管理

```python
# 任务 1: 生成关键帧
task1 = create_task(
    task_id="task_001",
    task_type=TaskType.GENERATE_KEYFRAME,
    assigned_to="ImageGeneratorAgent",
    input_data={"shot_id": "S01"},
)

# 任务 2: QA（依赖任务 1）
task2 = create_task(
    task_id="task_002",
    task_type=TaskType.RUN_VISUAL_QA,
    assigned_to="QAAgent",
    input_data={"shot_id": "S01"},
    dependencies=[task1.task_id],  # 依赖关系
)

# 任务 3: 生成视频（依赖任务 2）
task3 = create_task(
    task_id="task_003",
    task_type=TaskType.GENERATE_PREVIEW_VIDEO,
    assigned_to="VideoGeneratorAgent",
    input_data={"shot_id": "S01"},
    dependencies=[task2.task_id],
)
```

## 契约文件位置

- **契约定义**: `d:\下载\contracts\contracts\`
- **Pydantic 模型**: `d:\文档\Kiro\VIdeoGen\src\contracts\models.py`
- **验证脚本**: `d:\文档\Kiro\VIdeoGen\scripts\validate_contracts.py`
- **测试用例**: `d:\文档\Kiro\VIdeoGen\tests\test_contract_compliance.py`
- **使用示例**: `d:\文档\Kiro\VIdeoGen\examples\contract_usage_examples.py`

## 参考资料

- [实施计划](file:///C:/Users/29989/.gemini/antigravity/brain/8fdb3456-3fe6-4d71-b2b5-70a2bf3e20ef/implementation_plan.md)
- [Contracts README](file:///D:/%E4%B8%8B%E8%BD%BD/contracts/contracts/README.md)
- [Pydantic 文档](https://docs.pydantic.dev/)
- [JSON Schema 规范](https://json-schema.org/)
