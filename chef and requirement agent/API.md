# RequirementParser Agent API 文档

## 概述

本文档详细描述了 RequirementParser Agent 的 API 接口、数据模型和使用方法。

## 核心 API

### RequirementParserAgent

主 Agent 类，负责协调所有组件完成需求解析流程。

#### 初始化

```python
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.requirement_parser.config import RequirementParserConfig

# 使用默认配置
agent = RequirementParserAgent()

# 使用自定义配置
config = RequirementParserConfig(
    deepseek_api_key="your_api_key",
    max_retries=5,
    timeout_seconds=60,
    confidence_threshold=0.7
)
agent = RequirementParserAgent(config=config)
```

**参数**:
- `config` (Optional[RequirementParserConfig]): 配置对象，默认使用环境变量配置
- `deepseek_client` (Optional[DeepSeekClient]): DeepSeek API 客户端，默认自动创建
- `metrics_collector` (Optional[MetricsCollector]): 指标收集器，默认使用全局实例

#### process_user_input

处理用户输入的主入口方法。

```python
async def process_user_input(
    user_input: UserInputData,
    causation_id: Optional[str] = None
) -> ProcessingResult
```

**参数**:
- `user_input` (UserInputData): 用户输入数据
- `causation_id` (Optional[str]): 触发此处理的事件 ID

**返回**:
- `ProcessingResult`: 处理结果，包含 GlobalSpec、置信度报告等

**异常**:
- `RequirementParserError`: 处理失败时抛出

**示例**:
```python
from src.agents.requirement_parser.models import UserInputData

user_input = UserInputData(
    text_description="一个年轻的探险家在神秘森林中寻找宝藏",
    reference_images=["s3://bucket/image1.jpg"],
    reference_videos=[],
    reference_audio=[],
    user_preferences={"quality_tier": "high"}
)

result = await agent.process_user_input(user_input)

if result.status == ProcessingStatus.COMPLETED:
    print(f"Success! GlobalSpec: {result.global_spec}")
    print(f"Confidence: {result.confidence_report.overall_confidence}")
else:
    print(f"Failed: {result.error_message}")
```

#### close

关闭 Agent 并清理资源。

```python
async def close() -> None
```

**示例**:
```python
# 使用上下文管理器（推荐）
async with RequirementParserAgent() as agent:
    result = await agent.process_user_input(user_input)

# 或手动关闭
agent = RequirementParserAgent()
try:
    result = await agent.process_user_input(user_input)
finally:
    await agent.close()
```

## 数据模型

### UserInputData

用户输入数据结构。

```python
@dataclass
class UserInputData:
    text_description: str                    # 文本描述
    reference_images: List[str] = []         # 参考图片 URL 列表
    reference_videos: List[str] = []         # 参考视频 URL 列表
    reference_audio: List[str] = []          # 参考音频 URL 列表
    user_preferences: Dict[str, Any] = {}    # 用户偏好设置
    timestamp: str = ""                      # 提交时间戳
```

**字段说明**:
- `text_description`: 用户的文本描述，可以包含项目需求、场景描述、角色信息等
- `reference_images`: 参考图片的 S3 URL 列表，用于风格参考
- `reference_videos`: 参考视频的 S3 URL 列表，用于运镜和节奏参考
- `reference_audio`: 参考音频的 S3 URL 列表，用于情绪和风格参考
- `user_preferences`: 用户偏好设置，如质量档位、宽高比等
- `timestamp`: 提交时间戳，ISO 8601 格式

**示例**:
```python
user_input = UserInputData(
    text_description="一个温馨的家庭聚餐场景，时长30秒",
    reference_images=[
        "s3://my-bucket/reference/warm-lighting.jpg",
        "s3://my-bucket/reference/family-dinner.jpg"
    ],
    reference_videos=[],
    reference_audio=["s3://my-bucket/reference/background-music.mp3"],
    user_preferences={
        "quality_tier": "high",
        "aspect_ratio": "16:9"
    },
    timestamp="2025-12-27T10:30:00Z"
)
```

