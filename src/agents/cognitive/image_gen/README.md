# ImageGen Agent

ImageGen Agent 负责图像生成、质量检查和失败重试。

## 核心功能

✅ **图像生成**: 使用 SDXL 等模型生成图像
✅ **Embedding 提取**: 提取图像 embedding 向量
✅ **CLIP 相似度**: 计算图与 prompt 的匹配度
✅ **失败重试**: CLIP < 0.25 或API错误时自动重试
✅ **事件发布**: IMAGE_GENERATED 事件

## 快速开始

```python
from src.agents.image_gen import ImageGen

agent = ImageGen(blackboard, event_bus, storage)
await agent.start()
```

## 组件结构

```
src/agents/image_gen/
├── image_gen.py            # 核心 Agent (200+ 行) ✅
├── embedding_extractor.py  # Embedding 提取 (120+ 行) ✅
├── clip_scorer.py          # CLIP 计算 (100+ 行) ✅
└── README.md               # 文档 ✅

src/adapters/implementations/
├── sdxl_adapter.py         # SDXL 适配器 (200+ 行) ✅
└── __init__.py             ✅
```

## 工作流程

```
KEYFRAME_REQUESTED Event
    ↓
1. Get Prompt Config
2. Select Adapter (SDXL)
3. Generate Image
4. Check Quality (CLIP score)
    ↓ (< 0.25)
5. Retry (max 2 times)
    ↓
6. Extract Embedding
7. Save to Blackboard
    ↓
IMAGE_GENERATED Event
```

## 失败策略

1. **CLIP < 0.25** → 调整 prompt 重试（最多 2 次）
2. **API 错误** → 重试（最多 2 次）
3. **仍失败** → 上报 ChefAgent

## SDXL Adapter

### 支持参数
- prompt: 正向 prompt
- negative_prompt: 负向 prompt
- width/height: 分辨率
- seed: 随机种子
- cfg_scale: CFG 强度
- steps: 采样步数

### Cost
- 基础: $0.02/image
- 超过 1024x1024: $0.03/image

## License

MIT
