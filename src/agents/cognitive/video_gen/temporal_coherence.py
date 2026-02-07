"""
时间连贯性计算

计算视频的时间连贯性分数。
"""

import logging
import cv2
import numpy as np
from typing import Optional
from skimage.metrics import structural_similarity as ssim


logger = logging.getLogger(__name__)


class TemporalCoherence:
    """
    时间连贯性计算器
    
    使用 SSIM 和特征相似度计算帧间一致性。
    """
    
    def __init__(self):
        """初始化计算器"""
        logger.info("TemporalCoherence initialized")
    
    def calculate(self, video_path: str) -> Optional[float]:
        """
        计算时间连贯性
        
        Args:
            video_path: 视频路径
            
        Returns:
            Optional[float]: 连贯性分数 (0-1)
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return None
            
            ssim_scores = []
            prev_frame = None
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # 转换为灰度
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                
                if prev_frame is not None:
                    # 计算 SSIM
                    score = ssim(prev_frame, gray)
                    ssim_scores.append(score)
                
                prev_frame = gray
            
            cap.release()
            
            if not ssim_scores:
                logger.warning("No frames to compare")
                return None
            
            # 平均 SSIM 分数
            coherence_score = float(np.mean(ssim_scores))
            
            logger.info(f"Temporal coherence: {coherence_score:.4f}")
            
            return coherence_score
            
        except Exception as e:
            logger.error(f"Temporal coherence calculation failed: {e}", exc_info=True)
            return None
