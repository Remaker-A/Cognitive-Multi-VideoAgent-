"""
连续性错误检测器

检测人物/物体突然消失或出现的连续性错误。
"""

import logging
from typing import List, Dict, Optional, Set
import numpy as np

from ..data_structures import LogicError, Track, ErrorType, Severity

logger = logging.getLogger(__name__)


class ContinuityErrorDetector:
    """
    连续性错误检测器
    
    检测人物/物体突然消失、突然出现等连续性问题。
    """
    
    def __init__(self, config: Optional[dict] = None):
        """初始化连续性错误检测器"""
        self.config = config or {}
        self.min_track_length = self.config.get("min_track_length", 5)
        self.disappearance_threshold = self.config.get("disappearance_threshold", 3)
        
        logger.info("ContinuityErrorDetector initialized")
    
    def check_continuity(
        self,
        tracks: List[Track],
        frames: List[np.ndarray]
    ) -> List[LogicError]:
        """
        检查连续性错误
        
        Args:
            tracks: 对象跟踪列表
            frames: 视频帧
            
        Returns:
            List[LogicError]: 检测到的连续性错误
        """
        errors = []
        
        # 检测突然消失
        disappearance_errors = self._detect_disappearance(tracks, frames)
        errors.extend(disappearance_errors)
        
        # 检测突然出现
        appearance_errors = self._detect_appearance(tracks, frames)
        errors.extend(appearance_errors)
        
        logger.info(f"Continuity check found {len(errors)} errors")
        return errors
    
    def _detect_disappearance(
        self,
        tracks: List[Track],
        frames: List[np.ndarray]
    ) -> List[LogicError]:
        """检测物体突然消失"""
        errors = []
        
        for track in tracks:
            if len(track.detections) < self.min_track_length:
                continue
            
            # 检查跟踪是否突然中断（非自然离场）
            if track.state == "lost":
                last_detection = track.detections[-1]
                last_frame_id = last_detection.frame_id
                
                # 如果物体在画面中央突然消失，可能是连续性错误
                if self._is_in_center_region(last_detection, frames[0]):
                    error = LogicError(
                        error_type=ErrorType.CONTINUITY_ERROR,
                        severity=Severity.MEDIUM,
                        frame_range=(last_frame_id, last_frame_id + 1),
                        description=f"Object {track.track_id} ({last_detection.class_name}) "
                                  f"disappeared without leaving the frame",
                        confidence=0.75,
                        affected_objects=[track.track_id],
                        metadata={
                            "last_position": last_detection.bbox,
                            "track_length": len(track.detections)
                        }
                    )
                    errors.append(error)
        
        return errors
    
    def _detect_appearance(
        self,
        tracks: List[Track],
        frames: List[np.ndarray]
    ) -> List[LogicError]:
        """检测物体突然出现"""
        errors = []
        
        for track in tracks:
            if len(track.detections) < self.min_track_length:
                continue
            
            first_detection = track.detections[0]
            first_frame_id = first_detection.frame_id
            
            # 如果物体在画面中央突然出现（非从边缘进入），可能是连续性错误
            if first_frame_id > 0 and self._is_in_center_region(first_detection, frames[0]):
                error = LogicError(
                    error_type=ErrorType.CONTINUITY_ERROR,
                    severity=Severity.MEDIUM,
                    frame_range=(first_frame_id - 1, first_frame_id),
                    description=f"Object {track.track_id} ({first_detection.class_name}) "
                              f"appeared without entering from frame edge",
                    confidence=0.70,
                    affected_objects=[track.track_id],
                    metadata={
                        "first_position": first_detection.bbox,
                        "track_length": len(track.detections)
                    }
                )
                errors.append(error)
        
        return errors
    
    def _is_in_center_region(self, detection, reference_frame: np.ndarray) -> bool:
        """判断物体是否在画面中央区域"""
        h, w = reference_frame.shape[:2]
        x1, y1, x2, y2 = detection.bbox
        
        # 计算物体中心
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        # 定义中央区域（画面中央 60%）
        margin_x = w * 0.2
        margin_y = h * 0.2
        
        return (margin_x < center_x < w - margin_x and 
                margin_y < center_y < h - margin_y)
