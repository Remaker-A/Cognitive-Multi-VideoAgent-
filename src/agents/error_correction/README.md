# ErrorCorrection Agent

ErrorCorrection Agent 负责检测 AI 生成内容中的视觉错误。

## 核心功能

✅ **手部检测**: 手指数量、手部形态
✅ **面部检测**: 五官、表情
✅ **姿态检测**: 人物姿态、解剖学正确性
✅ **物理规律检测**: 重力、透视
✅ **文字检测**: OCR、乱码、拼写
✅ **错误分级**: CRITICAL / HIGH / MEDIUM / LOW

## 快速开始

```python
from src.agents.error_correction import ErrorCorrection

agent = ErrorCorrection(blackboard, event_bus)
await agent.start()
```

## 组件结构

```
src/agents/error_correction/
├── error_correction.py      # 核心 Agent (180+ 行) ✅
├── error_classifier.py      # 错误分级 (120+ 行) ✅
├── hand_detector.py          # 手部检测 (70+ 行) ✅
├── face_detector.py          # 面部检测 (60+ 行) ✅
├── pose_detector.py          # 姿态检测 (60+ 行) ✅
├── physics_detector.py       # 物理检测 (60+ 行) ✅
├── text_detector.py          # 文字检测 (60+ 行) ✅
└── README.md                 # 文档 ✅
```

## 错误严重程度分级

### CRITICAL（严重）- 必须修复

**手部错误**:
- `hand_finger_count_wrong`: 手指数量错误
- `hand_missing`: 手部缺失

**面部错误**:
- `face_missing_eyes`: 缺少眼睛
- `face_missing_nose`: 缺少鼻子
- `face_missing_mouth`: 缺少嘴巴

**姿态错误**:
- `pose_anatomically_impossible`: 解剖学上不可能的姿态
- `pose_limb_missing`: 肢体缺失

### HIGH（高）- 强烈建议修复

**手部错误**:
- `hand_deformed`: 手部形态异常

**面部错误**:
- `face_expression_abnormal`: 表情异常

**姿态错误**:
- `pose_unnatural`: 姿态不自然

**物理错误**:
- `physics_gravity_violation`: 重力违背
- `physics_floating_object`: 物体不自然悬浮

### MEDIUM（中）- 建议修复

**面部错误**:
- `face_asymmetric`: 面部不对称

**物理错误**:
- `physics_perspective_wrong`: 透视错误

**文字错误**:
- `text_gibberish`: 乱码

### LOW（低）- 可选修复

**文字错误**:
- `text_spelling_error`: 拼写错误
- `text_blurry`: 文字模糊

## 检测流程

```
IMAGE_GENERATED Event
    ↓
1. Hand Detection
2. Face Detection
3. Pose Detection
4. Physics Detection
5. Text Detection
    ↓
6. Error Classification
7. Severity Grading
    ↓
ERROR_DETECTED Event (if errors found)
```

## 使用示例

### 检测图像错误

```python
# 自动检测（事件驱动）
# ErrorCorrection 会自动监听 IMAGE_GENERATED 事件

# 手动检测
error_report = agent.detect_errors(
    artifact_url="data:image/png;base64,...",
    artifact_type="image"
)

# 结果格式
{
    "errors_by_severity": {
        "CRITICAL": [
            {
                "type": "hand_finger_count_wrong",
                "description": "Hand has 6 fingers instead of 5",
                "confidence": 0.9,
                "location": {...}
            }
        ],
        "HIGH": [...],
        "MEDIUM": [...],
        "LOW": [...]
    },
    "stats": {
        "total_errors": 5,
        "critical_count": 1,
        "high_count": 2,
        "medium_count": 1,
        "low_count": 1
    },
    "requires_fix": True
}
```

## 事件发布

### ERROR_DETECTED
```python
{
    "shot_id": "S001_001",
    "error_report": {...},
    "artifact_url": "..."
}
```

## 未来扩展

### 计划集成的模型

- **Hand Detection**: MediaPipe Hands
- **Face Detection**: MediaPipe Face Mesh
- **Pose Detection**: OpenPose / MediaPipe Pose
- **OCR**: EasyOCR / PaddleOCR

### 计划功能

- 自动修复建议
- 错误热力图可视化
- 批量检测优化

## 注意事项

⚠️ **当前版本**: 简化版本，检测器返回占位符结果
⚠️ **生产环境**: 需要集成真实的检测模型
⚠️ **性能**: 检测可能需要较长时间，建议异步处理

## License

MIT
