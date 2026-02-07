"""
重力检查器

检测物体运动是否违反重力规律。
"""

import logging
from typing import List, Optional
import numpy as np

from ..data_structures import PhysicsError, Track, ErrorType, Severity

logger = logging.getLogger(__name__)


class GravityChecker:
    """
    重力检查器
    
    检测下落物体的运动方向，验证重力方向一致性。
    """
    
    def __init__(self, config: Optional[dict] = None):
        """初始化重力检查器"""
        self.config = config or {}
        self.gravity_threshold = self.config.get("gravity_threshold", 0.7)
        
        logger.info("GravityChecker initialized")
    
    def check_gravity(
        self,
        tracks: List[Track],
        frames: List[np.ndarray]
    ) -> List[PhysicsError]:
        """
        检查重力违反
        
        Args:
            tracks: 对象跟踪列表
            frames: 视频帧
            
        Returns:
            List[PhysicsError]: 检测到的重力错误
        """
        errors = []
        
        for track in tracks:
            if len(track.positions) < 3:
                continue  # 需要至少3个位置点
            
            # 分析垂直运动
            vertical_movement = self._analyze_vertical_movement(track)
            
            # 检测反重力
            if self._is_anti_gravity(vertical_movement):
                error = PhysicsError(
                    error_type=ErrorType.GRAVITY_VIOLATION,
                    severity=Severity.HIGH,
                    frame_range=(
                        track.detections[0].frame_id,
                        track.detections[-1].frame_id
                    ),
                    description=f"Object {track.track_id} appears to fall upward",
                    confidence=0.85,
                    affected_objects=[track.track_id],
                    metadata={
                        "vertical_direction": vertical_movement["direction"],
                        "avg_velocity": vertical_movement["avg_velocity"]
                    }
                )
                errors.append(error)
        
        logger.info(f"Gravity check found {len(errors)} violations")
        return errors
    
    def _analyze_vertical_movement(self, track: Track) -> dict:
        """分析垂直运动"""
        positions = track.positions
        
        # 计算垂直方向的位移
        vertical_displacements = []
        for i in range(1, len(positions)):
            _, y1 = positions[i-1]
            _, y2 = positions[i]
            displacement = y2 - y1  # 正值=向下，负值=向上
            vertical_displacements.append(displacement)
        
        avg_displacement = np.mean(vertical_displacements)
        
        # 判断主要方向
        if avg_displacement > 5:  # 向下
            direction = "downward"
        elif avg_displacement < -5:  # 向上
            direction = "upward"
        else:
            direction = "static"
        
        return {
            "direction": direction,
            "avg_velocity": abs(avg_displacement),
            "displacements": vertical_displacements
        }
    
    def _is_anti_gravity(self, movement: dict) -> bool:
        """判断是否违反重力"""
        # 简化版：如果物体持续向上移动，可能违反重力
        # 实际应用中需要考虑抛物线运动、飞行器等情况
        
        if movement["direction"] == "upward" and movement["avg_velocity"] > 10:
            # 检查是否是加速向上（违反重力）
            displacements = movement["displacements"]
            if len(displacements) >= 3:
                # 检查是否持续加速
                is_accelerating = all(
                    displacements[i] < displacements[i-1] 
                    for i in range(1, min(3, len(displacements)))
                )
                return is_accelerating
        
        return False
