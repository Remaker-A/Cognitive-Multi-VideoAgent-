"""
运动分析器

分析对象的运动轨迹、速度和加速度。
"""

import logging
from typing import List, Tuple, Optional
import numpy as np

from ..data_structures import Track

logger = logging.getLogger(__name__)


class MotionAnalyzer:
    """
    运动分析器
    
    分析对象运动轨迹，计算速度和加速度。
    """
    
    def __init__(self):
        """初始化运动分析器"""
        logger.info("MotionAnalyzer initialized")
    
    def analyze_trajectory(self, track: Track) -> dict:
        """
        分析轨迹
        
        Args:
            track: 对象跟踪
            
        Returns:
            dict: 分析结果
        """
        if len(track.positions) < 2:
            return {
                "avg_velocity": 0.0,
                "max_velocity": 0.0,
                "avg_acceleration": 0.0,
                "max_acceleration": 0.0,
                "total_distance": 0.0
            }
        
        velocities = self.compute_velocity(track.positions)
        accelerations = self.compute_acceleration(velocities)
        total_distance = self.compute_total_distance(track.positions)
        
        return {
            "avg_velocity": float(np.mean(velocities)) if velocities else 0.0,
            "max_velocity": float(np.max(velocities)) if velocities else 0.0,
            "avg_acceleration": float(np.mean(np.abs(accelerations))) if accelerations else 0.0,
            "max_acceleration": float(np.max(np.abs(accelerations))) if accelerations else 0.0,
            "total_distance": total_distance,
            "velocities": velocities,
            "accelerations": accelerations
        }
    
    def compute_velocity(self, positions: List[Tuple[float, float]]) -> List[float]:
        """
        计算速度
        
        Args:
            positions: 位置列表 [(x, y), ...]
            
        Returns:
            List[float]: 速度列表
        """
        if len(positions) < 2:
            return []
        
        velocities = []
        for i in range(1, len(positions)):
            x1, y1 = positions[i-1]
            x2, y2 = positions[i]
            
            # 计算欧氏距离
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            velocities.append(distance)
        
        return velocities
    
    def compute_acceleration(self, velocities: List[float]) -> List[float]:
        """
        计算加速度
        
        Args:
            velocities: 速度列表
            
        Returns:
            List[float]: 加速度列表
        """
        if len(velocities) < 2:
            return []
        
        accelerations = []
        for i in range(1, len(velocities)):
            acceleration = velocities[i] - velocities[i-1]
            accelerations.append(acceleration)
        
        return accelerations
    
    def compute_total_distance(self, positions: List[Tuple[float, float]]) -> float:
        """
        计算总移动距离
        
        Args:
            positions: 位置列表
            
        Returns:
            float: 总距离
        """
        if len(positions) < 2:
            return 0.0
        
        total = 0.0
        for i in range(1, len(positions)):
            x1, y1 = positions[i-1]
            x2, y2 = positions[i]
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total += distance
        
        return total
    
    def detect_sudden_changes(
        self,
        track: Track,
        velocity_threshold: float = 50.0,
        acceleration_threshold: float = 30.0
    ) -> dict:
        """
        检测突然变化
        
        Args:
            track: 对象跟踪
            velocity_threshold: 速度阈值
            acceleration_threshold: 加速度阈值
            
        Returns:
            dict: 检测结果
        """
        analysis = self.analyze_trajectory(track)
        
        sudden_velocity_changes = []
        sudden_acceleration_changes = []
        
        # 检测速度突变
        for i, v in enumerate(analysis.get("velocities", [])):
            if v > velocity_threshold:
                sudden_velocity_changes.append({
                    "frame_index": i,
                    "velocity": v
                })
        
        # 检测加速度突变
        for i, a in enumerate(analysis.get("accelerations", [])):
            if abs(a) > acceleration_threshold:
                sudden_acceleration_changes.append({
                    "frame_index": i,
                    "acceleration": a
                })
        
        return {
            "has_sudden_changes": len(sudden_velocity_changes) > 0 or len(sudden_acceleration_changes) > 0,
            "sudden_velocity_changes": sudden_velocity_changes,
            "sudden_acceleration_changes": sudden_acceleration_changes
        }
