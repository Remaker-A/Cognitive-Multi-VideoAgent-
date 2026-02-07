"""
光照检测器

检测图像间的光照变化。
"""

import logging
import numpy as np
from typing import Optional
from PIL import Image
import io
import base64
import cv2


logger = logging.getLogger(__name__)


class LightingDetector:
    """
    光照检测器
    
    检测图像间的光照一致性和突变。
    """
    
    def __init__(self):
        """初始化检测器"""
        logger.info("LightingDetector initialized")
    
    def detect_lighting_change(
        self,
        image1_data: str,
        image2_data: str
    ) -> Optional[float]:
        """
        检测光照变化
        
        Args:
            image1_data: 图像1数据
            image2_data: 图像2数据
            
        Returns:
            Optional[float]: 光照一致性分数 (0-1)，1 表示完全一致
        """
        try:
            # 加载图像
            image1 = self._load_image(image1_data)
            image2 = self._load_image(image2_data)
            
            if image1 is None or image2 is None:
                return None
            
            # 转换为 numpy 数组
            img1_array = np.array(image1.convert('RGB'))
            img2_array = np.array(image2.convert('RGB'))
            
            # 计算亮度直方图
            hist1 = self._calculate_brightness_histogram(img1_array)
            hist2 = self._calculate_brightness_histogram(img2_array)
            
            # 比较直方图
            consistency = self._compare_histograms(hist1, hist2)
            
            logger.debug(f"Lighting consistency: {consistency:.4f}")
            
            return consistency
            
        except Exception as e:
            logger.error(f"Lighting detection failed: {e}", exc_info=True)
            return None
    
    def _calculate_brightness_histogram(
        self,
        image_array: np.ndarray,
        bins: int = 256
    ) -> np.ndarray:
        """计算亮度直方图"""
        # 转换为灰度
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        
        # 计算直方图
        hist, _ = np.histogram(gray, bins=bins, range=(0, 256))
        
        # 归一化
        hist = hist.astype(float) / hist.sum()
        
        return hist
    
    def _compare_histograms(
        self,
        hist1: np.ndarray,
        hist2: np.ndarray
    ) -> float:
        """
        比较两个直方图
        
        使用巴氏距离（Bhattacharyya distance）
        """
        # 计算巴氏系数
        bc = np.sum(np.sqrt(hist1 * hist2))
        
        # 转换为相似度（1 - 巴氏距离）
        similarity = bc
        
        return float(similarity)
    
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
