# ShotDirector Agent

ShotDirector Agent 负责 shot 级别的规划和镜头设计。

## 核心功能

✅ **Shot 规划**: 为每个 shot 规划具体细节
✅ **镜头语言**: 定义镜头类型、运动、角度
✅ **Keyframe 请求**: 自动生成 keyframe 请求
✅ **Preview Video**: 生成预览视频请求
✅ **Shot 审批**: 审批 shot 完成

## 快速开始

```python
from src.agents.shot_director import ShotDirector

director = ShotDirector(blackboard, event_bus)
await director.start()
```

## 组件结构

```
src/agents/shot_director/
├── shot_director.py         # 核心 Agent (200+ 行) ✅
├── shot_planner.py         # Shot 规划器 (200+ 行) ✅
├── camera_language.py      # 镜头语言 (130+ 行) ✅
├── keyframe_requester.py   # Keyframe 请求器 (120+ 行) ✅
└── README.md               # 文档 ✅
```

## 镜头语言

### 镜头类型
- Extreme Close-Up
- Close-Up
- Medium Shot
- Full Shot
- Long Shot
- Extreme Long Shot

### 镜头运动
- Static
- Pan (Left/Right)
- Tilt (Up/Down)
- Dolly (In/Out)
- Tracking
- Zoom

### 镜头角度
- Eye Level
- High Angle
- Low Angle
- Bird's Eye
- Worm's Eye

## 工作流程

```
SCENE_WRITTEN Event
    ↓
For each Shot:
  1. Plan Shot (camera, duration, keyframes)
  2. Create Keyframe Requests
  3. Publish KEYFRAME_REQUESTED
    ↓
SHOT_PLANNED Event
```

## License

MIT
