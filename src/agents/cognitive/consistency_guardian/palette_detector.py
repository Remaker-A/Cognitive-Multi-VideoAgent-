"""
色彩一致性检测器

检测图像序列的色彩一致性。
"""

import logging
import numpy as np
from typing import List, Optional
from PIL import Image
import io
import base64
from sklearn.cluster import KMeans


logger = logging.getLogger(__name__)


class PaletteDetector:
    """
    色彩一致性检测器
    
    检测图像序列的色彩风格一致性。
    """
    
    def __init__(self, n_colors: int = 5):
        """
        初始化检测器
        
        Args:
            n_colors: 提取颜色数量
        """
        self.n_colors = n_colors
        
        logger.info("PaletteDetector initialized")
    
    def check_consistency(
        self,
        images_data: List[str]
    ) -> Optional[float]:
        """
        检测一批图像的色彩一致性
        
        Args:
            images_data: 图像数据列表
            
        Returns:
            Optional[float]: 一致性分数 (0-1)
        """
        if len(images_data) < 2:
            return None
        
        try:
            # 提取每张图像的色彩
            palettes = []
            
            for img_data in images_data:
                palette = self._extract_palette(img_data)
                if palette is not None:
                    palettes.append(palette)
            
            if len(palettes) < 2:
                return None
            
            # 计算色彩一致性
            consistency = self._calculate_palette_consistency(palettes)
            
            logger.debug(f"Palette consistency: {consistency:.4f}")
            
            return consistency
            
        except Exception as e:
            logger.error(f"Palette consistency check failed: {e}", exc_info=True)
            return None
    
    def _extract_palette(self, image_data: str) -> Optional[np.ndarray]:
        """提取色彩"""
        try:
            image = self._load_image(image_data)
            
            if image is None:
                return None
            
            # 转换为 RGB 数组
            img_array = np.array(image.convert('RGB'))
            
            # 重塑为像素列表
            pixels = img_array.reshape(-1, 3)
            
            # 使用 K-means 聚类
            kmeans = KMeans(n_clusters=self.n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # 获取主色调
            colors = kmeans.cluster_centers_
            
            return colors
            
        except Exception as e:
            logger.error(f"Palette extraction failed: {e}")
            return None
    
    def _calculate_palette_consistency(
        self,
        palettes: List[np.ndarray]
    ) -> float:
        """计算色彩一致性"""
        if len(palettes) < 2:
            return 0.0
        
        # 计算相邻色彩的相似度
        similarities = []
        
        for i in range(len(palettes) - 1):
            sim = self._palette_similarity(palettes[i], palettes[i + 1])
            similarities.append(sim)
        
        # 平均相似度
        consistency = float(np.mean(similarities))
        
        return consistency
    
    def _palette_similarity(
        self,
        palette1: np.ndarray,
        palette2: np.ndarray
    ) -> float:
        """计算两个色彩的相似度"""
        # 使用最近邻匹配
        total_distance = 0.0
        
        for color1 in palette1:
            # 找到最近的颜色
            distances = [np.linalg.norm(color1 - color2) for color2 in palette2]
            min_distance = min(distances)
            total_distance += min_distance
        
        # 归一化（最大距离约为 sqrt(3 * 255^2) ≈ 441）
        max_distance = 441.0 * len(palette1)
        similarity = 1.0 - (total_distance / max_distance)
        
        return max(0.0, min(1.0, similarity))
    
    def extract_palette(self, image, n_colors=None, color_space='RGB'):
        """
        提取调色板（测试兼容方法）
        
        Args:
            image: numpy array 或 PIL Image
            n_colors: 颜色数量
            color_space: 色彩空间
            
        Returns:
            List[tuple]: 颜色列表
        """
        if n_colors is None:
            n_colors = self.n_colors
        
        try:
            # 处理 numpy array
            if isinstance(image, np.ndarray):
                img_array = image
            else:
                img_array = np.array(image.convert('RGB'))
            
            # 重塑为像素列表
            pixels = img_array.reshape(-1, 3)
            
            # 使用 K-means 聚类
            kmeans = KMeans(n_clusters=n_colors, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # 获取主色调
            colors = kmeans.cluster_centers_
            
            # 转换为 tuple 列表
            return [tuple(map(int, color)) for color in colors]
            
        except Exception as e:
            logger.error(f"Palette extraction failed: {e}")
            return []
    
    def compute_palette_similarity(self, palette1, palette2):
        """
        计算调色板相似度（测试兼容方法）
        
        Args:
            palette1: 调色板1
            palette2: 调色板2
            
        Returns:
            float: 相似度 (0-1)
        """
        if not palette1 or not palette2:
            raise ValueError("Empty palette")
        
        # 转换为 numpy 数组
        p1 = np.array(palette1, dtype=np.float32)
        p2 = np.array(palette2, dtype=np.float32)
        
        return self._palette_similarity(p1, p2)
    
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
