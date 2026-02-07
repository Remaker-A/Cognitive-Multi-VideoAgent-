"""
Embedding 提取器

从图像中提取 embedding 向量。

优化：
- 使用共享模型管理器（节省~600MB内存）
- 使用图像解码缓存（避免重复解码）
"""

import logging
import numpy as np
from typing import Optional
from PIL import Image

# 导入性能优化组件
from src.infrastructure.performance import model_manager, image_decode_cache


logger = logging.getLogger(__name__)


class EmbeddingExtractor:
    """
    Embedding 提取器

    使用 CLIP 或其他模型提取图像 embedding。

    优化特性：
    - 使用共享模型管理器，与CLIPScorer共享同一模型实例
    - 使用图像解码缓存，避免重复解码相同图像
    """

    def __init__(self, model_name: str = "clip"):
        """
        初始化提取器

        Args:
            model_name: 模型名称 ("clip" 或 "dinov2")
        """
        self.model_name = model_name
        self.model = None
        self.processor = None

        # 延迟加载模型
        self._load_model()

        logger.info(f"EmbeddingExtractor initialized with model: {model_name} (using shared manager)")

    def _load_model(self):
        """加载模型 - 从共享管理器获取"""
        try:
            if self.model_name == "clip":
                # 从共享模型管理器获取模型（与CLIPScorer共享同一实例）
                self.model, self.processor = model_manager.get_clip_model()

                logger.info("CLIP model loaded from shared manager for embedding extraction")

            elif self.model_name == "dinov2":
                # DINOv2 - 更好的视觉表示
                # TODO: 实现 DINOv2
                logger.warning("DINOv2 not implemented, using CLIP")
                self.model_name = "clip"
                self._load_model()  # 回退到 CLIP

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.warning("Embedding extraction will be disabled")
            self.model = None
    
    def extract(self, image_data: str) -> Optional[np.ndarray]:
        """
        提取 embedding
        
        Args:
            image_data: 图像数据（base64 或 URL）
            
        Returns:
            Optional[np.ndarray]: Embedding 向量
        """
        if self.model is None:
            logger.warning("Model not loaded, skipping embedding extraction")
            return None
        
        try:
            # 加载图像
            image = self._load_image(image_data)
            
            if image is None:
                return None
            
            # 提取 embedding
            if self.model_name == "clip":
                return self._extract_clip(image)
            
            return None
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}", exc_info=True)
            return None
    
    def _load_image(self, image_data: str) -> Optional[Image.Image]:
        """
        加载图像 - 使用缓存避免重复解码

        Args:
            image_data: 图像数据（base64、URL或文件路径）

        Returns:
            Optional[Image.Image]: PIL图像对象
        """
        try:
            # 使用图像解码缓存（避免重复解码相同图像）
            return image_decode_cache.get_or_decode(image_data)

        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def _extract_clip(self, image: Image.Image) -> np.ndarray:
        """使用 CLIP 提取 embedding"""
        # 预处理图像
        inputs = self.processor(images=image, return_tensors="pt")
        
        # 提取特征
        image_features = self.model.get_image_features(**inputs)
        
        # 转换为 numpy
        embedding = image_features.detach().numpy()[0]
        
        # 归一化
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding
