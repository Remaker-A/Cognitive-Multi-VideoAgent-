# Adapters - 模型适配器层

模型适配器层为不同 AI 模型提供统一的调用接口。

## 核心组件

### 1. 基础接口 (base.py)

所有 Adapter 的抽象基类：

```python
class BaseAdapter(ABC):
    @abstractmethod
    async def generate(self, **kwargs):
        """生成接口"""
        pass
    
    @abstractmethod
    def calculate_cost(self, result):
        """计算成本"""
        pass
```

### 2. 统一输出 Schema (schemas.py)

标准化的输出格式：

- `GenerationResult` - 基础结果
- `ImageGenerationResult` - 图像结果
- `VideoGenerationResult` - 视频结果
- `VoiceGenerationResult` - 语音结果
- `MusicGenerationResult` - 音乐结果

### 3. 具体 Adapter 接口

#### ImageModelAdapter
- `generate()` - 生成图像
- `generate_batch()` - 批量生成

#### VideoModelAdapter
- `generate()` - 生成视频
- `extend_video()` - 延长视频
- `interpolate()` - 图像插值

#### VoiceModelAdapter
- `generate()` - 生成语音
- `clone_voice()` - 克隆声音
- `get_available_voices()` - 获取声音列表

#### MusicModelAdapter
- `generate()` - 生成音乐
- `extend_music()` - 延长音乐
- `remix()` - 混音

## 使用示例

### 实现自定义 Adapter

```python
from src.adapters import ImageModelAdapter, ImageGenerationResult

class SDXLAdapter(ImageModelAdapter):
    async def generate(self, prompt, **kwargs):
        # 调用 SDXL API
        result = await sdxl_api.generate(prompt)
        
        return ImageGenerationResult(
            success=True,
            artifact_url=result.url,
            width=1024,
            height=1024,
            metadata={"model": "sdxl-1.0"}
        )
    
    def calculate_cost(self, result):
        return 0.02  # $0.02 per image
```

### 使用 Adapter

```python
adapter = SDXLAdapter(model_name="sdxl-1.0")

result = await adapter.generate(
    prompt="a beautiful sunset",
    negative_prompt="blurry",
    width=1024,
    height=1024
)

print(f"Image URL: {result.artifact_url}")
print(f"Cost: ${result.cost}")
```

## Adapter 列表

### 已计划实现的 Adapters

**图像模型**:
- SDXL
- DALL-E 3
- Midjourney
- Stable Diffusion 3

**视频模型**:
- Sora 2
- Veo 3.1
- Runway
- Pika

**语音模型**:
- MiniMax TTS
- ElevenLabs

**音乐模型**:
- Tunee
- Suno

## 架构优势

1. **统一接口**: 所有模型使用相同的调用方式
2. **易于扩展**: 新增模型只需实现 Adapter 接口
3. **标准化输出**: 统一的数据结构
4. **成本追踪**: 内置成本计算
5. **灵活参数**: 支持模型特定参数

## License

MIT