### GlobalSpec

全局规格数据结构，描述视频项目的所有基础配置。

```python
@dataclass
class GlobalSpec:
    title: str                          # 项目标题
    duration: int                       # 视频时长（秒）
    aspect_ratio: str                   # 宽高比
    quality_tier: str                   # 质量档位
    resolution: str                     # 分辨率
    fps: int                            # 帧率
    style: StyleConfig                  # 风格配置
    characters: List[str]               # 角色列表
    mood: str                           # 整体情绪
    user_options: Dict[str, Any]        # 用户选项
```

**字段说明**:
- `title`: 项目标题，从用户输入中提取或生成
- `duration`: 视频时长（秒），从用户输入中提取或使用默认值
- `aspect_ratio`: 宽高比，支持 "16:9", "9:16", "1:1", "4:3", "3:4"
- `quality_tier`: 质量档位，支持 "low", "balanced", "high"
- `resolution`: 分辨率，如 "1080x1920"
- `fps`: 帧率，通常为 30 或 60
- `style`: 风格配置对象
- `characters`: 角色名称列表
- `mood`: 整体情绪标签，如 "温馨", "紧张", "欢快"
- `user_options`: 用户自定义选项

**示例**:
```python
global_spec = GlobalSpec(
    title="家庭聚餐",
    duration=30,
    aspect_ratio="16:9",
    quality_tier="high",
    resolution="1920x1080",
    fps=30,
    style=StyleConfig(
        tone="warm",
        palette=["#FFA500", "#FFD700", "#FFFFFF"],
        visual_dna_version=1
    ),
    characters=["父亲", "母亲", "孩子"],
    mood="温馨,欢乐",
    user_options={}
)
```

### StyleConfig

风格配置数据结构。

```python
@dataclass
class StyleConfig:
    tone: str                           # 色调风格
    palette: List[str]                  # 调色板（十六进制颜色）
    visual_dna_version: int             # 视觉 DNA 版本
```

**字段说明**:
- `tone`: 色调风格，如 "warm"（温暖）, "cool"（冷色）, "natural"（自然）
- `palette`: 调色板，十六进制颜色代码列表
- `visual_dna_version`: 视觉 DNA 版本号

### ProcessingResult

处理结果数据结构。

```python
@dataclass
class ProcessingResult:
    status: ProcessingStatus                        # 处理状态
    global_spec: Optional[GlobalSpec]               # 生成的 GlobalSpec
    confidence_report: Optional[ConfidenceReport]   # 置信度报告
    error_message: Optional[str] = None             # 错误消息
    processing_time: float = 0.0                    # 处理时间（秒）
    cost: float = 0.0                               # 成本（美元）
    events_published: int = 0                       # 发布的事件数量
```

**字段说明**:
- `status`: 处理状态，枚举值：COMPLETED, FAILED, PENDING
- `global_spec`: 生成的 GlobalSpec，失败时为 None
- `confidence_report`: 置信度报告，失败时为 None
- `error_message`: 错误消息，成功时为 None
- `processing_time`: 处理时间（秒）
- `cost`: API 调用成本（美元）
- `events_published`: 发布的事件数量

**方法**:
```python
def is_successful(self) -> bool:
    """判断处理是否成功"""
    return self.status == ProcessingStatus.COMPLETED
```

### ConfidenceReport

置信度报告数据结构。

```python
@dataclass
class ConfidenceReport:
    overall_confidence: float                       # 总体置信度 (0-1)
    confidence_level: ConfidenceLevel               # 置信度等级
    component_scores: Dict[str, float]              # 各组件置信度分数
    low_confidence_areas: List[str]                 # 低置信度区域
    clarification_requests: List[ClarificationRequest]  # 澄清请求列表
    recommendation: str                             # 建议行动
```

