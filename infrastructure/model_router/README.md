# ModelRouter

ModelRouter 是 LivingAgentPipeline v2.0 的模型路由器，负责模型选择、成本估算和能力查询。

## 核心特性

✅ **智能模型选择**: 基于质量档位和预算的多维度选择
✅ **成本估算**: 准确的任务成本预测
✅ **模型注册表**: 预定义常用模型
✅ **质量档位**: 4 个质量等级

## 快速开始

### 基础使用

```python
from src.infrastructure.model_router import ModelRouter, QualityTier
from src.infrastructure.model_router.factory import ModelRouterFactory

# 创建 ModelRouter
router = ModelRouterFactory.create()

# 选择模型
model = router.select_model(
    task_type="GENERATE_KEYFRAME",
    quality_tier=QualityTier.STANDARD,
    budget_remaining=10.0
)

print(f"Selected model: {model.name}")
print(f"Cost per unit: ${model.cost_per_unit}")
```

## 质量档位

- **DRAFT (1)**: 草稿质量 - 快速、低成本
- **STANDARD (2)**: 标准质量 - 平衡质量和成本
- **HIGH (3)**: 高质量 - 更好的效果
- **PREMIUM (4)**: 顶级质量 - 最佳效果

## 预定义模型

### 图像生成
- **sdxl-turbo**: DRAFT, $0.01/image
- **sdxl**: STANDARD, $0.04/image
- **midjourney-v6**: HIGH, $0.08/image

### 视频生成
- **runway-gen2**: STANDARD, $0.30/second
- **runway-gen3**: HIGH, $0.50/second

### 文本生成
- **gpt-4**: HIGH, $0.03/1k tokens

## License

MIT
