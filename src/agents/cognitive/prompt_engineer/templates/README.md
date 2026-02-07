# Prompt 智能构建系统 - 模板库整合说明

## 概述

本目录包含基于完整 Prompt 智能构建系统的模板库，整合了以下核心维度：

1. **角色维度** - 完整的角色外貌、性格、动作描述
2. **场景环境维度** - 空间构成、环境氛围、光线色彩
3. **镜头语言维度** - 镜头类型、角度、运动、构图
4. **风格与情绪维度** - 艺术风格、情绪氛围、叙事基调
5. **动作与表演维度** - 角色动作、互动行为、微表情
6. **时间与连续性维度** - 时间线定位、状态衔接、连续性管理

## 模板文件

### 1. character_portrait.json
**用途**: 角色肖像和特写镜头
**核心要素**:
- 角色标志性特征（signature features）
- 面部细节描述
- 发型发色
- 服装细节
- 表情和情绪

**示例变量**:
```json
{
  "character_signature": "silver star-shaped earrings, red checkered scarf",
  "character_face": "16-year-old girl, oval face, bright blue eyes",
  "character_hair": "jet black long straight hair, red ribbon bow",
  "expression": "bright smile showing teeth"
}
```

### 2. action_scene.json
**用途**: 动作和运动镜头
**核心要素**:
- 主要动作描述
- 次要动作和微表情
- 环境互动
- 镜头运动跟随
- 动作连续性

**示例变量**:
```json
{
  "action_primary": "walking forward slowly, taking measured steps",
  "action_secondary": "right hand brushing hair behind ear",
  "camera_movement": "slow pan right following character"
}
```

### 3. environment_establishing.json
**用途**: 环境展示和场景建立
**核心要素**:
- 空间布局
- 关键物体
- 时间和天气
- 光线和色彩
- 环境氛围

**示例变量**:
```json
{
  "location_type": "outdoor rooftop",
  "time_of_day": "golden hour around 4-5 PM",
  "lighting": "warm golden sunlight, soft diffused lighting",
  "atmosphere": "warm, nostalgic, peaceful"
}
```

## 质量档位系统

所有模板支持 4 个质量档位：

- **DRAFT**: 快速生成，基础质量
- **STANDARD**: 标准质量，平衡速度和效果
- **HIGH**: 高质量，详细渲染
- **PREMIUM**: 顶级质量，专业级输出

每个档位自动添加相应的质量修饰符。

## 使用示例

### Python 代码示例

```python
from src.agents.prompt_engineer import PromptEngineer

# 初始化
engineer = PromptEngineer(blackboard, event_bus)

# 生成 prompt
prompt_config = engineer.create_prompt_config(
    shot=shot_data,
    dna_tokens=["silver star earrings", "red scarf"],
    global_spec=global_spec,
    quality_tier="HIGH"
)

# 输出
print(prompt_config["positive"])
print(prompt_config["negative"])
```

### 生成的 Prompt 示例

**输入**:
- Template: character_portrait
- Character: 小美
- Expression: bright smile
- Quality: HIGH

**输出 Prompt**:
```
silver star-shaped earrings, red checkered scarf, 16-year-old girl with oval face, 
bright blue eyes, small delicate nose, jet black long straight hair reaching waist 
with red ribbon bow, white cotton blouse with Peter Pan collar, navy blue pleated skirt, 
bright smile showing teeth, warm lighting, portrait shot, medium close-up, 
highly detailed, ultra realistic, 8k, photorealistic, professional photography
```

**Negative Prompt**:
```
blurry, distorted, multiple faces, deformed, low quality, bad anatomy, 
extra fingers, fused fingers, poorly drawn face, ugly, bad proportions
```

## 连续性管理

模板系统支持跨镜头连续性：

1. **角色一致性**: 使用 DNA Bank 中的 signature features
2. **状态衔接**: 记录每个镜头的结束状态
3. **时间连续**: 维护时间线和相对时间
4. **视觉连贯**: 保持光线、色彩、风格一致

## DNA Token 注入

系统自动从 DNA Bank 提取并注入：

- **外观特征**: appearance_tokens
- **风格特征**: style_tokens
- **置信度过滤**: 仅使用 confidence >= 0.6 的 tokens

## 扩展模板

要添加新模板：

1. 创建 JSON 文件在 `templates/` 目录
2. 遵循标准模板结构
3. 定义所有必需变量
4. 设置质量修饰符
5. 添加 negative prompt
6. 设置优先级和标签

## 参考文档

完整的 Prompt 智能构建系统文档：
`d:\文档\Kiro\VIdeoGen\方案参考\prompt智能构建系统.md`

包含：
- 完整的元素库定义
- 模板变体库
- GPT 优化器集成
- 连续性追踪系统
- 最佳实践指南
