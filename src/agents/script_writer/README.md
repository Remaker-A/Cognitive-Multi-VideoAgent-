# ScriptWriter Agent

ScriptWriter Agent 是 LivingAgentPipeline v2.0 的剧本编写组件，负责将用户需求转化为结构化的视频剧本。

## 核心功能

✅ **LLM 集成**: 支持 OpenAI 和 Claude API
✅ **多阶段生成**: Outline → Detailed Script
✅ **智能 Shot 分解**: 自动分解场景为 3-7 秒的 shots
✅ **情绪标注**: 自动标注每个 shot 的情绪和氛围
✅ **可行性检查**: 自动评估视觉可实现性
✅ **自动重写**: 可行性 < 0.28 时自动重写（最多 3 次）
✅ **用户修改处理**: 基于用户反馈智能修改剧本

## 快速开始

### 基础使用

```python
from src.agents.script_writer import ScriptWriter
from src.infrastructure.blackboard import SharedBlackboard
from src.infrastructure.event_bus import EventBus

# 初始化
blackboard = SharedBlackboard()
event_bus = EventBus()

writer = ScriptWriter(blackboard, event_bus, llm_provider="openai")

# 启动
await writer.start()

# 编写剧本会自动响应 PROJECT_CREATED 事件
```

## 架构

### 组件结构

```
src/agents/script_writer/
├── __init__.py              # 模块导出
├── script_writer.py         # 核心 Agent (200+ 行) ✅
├── llm_client.py            # LLM 客户端 (150+ 行) ✅
├── script_generator.py      # 剧本生成器 (400+ 行) ✅
├── shot_decomposer.py       # Shot 分解器 (180+ 行) ✅
├── emotion_tagger.py        # 情绪标注器 (100+ 行) ✅
└── README.md                # 使用文档 ✅
```

### 工作流程

```
PROJECT_CREATED Event
    ↓
1. Generate Outline (LLM)
    ↓
2. Generate Detailed Script (LLM)
    ↓
3. Check Feasibility
    ↓ (< 0.28)
4. Auto Rewrite (max 3 times)
    ↓
5. Decompose into Shots
    ↓
6. Tag Emotions
    ↓
7. Save to Blackboard
    ↓
SCENE_WRITTEN Event
```

## 优化版剧本生成机制

### 多阶段生成

**阶段 1: 生成大纲**
- 简短的场景列表
- 粗略的时长估算
- 视觉化的场景描述

**阶段 2: 详细剧本**
- 基于大纲生成详细内容
- 结构化 JSON 输出
- 每个 shot 包含完整信息

**阶段 3: 可行性检查**
- 描述具体性检查
- Shot 时长合理性
- 视觉可实现性评估
- 结构完整性验证

**阶段 4: 后处理优化**
- 标准化 ID
- 补充缺失字段
- 调整总时长

### 可行性评分系统

```python
评分标准：
- 描述长度 < 20: -0.1
- 包含抽象词汇: -0.05
- 时长异常 (< 2s 或 > 10s): -0.05
- 缺少必要字段: -0.03

阈值: 0.28
- >= 0.28: 通过
- < 0.28: 自动重写（最多 3 次）
```

## 剧本结构

### JSON 格式

```json
{
  "title": "视频标题",
  "total_duration": 30,
  "scenes": [
    {
      "scene_id": "S001",
      "description": "场景描述",
      "duration_estimate": 10,
      "environment": "环境描述",
      "characters": ["角色名"],
      "shots": [
        {
          "shot_id": "S001_001",
          "description": "详细的视觉描述",
          "duration": 5,
          "characters": ["角色名"],
          "mood_tags": ["happy", "peaceful"],
          "mood_intensity": "moderate",
          "dialogue": "对话内容",
          "type": "character_portrait"
        }
      ]
    }
  ]
}
```

## Shot 分解算法

### 智能分解策略

1. **按句子分割**: 基于句号、问号、感叹号
2. **时长检查**: 
   - 太短 (< 3s): 合并句子
   - 太长 (> 7s): 拆分句子
3. **类型推断**: 自动推断 shot 类型
4. **对话提取**: 提取引号中的对话

### Shot 类型

- `character_portrait`: 角色特写
- `action_scene`: 动作场景
- `environment_establishing`: 环境展示
- `dialogue`: 对话场景
- `general`: 一般镜头

## 情绪标注

### 支持的情绪标签

- happy, sad, angry, calm
- tense, excited, mysterious
- romantic, dramatic, nostalgic
- neutral (默认)

### 情绪强度

- `subtle`: 微妙
- `moderate`: 适中
- `intense`: 强烈

## 事件处理

### 监听事件

- **PROJECT_CREATED**: 开始编写剧本
- **REWRITE_SCENE**: 重写特定场景

### 发布事件

- **SCENE_WRITTEN**: 剧本编写完成

## 配置

### 环境变量

```bash
# OpenAI
export OPENAI_API_KEY=your_key_here

# Claude
export ANTHROPIC_API_KEY=your_key_here
```

### LLM 设置

```python
# 使用 OpenAI
writer = ScriptWriter(blackboard, event_bus, llm_provider="openai")

# 使用 Claude
writer = ScriptWriter(blackboard, event_bus, llm_provider="claude")
```

## 用户修改处理

```python
# 处理用户修改请求
await writer.handle_user_revision({
    "project_id": "PROJ-001",
    "revision_notes": "Make the opening scene more dramatic"
})
```

## License

MIT
