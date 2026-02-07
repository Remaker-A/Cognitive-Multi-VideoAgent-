# ConsistencyGuardian Agent

ConsistencyGuardian Agent 负责视觉一致性检测、质量保证和自动修复。

## 核心功能

✅ **CLIP 相似度检测**: 图像间视觉相似度
✅ **面部一致性检测**: 同一角色的面部识别
✅ **色彩一致性检测**: 色彩风格一致性
✅ **光流流畅度检测**: 视频运动流畅度
✅ **跨 Shot 连贯性检测**: 相邻镜头连贯性
✅ **三层自动修复策略**: Prompt Tuning / Model Switch / HumanGate (NEW)
✅ **动态阈值管理**: 基于质量档位和镜头类型

## 快速开始

```python
from src.agents.consistency_guardian import ConsistencyGuardian

agent = ConsistencyGuardian(blackboard, event_bus)
await agent.start()
```

## 组件结构

```
src/agents/consistency_guardian/
├── consistency_guardian.py  # 核心 Agent (290+ 行) ✅
├── threshold_manager.py     # 动态阈值 (100+ 行) ✅
├── clip_detector.py         # CLIP 检测 (120+ 行) ✅
├── face_detector.py         # 面部检测 (70+ 行) ✅
├── palette_detector.py      # 色彩检测 (150+ 行) ✅
├── flow_detector.py         # 光流检测 (100+ 行) ✅
├── lighting_detector.py     # 光照检测 (100+ 行) ✅
├── continuity_checker.py    # 连贯性检查 (140+ 行) ✅
├── auto_fix_strategy.py     # 自动修复 (300+ 行) ✅ NEW
└── README.md                # 文档 ✅
```

## 三层自动修复策略

### Level 1: Prompt Tuning（轻量级）

**触发条件**: 质量分数 >= 0.60

**操作**:
- 调整 CFG scale
- 增加 negative prompts
- 调整权重

**重试次数**: 最多 2 次

**成本**: 低

**示例**:
```python
{
    "cfg_scale": 8.5,
    "negative_prompts": ["inconsistent_style", "different_face"],
    "weight_adjustments": {
        "character_consistency": 1.3,
        "color_palette": 1.2
    }
}
```

### Level 2: Model Switch / Quality Downgrade（中等）

**触发条件**: 
- Level 1 失败
- 质量分数 >= 0.40

**操作**:
- **Model Switch**: 切换到备用模型
  - SDXL → DALL-E 3
  - Runway → Pika
- **Quality Downgrade**: 降低质量档位
  - ULTRA → HIGH → STANDARD → PREVIEW

**重试次数**: 最多 1 次

**成本**: 中等

**决策逻辑**:
- 视觉质量问题 → Model Switch
- 其他问题 → Quality Downgrade

### Level 3: HumanGate（重量级）

**触发条件**:
- Level 2 失败
- 质量分数 < 0.40
- 关键任务失败

**操作**:
- 暂停流程
- 发布 HUMAN_GATE_TRIGGERED 事件
- 等待人工决策

**成本**: 高（人工成本）

## 决策流程

```
QA Failed
    ↓
Score >= 0.60?
    ↓ Yes
Level 1: Prompt Tuning
    ↓ Failed
Score >= 0.40?
    ↓ Yes
Level 2: Model Switch / Downgrade
    ↓ Failed
Level 3: HumanGate
```

## 使用示例

### 自动修复

```python
# QA 检测失败后自动修复
qa_results = {
    "overall_score": 0.55,
    "checks": {
        "clip_similarity": {"score": 0.50, "passed": False}
    }
}

context = {
    "shot_id": "S001_001",
    "model": "sdxl-1.0",
    "quality_tier": "STANDARD"
}

fix_result = await guardian.auto_fix_strategy.auto_fix(
    project_id="PROJ-001",
    qa_results=qa_results,
    context=context
)

# 结果
{
    "success": True,
    "fix_level": 2,
    "fix_type": "model_switch",
    "fix_action": {
        "action": "model_switch",
        "from_model": "sdxl-1.0",
        "to_model": "dalle3"
    }
}
```

## 事件发布

### AUTO_FIX_REQUEST
```python
{
    "fix_level": 1,  # or 2, 3
    "fix_type": "prompt_tuning",  # or "model_switch", "quality_downgrade", "human_gate"
    "shot_id": "S001_001",
    "adjustments": {...},
    "qa_results": {...}
}
```

### HUMAN_GATE_TRIGGERED
```python
{
    "fix_level": 3,
    "fix_type": "human_gate",
    "review_info": {
        "project_id": "PROJ-001",
        "shot_id": "S001_001",
        "reason": "Quality score too low",
        "severity": "high"
    }
}
```

## 测试

### 运行测试

完整的测试套件包含 **86 个测试用例**，覆盖所有组件：

```bash
# 设置 Python 路径
$env:PYTHONPATH="d:\文档\Kiro\VIdeoGen"

# 运行所有测试
pytest tests/agents/consistency_guardian/ -v

# 运行特定测试
pytest tests/agents/consistency_guardian/test_threshold_manager.py -v
pytest tests/agents/consistency_guardian/test_auto_fix_strategy.py -v
pytest tests/agents/consistency_guardian/test_consistency_guardian.py -v

# 生成覆盖率报告
pytest tests/agents/consistency_guardian/ --cov=src/agents/consistency_guardian --cov-report=html
```

### 测试覆盖

- ✅ **ThresholdManager**: 10 个测试
- ✅ **CLIPDetector**: 8 个测试
- ✅ **FaceDetector**: 8 个测试
- ✅ **PaletteDetector**: 9 个测试
- ✅ **FlowDetector**: 8 个测试
- ✅ **ContinuityChecker**: 7 个测试
- ✅ **AutoFixStrategy**: 18 个测试（3层修复策略）
- ✅ **ConsistencyGuardian**: 18 个测试（集成测试）

**总计**: 86 个测试用例

### 测试文件

```
tests/agents/consistency_guardian/
├── conftest.py                      # 共享 fixtures
├── test_threshold_manager.py        # 动态阈值测试
├── test_clip_detector.py            # CLIP 检测测试
├── test_face_detector.py            # 面部检测测试
├── test_palette_detector.py         # 色彩检测测试
├── test_flow_detector.py            # 光流检测测试
├── test_continuity_checker.py       # 连贯性检测测试
├── test_auto_fix_strategy.py        # 自动修复策略测试
└── test_consistency_guardian.py     # Agent 集成测试
```

## License

MIT

