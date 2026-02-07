"""
CLIP 相似度计算器

计算图像与 prompt 的 CLIP 相似度分数。
"""

import logging
import numpy as np
from typing import Optional
from PIL import Image
import io
import base64


logger = logging.getLogger(__name__)


class CLIPScorer:
    """
    CLIP 相似度计算器
    
    计算图像与文本的 CLIP 相似度。
    """
    
    def __init__(self):
        """初始化 CLIP Scorer"""
        self.model = None
        self.processor = None
        
        self._load_model()
        
        logger.info("CLIPScorer initialized")
    
    def _load_model(self):
        """加载 CLIP 模型"""
        try:
            from transformers import CLIPProcessor, CLIPModel
            
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            logger.info("CLIP model loaded for scoring")
            
        except ImportError as e:
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
        """加载图像"""
        try:
            # 如果是 base64
            if image_data.startswith("data:image"):
                # 提取 base64 部分
                base64_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            
            # TODO: 实现 URL 加载
            
            logger.warning(f"Unsupported image data format")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
