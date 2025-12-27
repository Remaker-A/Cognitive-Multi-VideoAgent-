"""
Model 数据模型

定义模型的数据结构、类型和质量档位。
"""

from enum import Enum
from typing import Any, Dict, List
from dataclasses import dataclass, field


class ModelType(str, Enum):
    """模型类型枚举"""
    # 图像生成
    TEXT_TO_IMAGE = "TEXT_TO_IMAGE"
    IMAGE_TO_IMAGE = "IMAGE_TO_IMAGE"
    
    # 视频生成
    IMAGE_TO_VIDEO = "IMAGE_TO_VIDEO"
    TEXT_TO_VIDEO = "TEXT_TO_VIDEO"
    
    # 文本生成
    TEXT_GENERATION = "TEXT_GENERATION"
    
    # 音频生成
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    TEXT_TO_MUSIC = "TEXT_TO_MUSIC"


class QualityTier(int, Enum):
    """质量档位枚举"""
    DRAFT = 1       # 草稿质量（快速、低成本）
    STANDARD = 2    # 标准质量
    HIGH = 3        # 高质量
    PREMIUM = 4     # 顶级质量


@dataclass
class Model:
    """
    模型数据模型
    
    表示系统中的一个 AI 模型。
    """
    # 基础信息
    model_id: str
    name: str
    type: ModelType
    provider: str  # "openai", "anthropic", "stability", "runway", etc.
    
    # 能力
    capabilities: List[str] = field(default_factory=list)
    quality_tier: QualityTier = QualityTier.STANDARD
    
    # 成本
    cost_per_unit: float = 0.0
    unit_type: str = "image"  # "image", "second", "token", "character"
    
    # 性能
    avg_latency_ms: int = 3000
    max_concurrent: int = 10
    
    # 配置
    config: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "model_id": self.model_id,
            "name": self.name,
            "type": self.type.value if isinstance(self.type, ModelType) else self.type,
            "provider": self.provider,
            "capabilities": self.capabilities,
            "quality_tier": self.quality_tier.value if isinstance(self.quality_tier, QualityTier) else self.quality_tier,
            "cost_per_unit": self.cost_per_unit,
            "unit_type": self.unit_type,
            "avg_latency_ms": self.avg_latency_ms,
            "max_concurrent": self.max_concurrent,
            "config": self.config,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Model':
        """从字典创建"""
        model_type = ModelType(data["type"]) if isinstance(data["type"], str) else data["type"]
        quality_tier = QualityTier(data["quality_tier"]) if isinstance(data["quality_tier"], int) else data["quality_tier"]
        
        return cls(
            model_id=data.get("model_id", ""),
            name=data.get("name", ""),
            type=model_type,
            provider=data.get("provider", ""),
            capabilities=data.get("capabilities", []),
            quality_tier=quality_tier,
            cost_per_unit=data.get("cost_per_unit", 0.0),
            unit_type=data.get("unit_type", "image"),
            avg_latency_ms=data.get("avg_latency_ms", 3000),
            max_concurrent=data.get("max_concurrent", 10),
            config=data.get("config", {}),
            is_active=data.get("is_active", True)
        )
    
    def __repr__(self) -> str:
        return f"Model(id={self.model_id}, name={self.name}, tier={self.quality_tier.name})"
