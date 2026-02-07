"""
CLIP 相似度检测器

检测图像之间的 CLIP 相似度。
"""

import logging
import numpy as np
from typing import Optional, List
from PIL import Image
import io
import base64


logger = logging.getLogger(__name__)


class CLIPDetector:
    """
    CLIP 相似度检测器
    
    使用 CLIP 模型检测图像相似度。
    """
    
    def __init__(self):
        """初始化检测器"""
        self.model = None
        self.processor = None
        
        self._load_model()
        
        logger.info("CLIPDetector initialized")
    
    def _load_model(self):
        """加载 CLIP 模型"""
        try:
            from transformers import CLIPModel, CLIPProcessor
            
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            logger.info("CLIP model loaded for similarity detection")
            
        except ImportError as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
    
    def check_similarity(
        self,
        image1_data: str,
        image2_data: str
    ) -> Optional[float]:
        """
        检测两张图像的相似度
        
        Args:
            image1_data: 图像1数据
            image2_data: 图像2数据
            
        Returns:
            Optional[float]: 相似度分数 (0-1)
        """
        if self.model is None:
            logger.warning("CLIP model not loaded")
            return None
        
        try:
            # 加载图像
            image1 = self._load_image(image1_data)
            image2 = self._load_image(image2_data)
            
            if image1 is None or image2 is None:
                return None
            
            # 提取特征
            emb1 = self._extract_embedding(image1)
            emb2 = self._extract_embedding(image2)
            
            if emb1 is None or emb2 is None:
                return None
            
            # 计算余弦相似度
            similarity = float(np.dot(emb1, emb2))
            
            logger.debug(f"CLIP similarity: {similarity:.4f}")
            
            return similarity
            
        except Exception as e:
            logger.error(f"Similarity check failed: {e}", exc_info=True)
            return None
    
    def check_batch_similarity(
        self,
        images_data: List[str]
    ) -> Optional[List[float]]:
        """
        检测一批图像的相邻相似度
        
        Args:
            images_data: 图像数据列表
            
        Returns:
            Optional[List[float]]: 相似度分数列表
        """
        if len(images_data) < 2:
            return []
        
        similarities = []
        
        for i in range(len(images_data) - 1):
            sim = self.check_similarity(images_data[i], images_data[i + 1])
            if sim is not None:
                similarities.append(sim)
        
        return similarities
    
    def _extract_embedding(self, image: Image.Image) -> Optional[np.ndarray]:
        """提取图像 embedding"""
        try:
            inputs = self.processor(images=image, return_tensors="pt")
            image_features = self.model.get_image_features(**inputs)
            embedding = image_features.detach().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            return None
    
    def _load_image(self, image_data: str) -> Optional[Image.Image]:
        """加载图像"""
        try:
            if image_data.startswith("data:image"):
                base64_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
