"""
CLIP 相似度计算器

计算图像与 prompt 的 CLIP 相似度分数。

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


class CLIPScorer:
    """
    CLIP 相似度计算器

    计算图像与文本的 CLIP 相似度。

    优化特性：
    - 使用共享模型管理器，多个组件共享同一CLIP模型实例
    - 使用图像解码缓存，避免重复解码相同图像
    """

    def __init__(self):
        """初始化 CLIP Scorer - 使用共享模型"""
        self.model = None
        self.processor = None

        self._load_model()

        logger.info("CLIPScorer initialized (using shared model manager)")

    def _load_model(self):
        """加载 CLIP 模型 - 从共享管理器获取"""
        try:
            # 从共享模型管理器获取模型（单例，所有组件共享）
            self.model, self.processor = model_manager.get_clip_model()

            logger.info("CLIP model loaded from shared manager for scoring")

        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            logger.warning("CLIP scoring will be disabled")
            self.model = None
    
    def calculate_similarity(
        self,
        image_data: str,
        prompt: str
    ) -> Optional[float]:
        """
        计算相似度
        
        Args:
            image_data: 图像数据（base64 或 URL）
            prompt: 文本 prompt
            
        Returns:
            Optional[float]: 相似度分数 (0-1)
        """
        if self.model is None:
            logger.warning("CLIP model not loaded, returning default score")
            return 0.8  # 默认分数
        
        try:
            # 加载图像
            image = self._load_image(image_data)
            
            if image is None:
                return None
            
            # 预处理
            inputs = self.processor(
                text=[prompt],
                images=image,
                return_tensors="pt",
                padding=True
            )
            
            # 计算相似度
            outputs = self.model(**inputs)
            
            # 获取 logits
            logits_per_image = outputs.logits_per_image
            
            # 转换为概率（使用 sigmoid）
            probs = logits_per_image.sigmoid()
            
            # 获取相似度分数
            score = float(probs[0][0].item())
            
            logger.debug(f"CLIP similarity: {score:.4f}")
            
            return score
            
        except Exception as e:
            logger.error(f"CLIP scoring failed: {e}", exc_info=True)
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
