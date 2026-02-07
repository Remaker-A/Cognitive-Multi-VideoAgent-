"""
关键帧选择器

智能选择视频中的关键帧以优化 LLM 成本。
"""

import logging
from typing import List, Optional
import numpy as np
import cv2

logger = logging.getLogger(__name__)


class KeyFrameSelector:
    """
    关键帧选择器
    
    使用场景变化检测、运动分析等方法选择关键帧。
    """
    
    def __init__(self, config: Optional[dict] = None):
        """
        初始化关键帧选择器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        self.method = self.config.get("keyframe_selection", {}).get("method", "scene_change")
        self.max_keyframes = self.config.get("keyframe_selection", {}).get("max_keyframes", 100)
        self.min_interval = self.config.get("keyframe_selection", {}).get("min_interval", 10)
        self.scene_change_threshold = self.config.get("scene_change_threshold", 30.0)
        
        logger.info(f"KeyFrameSelector initialized with method: {self.method}")
    
    def select_keyframes(self, frames: List[np.ndarray]) -> List[int]:
        """
        选择关键帧
        
        Args:
            frames: 视频帧列表
            
        Returns:
            List[int]: 关键帧索引列表
        """
        if self.method == "scene_change":
            return self._select_by_scene_change(frames)
        elif self.method == "motion":
            return self._select_by_motion(frames)
        elif self.method == "uniform":
            return self._select_uniform(frames)
        else:
            logger.warning(f"Unknown method {self.method}, using uniform")
            return self._select_uniform(frames)
    
    def _select_by_scene_change(self, frames: List[np.ndarray]) -> List[int]:
        """基于场景变化选择关键帧"""
        keyframes = [0]  # 总是包含第一帧
        
        for i in range(1, len(frames)):
            # 计算与前一帧的差异
            diff = self._compute_frame_diff(frames[i-1], frames[i])
            
            # 如果差异超过阈值，认为是场景变化
            if diff > self.scene_change_threshold:
                # 检查是否满足最小间隔
                if i - keyframes[-1] >= self.min_interval:
                    keyframes.append(i)
            
            # 检查是否达到最大数量
            if len(keyframes) >= self.max_keyframes:
                break
        
        # 总是包含最后一帧
        if keyframes[-1] != len(frames) - 1:
            keyframes.append(len(frames) - 1)
        
        logger.info(f"Selected {len(keyframes)} keyframes by scene change")
        return keyframes
    
    def _select_by_motion(self, frames: List[np.ndarray]) -> List[int]:
        """基于运动强度选择关键帧"""
        keyframes = [0]
        
        # 计算每帧的运动强度
        motion_scores = []
        for i in range(1, len(frames)):
            motion = self._compute_motion_score(frames[i-1], frames[i])
            motion_scores.append((i, motion))
        
        # 按运动强度排序
        motion_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 选择运动强度最高的帧
        for frame_id, _ in motion_scores:
            if len(keyframes) >= self.max_keyframes:
                break
            
            # 检查是否满足最小间隔
            if all(abs(frame_id - kf) >= self.min_interval for kf in keyframes):
                keyframes.append(frame_id)
        
        # 排序
        keyframes.sort()
        
        # 总是包含最后一帧
        if keyframes[-1] != len(frames) - 1:
            keyframes.append(len(frames) - 1)
        
        logger.info(f"Selected {len(keyframes)} keyframes by motion")
        return keyframes
    
    def _select_uniform(self, frames: List[np.ndarray]) -> List[int]:
        """均匀选择关键帧"""
        n_frames = len(frames)
        
        if n_frames <= self.max_keyframes:
            return list(range(n_frames))
        
        # 计算间隔
        interval = n_frames // self.max_keyframes
        
        keyframes = list(range(0, n_frames, interval))
        
        # 确保包含最后一帧
        if keyframes[-1] != n_frames - 1:
            keyframes.append(n_frames - 1)
        
        logger.info(f"Selected {len(keyframes)} keyframes uniformly")
        return keyframes
    
    def _compute_frame_diff(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算两帧之间的差异"""
        # 转换为灰度
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
        else:
            gray1 = frame1
        
        if len(frame2.shape) == 3:
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        else:
            gray2 = frame2
        
        # 计算绝对差异
        diff = cv2.absdiff(gray1, gray2)
        
        # 返回平均差异
        return float(np.mean(diff))
    
    def _compute_motion_score(self, frame1: np.ndarray, frame2: np.ndarray) -> float:
        """计算运动分数"""
        # 使用光流计算运动
        if len(frame1.shape) == 3:
            gray1 = cv2.cvtColor(frame1, cv2.COLOR_RGB2GRAY)
        else:
            gray1 = frame1
        
        if len(frame2.shape) == 3:
            gray2 = cv2.cvtColor(frame2, cv2.COLOR_RGB2GRAY)
        else:
            gray2 = frame2
        
        # 计算光流
        flow = cv2.calcOpticalFlowFarneback(
            gray1, gray2, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        # 计算运动幅度
        magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
        
        # 返回平均运动幅度
        return float(np.mean(magnitude))
