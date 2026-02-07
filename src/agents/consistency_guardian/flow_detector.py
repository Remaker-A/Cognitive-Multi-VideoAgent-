"""
光流流畅度检测器

检测视频的运动流畅度。
"""

import logging
import cv2
import numpy as np
from typing import Optional, Dict


logger = logging.getLogger(__name__)


class FlowDetector:
    """
    光流流畅度检测器
    
    使用光流分析检测视频运动流畅度。
    """
    
    def __init__(self):
        """初始化检测器"""
        logger.info("FlowDetector initialized")
    
    def check_smoothness(self, video_path: str) -> Optional[float]:
        """
        检测视频的运动流畅度
        
        Args:
            video_path: 视频路径
            
        Returns:
            Optional[float]: 流畅度分数 (0-1)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return None
            
            ret, prev_frame = cap.read()
            
            if not ret:
                logger.error("Failed to read first frame")
                return None
            
            prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            
            flow_magnitudes = []
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                # 计算光流
                flow = cv2.calcOpticalFlowFarneback(
                    prev_gray,
                    gray,
                    None,
                    pyr_scale=0.5,
                    levels=3,
                    winsize=15,
                    iterations=3,
                    poly_n=5,
                    poly_sigma=1.2,
                    flags=0
                )
                
                # 计算流的幅度
                magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                
                # 平均幅度
                avg_magnitude = float(np.mean(magnitude))
                flow_magnitudes.append(avg_magnitude)
                
                prev_gray = gray
            
            cap.release()
            
            if not flow_magnitudes:
                logger.warning("No optical flow data")
                return None
            
            # 计算流畅度
            smoothness = self._calculate_smoothness(flow_magnitudes)
            
            logger.debug(f"Flow smoothness: {smoothness:.4f}")
            
            return smoothness
            
        except Exception as e:
            logger.error(f"Flow smoothness check failed: {e}", exc_info=True)
            return None
    
    def _calculate_smoothness(self, magnitudes: list) -> float:
        """
        计算运动流畅度
        
        流畅度 = 1 - (标准差 / 平均值)
        """
        if not magnitudes:
            return 0.0
        
        mean_val = np.mean(magnitudes)
        std_val = np.std(magnitudes)
        
        if mean_val == 0:
            return 0.0
        
        smoothness = 1.0 - min(1.0, std_val / mean_val)
        
        return float(smoothness)
