# ArtDirector Agent

ArtDirector Agent 负责视觉 DNA 管理和特征提取。

## 核心功能

✅ **特征提取**: 面部、色彩、纹理、构图
✅ **DNA Bank 更新**: 多版本 embedding 管理
✅ **加权合并**: 4 种合并策略
✅ **置信度计算**: 自动质量评估
✅ **Prompt 调整**: DNA tokens 建议

## 快速开始

```python
from src.agents.art_director import ArtDirector

agent = ArtDirector(blackboard, event_bus)
await agent.start()
```

## 组件结构

```
src/agents/art_director/
├── art_director.py         # 核心 Agent (180+ 行) ✅
├── feature_extractor.py    # 特征提取 (280+ 行) ✅
├── dna_manager.py          # DNA 管理 (200+ 行) ✅
├── merge_strategy.py       # 合并策略 (150+ 行) ✅
└── README.md               # 文档 ✅
```

## 工作流程

```
IMAGE_GENERATED Event
    ↓
1. Extract Features
   - Face embedding (CLIP)
   - Color palette (K-means)
   - Texture (statistics)
   - Composition
    ↓
2. Calculate Confidence
    ↓
3. Update DNA Bank
   - Add new version
   - Rebalance weights
   - Merge embeddings
    ↓
4. Generate Appearance Tokens
    ↓
DNA_BANK_UPDATED Event
```

## 特征提取

### 面部 Embedding
- **模型**: CLIP (临时) / InsightFace (计划)
- **输出**: 512-d 向量
- **归一化**: L2 normalization

### 色彩提取
- **算法**: K-means 聚类
- **颜色数**: 5
- **输出**: RGB + HEX + 占比

### 纹理分析
- **统计**: 均值、标准差、对比度
- **输出**: 纹理特征字典

### 置信度计算
- Face: 40%
- Palette: 30%
- Texture: 20%
- General: 10%

## DNA Bank 结构

```python
{
    "character_id": "char_001",
    "embeddings": [
        {
            "version": 1,
            "face_embedding": np.array(...),
            "palette": {...},
            "texture": {...},
            "weight": 0.35,
            "confidence": 0.85,
            "source": "keyframe_001",
            "timestamp": "2024-..."
        }
    ],
    "merged_embedding": np.array(...),
    "appearance_tokens": ["color_#ff5733", "..."],
    "style_tokens": []
}
```

## 合并策略

### 1. Weighted Average（默认）
- 按置信度加权平均
- 自动归一化权重
- 适用于大多数场景

### 2. Latest Priority
- 保留最新的 N 个版本
- 适用于角色外观变化场景

### 3. Confidence Threshold
- 过滤低置信度版本
- 阈值: 0.6
- 适用于质量控制

### 4. Manual Selection
- 人工选择保留版本
- 适用于关键角色

## Prompt 调整建议

```python
{
    "dna_tokens": ["color_#ff5733_v3", "..."],
    "weight_adjustments": {
        "character_consistency": 1.2,
        "color_palette": 1.1
    },
    "negative_prompts": [
        "inconsistent_face",
        "color_shift",
        "different_appearance"
    ]
}
```

## License

MIT