**字段说明**:
- `overall_confidence`: 总体置信度分数，范围 0.0-1.0
- `confidence_level`: 置信度等级，枚举值：HIGH, MEDIUM, LOW
- `component_scores`: 各组件的置信度分数字典
- `low_confidence_areas`: 置信度低的区域列表
- `clarification_requests`: 需要澄清的问题列表
- `recommendation`: 建议的后续行动，值为 "proceed", "clarify", "human_review"

**示例**:
```python
confidence_report = ConfidenceReport(
    overall_confidence=0.75,
    confidence_level=ConfidenceLevel.MEDIUM,
    component_scores={
        "text_clarity": 0.8,
        "style_consistency": 0.7,
        "completeness": 0.75,
        "user_input_quality": 0.7
    },
    low_confidence_areas=["style_consistency"],
    clarification_requests=[
        ClarificationRequest(
            field="style",
            question="请提供更多关于视觉风格的描述",
            suggestions=["现代简约", "复古怀旧", "科幻未来"]
        )
    ],
    recommendation="proceed"
)
```

## 配置 API

### RequirementParserConfig

配置类，管理所有 Agent 配置项。

```python
from src.agents.requirement_parser.config import RequirementParserConfig

config = RequirementParserConfig(
    # Agent 基础配置
    agent_name="RequirementParserAgent",
    
    # DeepSeek API 配置
    deepseek_api_key="your_api_key",
    deepseek_api_endpoint="https://api.deepseek.com/v1",
    deepseek_model_name="DeepSeek-V3.2",
    
    # 业务配置
    max_retries=3,
    timeout_seconds=30,
    confidence_threshold=0.6,
    
    # 默认配置
    default_quality_tier="balanced",
    default_aspect_ratio="9:16",
    default_resolution="1080x1920",
    default_fps=30,
    
    # 基础设施配置
    event_bus_url="redis://localhost:6379",
    blackboard_url="http://localhost:8000"
)
```

**方法**:

#### get_model_config

获取模型配置。

```python
def get_model_config(self) -> Dict[str, Any]
```

**返回**: 包含 API 配置的字典

#### get_default_global_spec_config

获取默认 GlobalSpec 配置。

```python
def get_default_global_spec_config(self) -> Dict[str, Any]
```

**返回**: 包含默认视频配置的字典

#### validate_required_config

验证必需配置项。

```python
def validate_required_config(self) -> None
```

**异常**: 配置无效时抛出 `ConfigurationError`

## 组件 API

### DeepSeekClient

DeepSeek API 客户端。

```python
from src.agents.requirement_parser.deepseek_client import DeepSeekClient

client = DeepSeekClient(
    api_key="your_api_key",
    base_url="https://api.deepseek.com/v1",
    model_name="DeepSeek-V3.2",
    timeout=30,
    max_retries=3
)
```

#### chat_completion

调用聊天完成 API。

```python
async def chat_completion(
    messages: List[Dict[str, str]],
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> ChatCompletionResponse
```

**参数**:
- `messages`: 消息列表，格式为 `[{"role": "user", "content": "..."}]`
- `temperature`: 温度参数，控制随机性，范围 0.0-2.0
- `max_tokens`: 最大生成 token 数

**返回**: ChatCompletionResponse 对象

**示例**:
```python
response = await client.chat_completion(
    messages=[
        {"role": "system", "content": "你是一个视频需求分析助手"},
        {"role": "user", "content": "分析这个需求：一个温馨的家庭聚餐场景"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.content)
```

### InputManager

输入管理器，负责接收和验证用户输入。

```python
from src.agents.requirement_parser.input_manager import InputManager

manager = InputManager()
```

#### receive_user_input

接收用户输入并进行初步验证。

```python
async def receive_user_input(
    input_data: UserInputData
) -> ProcessedInput
```

### GlobalSpecGenerator

GlobalSpec 生成器。

```python
from src.agents.requirement_parser.global_spec_generator import GlobalSpecGenerator

generator = GlobalSpecGenerator(
    default_config={
        "quality_tier": "balanced",
        "aspect_ratio": "9:16",
        "resolution": "1080x1920",
        "fps": 30
    }
)
```

#### generate_spec

