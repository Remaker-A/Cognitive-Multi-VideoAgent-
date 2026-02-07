"""
特征提取器

从图像中提取视觉特征（面部、色彩、纹理等）。
"""

import logging
import numpy as np
from typing import Dict, Any, Optional
from PIL import Image
import io
import base64
from sklearn.cluster import KMeans


logger = logging.getLogger(__name__)


class FeatureExtractor:
    """
    特征提取器
    
    提取图像的多种视觉特征。
    """
    
    def __init__(self):
        """初始化提取器"""
        self.face_model = None
        self.clip_model = None
        
        self._load_models()
        
        logger.info("FeatureExtractor initialized")
    
    def _load_models(self):
        """加载模型"""
        try:
            # 加载 CLIP 用于通用特征
            from transformers import CLIPModel, CLIPProcessor
            
            self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            logger.info("CLIP model loaded for feature extraction")
            
            # TODO: 加载 InsightFace 用于面部特征
            # from insightface.app import FaceAnalysis
            # self.face_model = FaceAnalysis()
            
        except ImportError as e:
            logger.error(f"Failed to load models: {e}")
    
    def extract_features(self, image_data: str) -> Dict[str, Any]:
        """
        提取所有特征
        
        Args:
            image_data: 图像数据（base64 或 URL）
            
        Returns:
            Dict: 特征字典
        """
        try:
            # 加载图像
            image = self._load_image(image_data)
            
            if image is None:
                return self._empty_features()
            
            # 提取各种特征
            features = {
                "face_embedding": self.extract_face(image),
                "palette": self.extract_colors(image),
                "texture": self.extract_texture(image),
                "composition": self.analyze_composition(image),
                "general_embedding": self.extract_general_embedding(image)
            }
            
            # 计算置信度
            features["confidence"] = self.calculate_confidence(features)
            
            logger.debug(f"Extracted features with confidence: {features['confidence']:.4f}")
            
            return features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}", exc_info=True)
            return self._empty_features()
    
    def extract_face(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        提取面部 embedding
        
        Args:
            image: PIL Image
            
        Returns:
            Optional[np.ndarray]: 面部 embedding
        """
        # TODO: 使用 InsightFace 提取面部特征
        # 这里使用 CLIP 作为替代
        
        if self.clip_model is None:
            return None
        
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**inputs)
            embedding = image_features.detach().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Face extraction failed: {e}")
            return None
    
    def extract_colors(self, image: Image.Image, n_colors: int = 5) -> Dict[str, Any]:
        """
        提取主色调
        
        Args:
            image: PIL Image
            n_colors: 提取颜色数量
            
        Returns:
            Dict: 色彩信息
        """
        try:
            # 转换为 RGB 数组
            img_array = np.array(image.convert('RGB'))
            
            # 重塑为像素列表
            pixels = img_array.reshape(-1, 3)
            
            # 使用 K-means 聚类
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # 获取主色调
            colors = kmeans.cluster_centers_.astype(int)
            
            # 计算每个颜色的占比
            labels = kmeans.labels_
            counts = np.bincount(labels)
            percentages = counts / len(labels)
            
            # 按占比排序
            sorted_indices = np.argsort(percentages)[::-1]
            
            palette = {
                "dominant_colors": [
                    {
                        "rgb": colors[i].tolist(),
                        "hex": self._rgb_to_hex(colors[i]),
                        "percentage": float(percentages[i])
                    }
                    for i in sorted_indices
                ]
            }
            
            return palette
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return {"dominant_colors": []}
    
    def extract_texture(self, image: Image.Image) -> Dict[str, Any]:
        """
        提取纹理特征
        
        Args:
            image: PIL Image
            
        Returns:
            Dict: 纹理信息
        """
        try:
            # 转换为灰度
            gray = np.array(image.convert('L'))
            
            # 计算简单的纹理统计
            texture = {
                "mean": float(np.mean(gray)),
                "std": float(np.std(gray)),
                "contrast": float(gray.max() - gray.min())
            }
            
            return texture
            
        except Exception as e:
            logger.error(f"Texture extraction failed: {e}")
            return {}
    
    def analyze_composition(self, image: Image.Image) -> Dict[str, Any]:
        """
        分析构图
        
        Args:
            image: PIL Image
            
        Returns:
            Dict: 构图信息
        """
        try:
            width, height = image.size
            
            composition = {
                "aspect_ratio": width / height,
                "resolution": {"width": width, "height": height}
            }
            
            return composition
            
        except Exception as e:
            logger.error(f"Composition analysis failed: {e}")
            return {}
    
    def extract_general_embedding(self, image: Image.Image) -> Optional[np.ndarray]:
        """
        提取通用 embedding
        
        Args:
            image: PIL Image
            
        Returns:
            Optional[np.ndarray]: Embedding
        """
        if self.clip_model is None:
            return None
        
        try:
            inputs = self.clip_processor(images=image, return_tensors="pt")
            image_features = self.clip_model.get_image_features(**inputs)
            embedding = image_features.detach().numpy()[0]
            embedding = embedding / np.linalg.norm(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"General embedding extraction failed: {e}")
            return None
    
    def calculate_confidence(self, features: Dict[str, Any]) -> float:
        """
        计算特征置信度
        
        Args:
            features: 特征字典
            
        Returns:
            float: 置信度 (0-1)
        """
        confidence = 0.0
        count = 0
        
        # 检查各个特征是否成功提取
        if features.get("face_embedding") is not None:
            confidence += 0.4
            count += 1
        
        if features.get("palette") and features["palette"].get("dominant_colors"):
            confidence += 0.3
            count += 1
        
        if features.get("texture"):
            confidence += 0.2
            count += 1
        
        if features.get("general_embedding") is not None:
            confidence += 0.1
            count += 1
        
        return confidence
    
    def _load_image(self, image_data: str) -> Optional[Image.Image]:
        """加载图像"""
        try:
            if image_data.startswith("data:image"):
                base64_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            
            # TODO: 实现 URL 加载
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to load image: {e}")
            return None
    
    def _rgb_to_hex(self, rgb: np.ndarray) -> str:
        """RGB 转 HEX"""
        return "#{:02x}{:02x}{:02x}".format(rgb[0], rgb[1], rgb[2])
    
    def _empty_features(self) -> Dict[str, Any]:
        """返回空特征"""
        return {
            "face_embedding": None,
            "palette": {"dominant_colors": []},
            "texture": {},
            "composition": {},
            "general_embedding": None,
            "confidence": 0.0
        }
