# Physics & Logic Checker

物理和逻辑检查器模块，用于检测视频序列中的物理规律违反和内容逻辑错误。

## 功能特性

### 物理检查
- ✅ **重力检查** (`GravityChecker`): 检测物体下落方向，识别反重力异常
- ✅ **运动检查** (`MotionChecker`): 检测瞬移和异常加速/减速
- 🚧 **空间关系检查** (`SpatialRelationChecker`): 检测遮挡关系和深度一致性（待实现）

### 逻辑检查
- ✅ **连续性检查** (`ContinuityErrorDetector`): 检测物体突然消失/出现
- 🚧 **状态检查** (`ObjectStateChecker`): 检测物品状态跳变（待实现）
- 🚧 **时间逻辑检查** (`TemporalLogicChecker`): 检测时间顺序错误（待实现）

### 多模态 LLM 集成
- 🔄 **成本优化**: 分层检测、关键帧采样、智能缓存
- 🔄 **模型选择**: 支持 GPT-4V, Claude 3, Gemini Pro Vision
- 🔄 **预算控制**: 可配置每视频预算，自动降级

## 快速开始

### 基础使用

```python
from src.agents.physics_logic_checker import PhysicsLogicChecker
import numpy as np

# 初始化检查器
checker = PhysicsLogicChecker(config={
    "enable_physics_check": True,
    "enable_logic_check": True,
    "enable_llm": False  # 暂时禁用 LLM
})

# 准备视频帧
frames = [...]  # List[np.ndarray]

# 运行检查
result = await checker.check_video_sequence(
    frames=frames,
    metadata={"quality_tier": "HIGH"}
)

# 查看结果
print(f"Overall score: {result.overall_score}")
print(f"Physics errors: {len(result.physics_errors)}")
print(f"Logic errors: {len(result.logic_errors)}")
print(f"Passed: {result.passed}")
```

### 启用 LLM 验证

```python
# 配置 LLM
config = {
    "enable_llm": True,
    "llm_budget": 0.50,  # 每个视频 $0.50 预算
    "llm_verification_level": "lightweight",
    "llm_models": {
        "lightweight": "claude-3-haiku",
        "balanced": "gemini-pro-vision",
        "advanced": "gpt-4-vision"
    }
}

checker = PhysicsLogicChecker(config)
result = await checker.check_video_sequence(frames)

print(f"LLM cost: ${result.llm_cost:.3f}")
```

## 架构

```
PhysicsLogicChecker
├── Physics Checkers
│   ├── GravityChecker
│   ├── MotionChecker
│   └── SpatialRelationChecker
│
├── Logic Checkers
│   ├── ContinuityErrorDetector
│   ├── ObjectStateChecker
│   └── TemporalLogicChecker
│
├── Multimodal LLM (待实现)
│   ├── LLMVerifier
│   ├── PromptBuilder
│   ├── CostOptimizer
│   └── CacheManager
│
└── Utils (待实现)
    ├── ObjectDetector
    ├── ObjectTracker
    ├── KeyFrameSelector
    └── MotionAnalyzer
```

## 数据结构

### 错误类型

```python
class ErrorType(Enum):
    # 物理错误
    GRAVITY_VIOLATION = "gravity_violation"
    MOTION_ANOMALY = "motion_anomaly"
    SPATIAL_INCONSISTENCY = "spatial_inconsistency"
    
    # 逻辑错误
    CONTINUITY_ERROR = "continuity_error"
    STATE_JUMP = "state_jump"
    TEMPORAL_ERROR = "temporal_error"
```

### 严重性等级

```python
class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

### 检查结果

```python
@dataclass
class CheckResult:
    physics_errors: List[PhysicsError]
    logic_errors: List[LogicError]
    overall_score: float  # 0-1
    passed: bool
    summary: Dict[str, Any]
    llm_cost: float
    processing_time: float
```

## 当前状态

### ✅ 已完成
- 基础数据结构
- 主检查器框架
- 重力检查器（基础版）
- 运动检查器（基础版）
- 连续性错误检测器（基础版）

### 🚧 进行中
- 对象检测和跟踪集成
- 关键帧选择器
- LLM 验证器

### 📋 待实现
- 空间关系检查器
- 状态检查器
- 时间逻辑检查器
- 深度估计
- 完整的 LLM 集成
- 测试套件

## 配置选项

```python
config = {
    # 基础功能
    "enable_physics_check": True,
    "enable_logic_check": True,
    "enable_llm": False,
    
    # LLM 配置
    "llm_budget": 0.5,
    "llm_verification_level": "lightweight",
    
    # 物理检查参数
    "gravity_threshold": 0.7,
    "max_acceleration": 50.0,
    "teleport_threshold": 200.0,
    
    # 逻辑检查参数
    "min_track_length": 5,
    "disappearance_threshold": 3,
    
    # 关键帧选择
    "keyframe_selection": {
        "method": "scene_change",
        "max_keyframes": 100
    }
}
```

## 依赖

```
numpy>=1.24.0
opencv-python>=4.8.0
```

可选（用于高级功能）:
```
ultralytics>=8.0.0  # YOLO 对象检测
torch>=2.0.0
transformers>=4.30.0  # CLIP
```

## 开发路线图

### Phase 1: 基础框架 ✅
- [x] 数据结构定义
- [x] 主检查器实现
- [x] 基础物理检查器
- [x] 基础逻辑检查器

### Phase 2: 工具集成 🚧
- [ ] 对象检测器
- [ ] 对象跟踪器
- [ ] 关键帧选择器
- [ ] 运动分析器

### Phase 3: LLM 集成 📋
- [ ] LLM 验证器
- [ ] 提示词构建器
- [ ] 成本优化器
- [ ] 缓存管理器

### Phase 4: 高级功能 📋
- [ ] 深度估计
- [ ] 空间关系检查
- [ ] 状态识别
- [ ] 时间逻辑推理

### Phase 5: 测试和优化 📋
- [ ] 单元测试
- [ ] 集成测试
- [ ] 性能优化
- [ ] 文档完善

## 许可证

MIT

---

**版本**: 0.1.0  
**状态**: 开发中  
**最后更新**: 2026-01-09
