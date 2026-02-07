# PromptEngineer Agent

PromptEngineer Agent 是 LivingAgentPipeline v2.0 的第一个 Agent 层组件，负责生成高质量的 AI 图像/视频生成 prompts。

## 核心功能

✅ **模板库管理**: 基于 JSON 的模板系统
✅ **智能模板选择**: 根据镜头类型和情绪标签自动选择最佳模板
✅ **Prompt 组合**: 变量填充、清理和优化
✅ **DNA Token 注入**: 自动从 DNA Bank 提取视觉一致性特征
✅ **Negative Prompt 管理**: 根据质量档位和镜头类型生成
✅ **质量档位支持**: DRAFT/STANDARD/HIGH/PREMIUM

## 快速开始

### 基础使用

```python
from src.agents.prompt_engineer import PromptEngineer
from src.infrastructure.blackboard import SharedBlackboard
from src.infrastructure.event_bus import EventBus

# 初始化
blackboard = SharedBlackboard()
event_bus = EventBus()

engineer = PromptEngineer(blackboard, event_bus)

# 启动
await engineer.start()

# 生成 prompt
prompt_config = engineer.create_prompt_config(
    shot=shot_data,
    project_id="PROJ-001",
    global_spec=global_spec,
    quality_tier="HIGH"
)

print(prompt_config["positive"])
print(prompt_config["negative"])
```

## 架构

### 组件结构

```
src/agents/prompt_engineer/
├── __init__.py              # 模块导出
├── prompt_engineer.py       # 核心 Agent (220+ 行) ✅
├── template_library.py      # 模板库管理 (200+ 行) ✅
├── prompt_composer.py       # Prompt 组合器 (200+ 行) ✅
├── dna_injector.py          # DNA Token 注入器 (100+ 行) ✅
├── negative_manager.py      # Negative 管理器 (100+ 行) ✅
└── templates/               # 模板文件目录
    ├── character_portrait.json ✅
    ├── action_scene.json ✅
    ├── environment_establishing.json ✅
    └── README.md ✅
```

### 工作流程

```
Event (KEYFRAME_REQUESTED)
    ↓
PromptEngineer.handle_event()
    ↓
1. 获取 Shot 数据
2. 提取 DNA Tokens (DNAInjector)
3. 选择模板 (TemplateLibrary)
4. 组合 Prompt (PromptComposer)
5. 生成 Negative (NegativeManager)
6. 保存到 Blackboard
    ↓
Event (PROMPT_GENERATED)
```

## 模板系统

### 模板结构

每个模板包含：
- **base_prompt**: 基础 prompt 模板
- **variables**: 可填充变量列表
- **quality_modifiers**: 质量档位修饰符
- **negative_prompt**: 默认 negative prompt
- **default_params**: 默认生成参数

### 示例模板

```json
{
  "template_id": "character_portrait",
  "base_prompt": "{character_signature}, {character_face}, {expression}",
  "quality_modifiers": {
    "HIGH": ", ultra realistic, 8k, photorealistic"
  },
  "negative_prompt": "blurry, distorted, multiple faces"
}
```

## DNA Token 注入

自动从 DNA Bank 提取：
- **appearance_tokens**: 外观特征
- **style_tokens**: 风格特征
- **置信度过滤**: 仅使用 confidence >= 0.6 的 tokens

## 事件处理

### 监听事件

- **KEYFRAME_REQUESTED**: 生成 keyframe prompt
- **DNA_BANK_UPDATED**: 更新角色 tokens

### 发布事件

- **PROMPT_GENERATED**: Prompt 生成完成

## 配置

### 质量档位

- **DRAFT**: 快速生成，基础质量
- **STANDARD**: 标准质量 + "highly detailed, 4k"
- **HIGH**: 高质量 + "ultra realistic, 8k, photorealistic"
- **PREMIUM**: 顶级 + "masterpiece, ultra detailed, 8k uhd"

## 扩展

### 添加新模板

1. 在 `templates/` 目录创建 JSON 文件
2. 遵循标准模板结构
3. 重启 Agent 自动加载

### 自定义 Negative Prompts

```python
engineer.negative_manager.add_custom_negatives([
    "custom negative 1",
    "custom negative 2"
])
```

## License

MIT
