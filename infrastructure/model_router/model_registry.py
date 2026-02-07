"""
模型注册表

管理所有可用的 AI 模型。
"""

import logging
from typing import Dict, List, Optional

from .model import Model, ModelType, QualityTier


logger = logging.getLogger(__name__)


# 预定义模型
PREDEFINED_MODELS = {
    # 图像生成 - DRAFT
    "sdxl-turbo": Model(
        model_id="sdxl-turbo",
        name="SDXL Turbo",
        type=ModelType.TEXT_TO_IMAGE,
        provider="stability",
        capabilities=["text-to-image", "fast"],
        quality_tier=QualityTier.DRAFT,
        cost_per_unit=0.01,
        unit_type="image",
        avg_latency_ms=1000
    ),
    
    # 图像生成 - STANDARD
    "sdxl": Model(
        model_id="sdxl",
        name="SDXL",
        type=ModelType.TEXT_TO_IMAGE,
        provider="stability",
        capabilities=["text-to-image", "controlnet", "inpainting"],
        quality_tier=QualityTier.STANDARD,
        cost_per_unit=0.04,
        unit_type="image",
        avg_latency_ms=3000
    ),
    
    # 图像生成 - HIGH
    "midjourney-v6": Model(
        model_id="midjourney-v6",
        name="Midjourney V6",
        type=ModelType.TEXT_TO_IMAGE,
        provider="midjourney",
        capabilities=["text-to-image", "high-quality"],
        quality_tier=QualityTier.HIGH,
        cost_per_unit=0.08,
        unit_type="image",
        avg_latency_ms=5000
    ),
    
    # 视频生成 - STANDARD
    "runway-gen2": Model(
        model_id="runway-gen2",
        name="Runway Gen-2",
        type=ModelType.IMAGE_TO_VIDEO,
        provider="runway",
        capabilities=["image-to-video"],
        quality_tier=QualityTier.STANDARD,
        cost_per_unit=0.30,
        unit_type="second",
        avg_latency_ms=10000
    ),
    
    # 视频生成 - HIGH
    "runway-gen3": Model(
        model_id="runway-gen3",
        name="Runway Gen-3",
        type=ModelType.IMAGE_TO_VIDEO,
        provider="runway",
        capabilities=["image-to-video", "high-quality"],
        quality_tier=QualityTier.HIGH,
        cost_per_unit=0.50,
        unit_type="second",
        avg_latency_ms=15000
    ),
    
    # 文本生成
    "gpt-4": Model(
        model_id="gpt-4",
        name="GPT-4",
        type=ModelType.TEXT_GENERATION,
        provider="openai",
        capabilities=["text-generation", "reasoning"],
        quality_tier=QualityTier.HIGH,
        cost_per_unit=0.03,
        unit_type="1k_tokens",
        avg_latency_ms=2000
    ),
}


class ModelRegistry:
    """
    模型注册表
    
    管理所有可用的 AI 模型。
    """
    
    def __init__(self):
        """初始化注册表"""
        self.models: Dict[str, Model] = {}
        self._load_predefined_models()
    
    def _load_predefined_models(self) -> None:
        """加载预定义模型"""
        for model_id, model in PREDEFINED_MODELS.items():
            self.models[model_id] = model
        logger.info(f"Loaded {len(self.models)} predefined models")
    
    def register_model(self, model: Model) -> bool:
        """
        注册模型
        
        Args:
            model: 模型对象
            
        Returns:
            bool: 是否成功注册
        """
        if model.model_id in self.models:
            logger.warning(f"Model {model.model_id} already exists, updating")
        
        self.models[model.model_id] = model
        logger.info(f"Registered model: {model.model_id}")
        return True
    
    def get_model(self, model_id: str) -> Optional[Model]:
        """
        获取模型
        
        Args:
            model_id: 模型 ID
            
        Returns:
            Optional[Model]: 模型对象
        """
        return self.models.get(model_id)
    
    def list_models(self, filters: Optional[Dict] = None) -> List[Model]:
        """
        列出模型
        
        Args:
            filters: 过滤条件
            
        Returns:
            List[Model]: 模型列表
        """
        models = list(self.models.values())
        
        if not filters:
            return models
        
        # 过滤类型
        if "type" in filters:
            model_type = filters["type"]
            models = [m for m in models if m.type == model_type]
        
        # 过滤质量档位
        if "quality_tier" in filters:
            quality_tier = filters["quality_tier"]
            models = [m for m in models if m.quality_tier == quality_tier]
        
        # 过滤激活状态
        if "is_active" in filters:
            is_active = filters["is_active"]
            models = [m for m in models if m.is_active == is_active]
        
        return models
    
    def update_model(self, model_id: str, updates: Dict) -> bool:
        """
        更新模型
        
        Args:
            model_id: 模型 ID
            updates: 更新字段
            
        Returns:
            bool: 是否成功更新
        """
        if model_id not in self.models:
            logger.error(f"Model {model_id} not found")
            return False
        
        model = self.models[model_id]
        
        for key, value in updates.items():
            if hasattr(model, key):
                setattr(model, key, value)
        
        logger.info(f"Updated model: {model_id}")
        return True
    
    def deactivate_model(self, model_id: str) -> bool:
        """
        停用模型
        
        Args:
            model_id: 模型 ID
            
        Returns:
            bool: 是否成功停用
        """
        return self.update_model(model_id, {"is_active": False})
