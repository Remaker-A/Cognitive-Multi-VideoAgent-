# VideoGen Agent

VideoGen Agent 负责视频生成和质量分析。

## 核心功能

✅ **视频生成**: 使用 Runway 等模型生成视频
✅ **帧提取**: 提取关键帧和 embeddings
✅ **时间连贯性**: 计算帧间 SSIM 一致性
✅ **光流分析**: 分析运动流畅度
✅ **质量检查**: 自动质量评估

## 快速开始

```python
from src.agents.video_gen import VideoGen

agent = VideoGen(blackboard, event_bus, storage)
await agent.start()
```

## 组件结构

```
src/agents/video_gen/
├── video_gen.py                # 核心 Agent (180+ 行) ✅
├── frame_extractor.py          # 帧提取 (130+ 行) ✅
├── temporal_coherence.py       # 连贯性计算 (80+ 行) ✅
├── optical_flow_analyzer.py    # 光流分析 (110+ 行) ✅
└── README.md                   # 文档 ✅

src/adapters/implementations/
├── runway_adapter.py           # Runway 适配器 (230+ 行) ✅
└── (已有 sdxl_adapter.py)
```

## 工作流程

```
PREVIEW_VIDEO_REQUESTED Event
    ↓
1. Select Adapter (Runway)
2. Generate Video
3. Extract Frames
4. Calculate Temporal Coherence
5. Analyze Optical Flow
6. Extract Frame Embeddings
7. Save Quality Metrics
    ↓
PREVIEW_VIDEO_READY Event
```

## 质量指标

### 时间连贯性 (Temporal Coherence)
- **计算方法**: 帧间 SSIM
- **阈值**: >= 0.85
- **含义**: 视频帧之间的视觉一致性

### 光流流畅度 (Optical Flow Smoothness)
- **计算方法**: Farneback 光流
- **阈值**: >= 0.75
- **含义**: 运动的平滑程度

### 帧一致性 (Frame Consistency)
- **计算方法**: Frame embeddings 相似度
- **阈值**: >= 0.80
- **含义**: 帧特征的一致性

## Runway Adapter

### 支持参数
- prompt: 视频描述
- duration: 时长（最大 10 秒）
- fps: 帧率
- width/height: 分辨率
- motion_strength: 运动强度 (0-1)
- keyframes: 关键帧图像列表

### 工作流程
1. 提交生成任务
2. 轮询任务状态（最多 60 次，间隔 5 秒）
3. 下载视频
4. 返回结果

### Cost
- $0.05/秒

## License

MIT
