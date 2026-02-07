"""
对象跟踪器

跟踪对象在多帧中的位置。
"""

import logging
from typing import List, Dict, Optional
import numpy as np

from ..data_structures import Detection, Track

logger = logging.getLogger(__name__)


class ObjectTracker:
    """
    对象跟踪器
    
    使用简单的 IOU 跟踪算法跟踪对象。
    """
    
    def __init__(self, iou_threshold: float = 0.3, max_age: int = 5):
        """
        初始化对象跟踪器
        
        Args:
            iou_threshold: IOU 阈值
            max_age: 最大丢失帧数
        """
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        
        self.tracks: Dict[int, Track] = {}
        self.next_track_id = 0
        
        logger.info("ObjectTracker initialized")
    
    def update(self, detections: List[Detection]) -> List[Track]:
        """
        更新跟踪
        
        Args:
            detections: 当前帧的检测结果
            
        Returns:
            List[Track]: 活跃的跟踪列表
        """
        # 匹配检测到现有跟踪
        matched_tracks = set()
        matched_detections = set()
        
        for track_id, track in self.tracks.items():
            if track.state != "active":
                continue
            
            # 获取最后一个检测的位置
            if not track.detections:
                continue
            
            last_bbox = track.detections[-1].bbox
            
            # 找到最佳匹配
            best_iou = 0
            best_detection_idx = -1
            
            for i, detection in enumerate(detections):
                if i in matched_detections:
                    continue
                
                iou = self._compute_iou(last_bbox, detection.bbox)
                
                if iou > best_iou and iou > self.iou_threshold:
                    best_iou = iou
                    best_detection_idx = i
            
            # 如果找到匹配
            if best_detection_idx >= 0:
                track.add_detection(detections[best_detection_idx])
                matched_tracks.add(track_id)
                matched_detections.add(best_detection_idx)
        
        # 创建新跟踪
        for i, detection in enumerate(detections):
            if i not in matched_detections:
                new_track = Track(track_id=self.next_track_id)
                new_track.add_detection(detection)
                self.tracks[self.next_track_id] = new_track
                self.next_track_id += 1
        
        # 更新未匹配的跟踪状态
        for track_id, track in self.tracks.items():
            if track_id not in matched_tracks and track.state == "active":
                # 增加丢失计数
                if not hasattr(track, 'lost_count'):
                    track.lost_count = 0
                track.lost_count += 1
                
                if track.lost_count > self.max_age:
                    track.state = "lost"
        
        # 返回活跃的跟踪
        active_tracks = [
            track for track in self.tracks.values()
            if track.state == "active"
        ]
        
        return active_tracks
    
    def get_all_tracks(self) -> List[Track]:
        """获取所有跟踪（包括丢失的）"""
        return list(self.tracks.values())
    
    def reset(self):
        """重置跟踪器"""
        self.tracks.clear()
        self.next_track_id = 0
    
    def _compute_iou(
        self,
        bbox1: tuple,
        bbox2: tuple
    ) -> float:
        """
        计算两个边界框的 IOU
        
        Args:
            bbox1: (x1, y1, x2, y2)
            bbox2: (x1, y1, x2, y2)
            
        Returns:
            float: IOU 值
        """
        x1_1, y1_1, x2_1, y2_1 = bbox1
        x1_2, y1_2, x2_2, y2_2 = bbox2
        
        # 计算交集
        x1_i = max(x1_1, x1_2)
        y1_i = max(y1_1, y1_2)
        x2_i = min(x2_1, x2_2)
        y2_i = min(y2_1, y2_2)
        
        if x2_i < x1_i or y2_i < y1_i:
            return 0.0
        
        intersection = (x2_i - x1_i) * (y2_i - y1_i)
        
        # 计算并集
        area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
        area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
        union = area1 + area2 - intersection
        
        if union == 0:
            return 0.0
        
        return intersection / union