生成 GlobalSpec。

```python
async def generate_spec(
    analysis: SynthesizedAnalysis,
    user_input: UserInputData
) -> GlobalSpec
```

### ConfidenceEvaluator

置信度评估器。

```python
from src.agents.requirement_parser.confidence_evaluator import ConfidenceEvaluator

evaluator = ConfidenceEvaluator(config)
```

#### evaluate_confidence

评估置信度。

```python
async def evaluate_confidence(
    global_spec: GlobalSpec,
    analysis: SynthesizedAnalysis,
    user_input: UserInputData
) -> ConfidenceReport
```

## 事件 API

### EventManager

事件管理器，负责发布事件和写入 Blackboard。

```python
from src.agents.requirement_parser.event_manager import EventManager

event_manager = EventManager(agent_name="RequirementParserAgent")
```

#### publish_project_created

发布项目创建事件。

```python
async def publish_project_created(
    project_id: str,
    global_spec: GlobalSpec,
    confidence_report: ConfidenceReport,
    causation_id: Optional[str] = None,
    cost: Money = None,
    latency_ms: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> Event
```

#### publish_error_occurred

发布错误事件。

```python
async def publish_error_occurred(
    project_id: str,
    error: Exception,
    error_context: Dict[str, Any],
    causation_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Event
```

## 异常处理

### 异常层次结构

```
RequirementParserError (基类)
├── ConfigurationError (配置错误)
├── DeepSeekAPIError (API 错误)
│   ├── APITimeoutError (超时)
│   ├── APIRateLimitError (限流)
│   └── NetworkError (网络错误)
├── InputValidationError (输入验证错误)
├── InsufficientInputError (输入不足)
├── HumanInterventionRequired (需要人工介入)
└── MaxRetriesExceededError (超过最大重试次数)
```

### 异常处理示例

```python
from src.agents.requirement_parser.exceptions import (
    RequirementParserError,
    DeepSeekAPIError,
    InputValidationError,
    HumanInterventionRequired
)

try:
    result = await agent.process_user_input(user_input)
except InputValidationError as e:
    print(f"输入验证失败: {e}")
    # 提示用户修正输入
except DeepSeekAPIError as e:
    print(f"API 调用失败: {e}")
    # 检查 API 配置和网络
except HumanInterventionRequired as e:
    print(f"需要人工介入: {e}")
    # 触发人工审核流程
except RequirementParserError as e:
    print(f"处理失败: {e}")
    # 通用错误处理
```

## 最佳实践

### 1. 使用上下文管理器

```python
async with RequirementParserAgent() as agent:
    result = await agent.process_user_input(user_input)
    # Agent 会自动关闭和清理资源
```

### 2. 批量处理

```python
async def process_batch(inputs: List[UserInputData]):
    async with RequirementParserAgent() as agent:
        tasks = [agent.process_user_input(inp) for inp in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
```

### 3. 错误处理

```python
result = await agent.process_user_input(user_input)

if result.is_successful():
    # 处理成功
    global_spec = result.global_spec
    
    if result.confidence_report.recommendation == "clarify":
        # 需要澄清，但可以继续
        print("建议澄清以下问题:")
        for req in result.confidence_report.clarification_requests:
            print(f"  - {req.question}")
else:
    # 处理失败
    print(f"错误: {result.error_message}")
```

### 4. 监控和日志

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 处理并记录指标
result = await agent.process_user_input(user_input)

print(f"处理时间: {result.processing_time:.2f}s")
print(f"成本: ${result.cost:.4f}")
print(f"置信度: {result.confidence_report.overall_confidence:.2f}")
```

## 版本历史

- **v1.0.0** (2025-12-27): 初始版本
  - 多模态输入处理
  - DeepSeek API 集成
  - 置信度评估
  - 三层错误恢复
  - 全面监控和日志

## 支持

如有问题或建议，请联系：
- 邮箱: support@example.com
- 文档: [完整文档](README.md)
- 问题追踪: [GitHub Issues](https://github.com/example/issues)
