"""
RequirementParser Agent 数据模型定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class ProcessingStatus(Enum):
    """处理状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ConfidenceLevel(Enum):
    """置信度级别"""
    HIGH = "high"      # >= 0.8
    MEDIUM = "medium"  # 0.6 - 0.8
    LOW = "low"        # < 0.6


@dataclass
class UserInputData:
    """用户输入数据"""
    text_description: str
    reference_images: List[str] = field(default_factory=list)  # S3 URLs
    reference_videos: List[str] = field(default_factory=list)  # S3 URLs
    reference_audio: List[str] = field(default_factory=list)   # S3 URLs
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def __post_init__(self):
        """验证输入数据"""
        if not self.text_description and not any([
            self.reference_images, 
            self.reference_videos, 
            self.reference_audio
        ]):
            raise ValueError("At least text description or reference files must be provided")


@dataclass
class FileReference:
    """文件引用"""
    url: str
    size: Optional[int] = None  # bytes
    name: Optional[str] = None
    mime_type: Optional[str] = None


@dataclass
class ValidatedFile:
    """验证后的文件"""
    url: str
    file_type: str  # image, video, audio
    format: str  # file extension
    size: Optional[int] = None
    is_valid: bool = True
    validation_message: str = ""


@dataclass
class FileMetadata:
    """文件元数据"""
    total_files: int
    image_count: int
    video_count: int
    audio_count: int
    total_size: int
    formats: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class ProcessedText:
    """处理后的文本数据"""
    original: str
    cleaned: str
    language: str
    word_count: int
    key_phrases: List[str] = field(default_factory=list)
    sentiment: Optional[str] = None


@dataclass
class ProcessedImage:
    """处理后的图像数据"""
    url: str
    width: int
    height: int
    format: str
    file_size: int
    dominant_colors: List[str] = field(default_factory=list)
    thumbnail_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedVideo:
    """处理后的视频数据"""
    url: str
    duration: float  # seconds
    width: int
    height: int
    fps: float
    format: str
    file_size: int
    thumbnail_url: Optional[str] = None
    keyframes: List[str] = field(default_factory=list)  # URLs to extracted keyframes
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedAudio:
    """处理后的音频数据"""
    url: str
    duration: float  # seconds
    format: str
    file_size: int
    sample_rate: int
    channels: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessedInput:
    """预处理后的输入数据"""
    text: str  # 简化为字符串，后续由Preprocessor处理
    images: List[str] = field(default_factory=list)  # URLs
    videos: List[str] = field(default_factory=list)  # URLs
    audio: List[str] = field(default_factory=list)  # URLs
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterInfo:
    """角色信息"""
    name: str
    description: str
    role: str  # protagonist, antagonist, supporting, etc.
    traits: List[str] = field(default_factory=list)


@dataclass
class SceneInfo:
    """场景信息"""
    description: str
    location: str
    time_of_day: Optional[str] = None
    mood: str = ""
    duration_estimate: Optional[float] = None


@dataclass
class TextAnalysis:
    """文本分析结果"""
    main_theme: str
    characters: List[CharacterInfo] = field(default_factory=list)
    scenes: List[SceneInfo] = field(default_factory=list)
    mood_tags: List[str] = field(default_factory=list)
    estimated_duration: int = 30  # seconds
    narrative_structure: str = "linear"
    genre: Optional[str] = None
    target_audience: Optional[str] = None


@dataclass
class VisualStyle:
    """视觉风格分析"""
    color_palette: List[str] = field(default_factory=list)
    lighting_style: str = "natural"
    composition_style: str = "balanced"
    art_style: str = "realistic"
    reference_styles: List[str] = field(default_factory=list)
    mood_descriptors: List[str] = field(default_factory=list)


@dataclass
class MotionStyle:
    """运动风格分析"""
    camera_movement: str = "static"
    pace: str = "medium"  # slow, medium, fast
    transition_style: str = "cut"
    energy_level: str = "medium"  # low, medium, high


@dataclass
class AudioMood:
    """音频情绪分析"""
    tempo: str = "medium"  # slow, medium, fast
    energy: str = "medium"  # low, medium, high
    mood: str = "neutral"
    genre: Optional[str] = None
    instruments: List[str] = field(default_factory=list)


