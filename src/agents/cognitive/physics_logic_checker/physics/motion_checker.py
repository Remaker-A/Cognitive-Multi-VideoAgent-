"""
运动检查器

检测物体运动的合理性，识别异常的加速/减速。
"""

import logging
from typing import List, Optional
import numpy as np

from ..data_structures import PhysicsError, Track, ErrorType, Severity

logger = logging.getLogger(__name__)


class MotionChecker:
    """
    运动检查器
    
    分析物体运动轨迹，检测突然加速/减速，验证运动连续性。
    """
    
    def __init__(self, config: Optional[dict] = None):
        """初始化运动检查器"""
        self.config = config or {}
        self.max_acceleration = self.config.get("max_acceleration", 50.0)
        self.teleport_threshold = self.config.get("teleport_threshold", 200.0)
        
        logger.info("MotionChecker initialized")
    
    def check_motion(
        self,
        tracks: List[Track],
        frames: List[np.ndarray]
    ) -> List[PhysicsError]:
        """
        检查运动异常
        
        Args:
            tracks: 对象跟踪列表
            frames: 视频帧
            
        Returns:
            List[PhysicsError]: 检测到的运动错误
        """
        errors = []
        
        for track in tracks:
            if len(track.positions) < 3:
                continue
            
            # 检测瞬移
            teleport_errors = self._detect_teleportation(track)
            errors.extend(teleport_errors)
            
            # 检测异常加速
            acceleration_errors = self._detect_abnormal_acceleration(track)
            errors.extend(acceleration_errors)
        
        logger.info(f"Motion check found {len(errors)} anomalies")
        return errors
    
    def _detect_teleportation(self, track: Track) -> List[PhysicsError]:
        """检测瞬移（位置突变）"""
        errors = []
        positions = track.positions
        
        for i in range(1, len(positions)):
            x1, y1 = positions[i-1]
            x2, y2 = positions[i]
            
            # 计算位移距离
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            
            if distance > self.teleport_threshold:
                error = PhysicsError(
                    error_type=ErrorType.MOTION_ANOMALY,
                    severity=Severity.HIGH,
                    frame_range=(
                        track.detections[i-1].frame_id,
                        track.detections[i].frame_id
                    ),
                    description=f"Object {track.track_id} teleported {distance:.1f} pixels",
                    confidence=0.9,
                    affected_objects=[track.track_id],
                    metadata={
                        "distance": float(distance),
                        "threshold": self.teleport_threshold
                    }
                )
                errors.append(error)
        
        return errors
    
    def _detect_abnormal_acceleration(self, track: Track) -> List[PhysicsError]:
        """检测异常加速"""
        errors = []
        positions = track.positions
        
        if len(positions) < 3:
            return errors
        
        # 计算速度
        velocities = []
        for i in range(1, len(positions)):
            x1, y1 = positions[i-1]
            x2, y2 = positions[i]
            velocity = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            velocities.append(velocity)
        
        # 计算加速度
        for i in range(1, len(velocities)):
            acceleration = abs(velocities[i] - velocities[i-1])
            
            if acceleration > self.max_acceleration:
                error = PhysicsError(
                    error_type=ErrorType.MOTION_ANOMALY,
                    severity=Severity.MEDIUM,
                    frame_range=(
                        track.detections[i].frame_id,
                        track.detections[i+1].frame_id
                    ),
                    description=f"Object {track.track_id} has abnormal acceleration: {acceleration:.1f}",
                    confidence=0.75,
                    affected_objects=[track.track_id],
                    metadata={
                        "acceleration": float(acceleration),
                        "threshold": self.max_acceleration
                    }
                )
                errors.append(error)
        
        return errors
