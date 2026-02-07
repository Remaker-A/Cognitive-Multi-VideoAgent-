"""
Embedding 提取器

从图像中提取 embedding 向量。
"""

import logging
import numpy as np
from typing import Optional
from PIL import Image
import io
import base64


logger = logging.getLogger(__name__)


class EmbeddingExtractor:
    """
    Embedding 提取器
    
    使用 CLIP 或其他模型提取图像 embedding。
    """
    
    def __init__(self, model_name: str = "clip"):
        """
        初始化提取器
        
        Args:
            model_name: 模型名称 ("clip" 或 "dinov2")
        """
        self.model_name = model_name
        self.model = None
        
        # 延迟加载模型
        self._load_model()
        
        logger.info(f"EmbeddingExtractor initialized with model: {model_name}")
    
    def _load_model(self):
        """加载模型"""
        try:
            if self.model_name == "clip":
                # 使用 transformers 的 CLIP
                from transformers import CLIPProcessor, CLIPModel
                
                self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
                self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
                
                logger.info("CLIP model loaded successfully")
            
            elif self.model_name == "dinov2":
                # DINOv2 - 更好的视觉表示
                # TODO: 实现 DINOv2
                logger.warning("DINOv2 not implemented, using CLIP")
                self._load_model()  # 回退到 CLIP
        
        except ImportError as e:
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