@dataclass
class SynthesizedAnalysis:
    """综合分析结果"""
    text_analysis: Optional[TextAnalysis]
    visual_style: Optional[VisualStyle]
    motion_style: Optional[MotionStyle]
    audio_mood: Optional[AudioMood]
    overall_theme: str = ""
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    processing_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClarificationRequest:
    """澄清请求"""
    field_name: str
    current_value: Any
    reason: str
    suggestions: List[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high


@dataclass
class ConfidenceReport:
    """置信度报告"""
    overall_confidence: float
    component_scores: Dict[str, float] = field(default_factory=dict)
    confidence_level: ConfidenceLevel = ConfidenceLevel.MEDIUM
    low_confidence_areas: List[str] = field(default_factory=list)
    clarification_requests: List[ClarificationRequest] = field(default_factory=list)
    recommendation: str = "proceed"  # proceed, clarify, human_review
    
    def __post_init__(self):
        """自动计算置信度级别"""
        if self.overall_confidence >= 0.8:
            self.confidence_level = ConfidenceLevel.HIGH
        elif self.overall_confidence >= 0.6:
            self.confidence_level = ConfidenceLevel.MEDIUM
        else:
            self.confidence_level = ConfidenceLevel.LOW


@dataclass
class StyleConfig:
    """风格配置"""
    tone: str
    palette: List[str]
    visual_dna_version: int = 1


@dataclass
class GlobalSpec:
    """全局规格数据结构"""
    title: str
    duration: int  # seconds
    aspect_ratio: str
    quality_tier: str
    resolution: str
    fps: int
    style: StyleConfig
    characters: List[str]
    mood: str
    user_options: Dict[str, Any] = field(default_factory=dict)
    # 分镜数估算 - 用于统一上下文
    estimated_shot_count: int = 0  # 估算的总分镜数
    shot_count_range: Dict[str, int] = field(default_factory=dict)  # {"min": 0, "max": 0}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "title": self.title,
            "duration": self.duration,
            "aspect_ratio": self.aspect_ratio,
            "quality_tier": self.quality_tier,
            "resolution": self.resolution,
            "fps": self.fps,
            "style": {
                "tone": self.style.tone,
                "palette": self.style.palette,
                "visual_dna_version": self.style.visual_dna_version
            },
            "characters": self.characters,
            "mood": self.mood,
            "user_options": self.user_options,
            "estimated_shot_count": self.estimated_shot_count,
            "shot_count_range": self.shot_count_range
        }


@dataclass
class ProcessingResult:
    """处理结果"""
    status: ProcessingStatus
    global_spec: Optional[GlobalSpec] = None
    confidence_report: Optional[ConfidenceReport] = None
    error_message: Optional[str] = None
    processing_time: Optional[float] = None
    cost: Optional[float] = None
    events_published: int = 0
    
    def is_successful(self) -> bool:
        """判断处理是否成功"""
        return self.status == ProcessingStatus.COMPLETED and self.global_spec is not None


@dataclass
class DeepSeekMessage:
    """DeepSeek 消息"""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class DeepSeekChoice:
    """DeepSeek 响应选项"""
    index: int
    message: DeepSeekMessage
    finish_reason: str


@dataclass
class DeepSeekUsage:
    """DeepSeek token 使用情况"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class DeepSeekRequest:
    """DeepSeek API 请求"""
    messages: List[DeepSeekMessage]
    model: str = "DeepSeek-V3.2"
    temperature: float = 0.7
    max_tokens: int = 2000
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为API请求格式"""
        return {
            "messages": [{"role": msg.role, "content": msg.content} for msg in self.messages],
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }


@dataclass
class DeepSeekResponse:
    """DeepSeek API 响应"""
    id: str
    object: str
    created: int
    model: str
    choices: List[DeepSeekChoice]
    usage: DeepSeekUsage
    
    @classmethod
    def from_api_response(cls, response: Dict[str, Any]) -> "DeepSeekResponse":
        """从API响应创建实例"""
        return cls(
            id=response.get("id", ""),
            object=response.get("object", "chat.completion"),
            created=response.get("created", 0),
            model=response.get("model", ""),
            choices=[
                DeepSeekChoice(
                    index=choice.get("index", 0),
                    message=DeepSeekMessage(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"]
                    ),
                    finish_reason=choice.get("finish_reason", "stop")
                )
                for choice in response.get("choices", [])
            ],
            usage=DeepSeekUsage(
                prompt_tokens=response.get("usage", {}).get("prompt_tokens", 0),
                completion_tokens=response.get("usage", {}).get("completion_tokens", 0),
                total_tokens=response.get("usage", {}).get("total_tokens", 0)
            )
        )


@dataclass
class MultimodalAnalysisResponse:
    """多模态分析响应"""
    analysis_text: str
    confidence: float
    tokens_used: int
    model_used: str


# Event-related models
class EventType(Enum):
    """事件类型枚举"""
    PROJECT_CREATED = "PROJECT_CREATED"
    ERROR_OCCURRED = "ERROR_OCCURRED"
    HUMAN_GATE_TRIGGERED = "HUMAN_GATE_TRIGGERED"
    HUMAN_CLARIFICATION_REQUIRED = "HUMAN_CLARIFICATION_REQUIRED"


@dataclass
class Money:
    """货币金额"""
    amount: float
    currency: str = "USD"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "amount": self.amount,
            "currency": self.currency
        }


@dataclass
class Event:
    """事件数据结构"""
    event_id: str
    project_id: str
    event_type: EventType
    actor: str
    payload: Dict[str, Any]
    causation_id: Optional[str] = None
    cost: Optional[Money] = None
    latency_ms: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "event_id": self.event_id,
            "project_id": self.project_id,
            "event_type": self.event_type.value if isinstance(self.event_type, EventType) else self.event_type,
            "actor": self.actor,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
        
        if self.causation_id:
            result["causation_id"] = self.causation_id
        if self.cost:
            result["cost"] = self.cost.to_dict()
        if self.latency_ms is not None:
            result["latency_ms"] = self.latency_ms
            
        return result


@dataclass
class BlackboardWriteRequest:
    """Blackboard 写入请求"""
    project_id: str
    path: str  # 数据路径，例如 "global_spec"
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)