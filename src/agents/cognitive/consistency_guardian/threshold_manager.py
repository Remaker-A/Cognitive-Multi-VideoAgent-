"""
动态阈值管理器

根据质量档位和镜头类型提供动态阈值。
"""

import logging
from typing import Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class QualityTier(str, Enum):
    """质量档位"""
    PREVIEW = "PREVIEW"
    STANDARD = "STANDARD"
    HIGH = "HIGH"
    ULTRA = "ULTRA"


class ThresholdManager:
    """
    动态阈值管理器
    
    根据不同场景提供适配的检测阈值。
    """
    
    # 基础阈值配置
    BASE_THRESHOLDS = {
        QualityTier.PREVIEW: {
            "clip_similarity": 0.65,
            "face_identity": 0.60,
            "palette_consistency": 0.55,
            "flow_smoothness": 0.60,
            "temporal_coherence": 0.70
        },
        QualityTier.STANDARD: {
            "clip_similarity": 0.75,
            "face_identity": 0.70,
            "palette_consistency": 0.65,
            "flow_smoothness": 0.70,
            "temporal_coherence": 0.80
        },
        QualityTier.HIGH: {
            "clip_similarity": 0.80,
            "face_identity": 0.75,
            "palette_consistency": 0.70,
            "flow_smoothness": 0.75,
            "temporal_coherence": 0.85
        },
        QualityTier.ULTRA: {
            "clip_similarity": 0.85,
            "face_identity": 0.80,
            "palette_consistency": 0.75,
            "flow_smoothness": 0.80,
            "temporal_coherence": 0.90
        }
    }
    
    # 镜头类型调整系数
    SHOT_TYPE_ADJUSTMENTS = {
        "character_portrait": {
            "face_identity": 1.1,  # 更严格的面部检测
            "palette_consistency": 0.95
        },
        "action_scene": {
            "flow_smoothness": 1.1,  # 更严格的流畅度
            "clip_similarity": 0.95
        },
        "environment_establishing": {
            "palette_consistency": 1.1,  # 更严格的色彩
            "face_identity": 0.9
        }
    }
    
    def __init__(self):
        """初始化阈值管理器"""
        logger.info("ThresholdManager initialized")
    
    def get_dynamic_thresholds(
        self,
        quality_tier: str = "STANDARD",
        shot_type: str = None
    ) -> Dict[str, float]:
        """
        获取动态阈值
        
        Args:
            quality_tier: 质量档位
            shot_type: 镜头类型
            
        Returns:
            Dict: 阈值字典
        """
        # 获取基础阈值
        tier = QualityTier(quality_tier) if quality_tier in QualityTier.__members__ else QualityTier.STANDARD
        
        thresholds = self.BASE_THRESHOLDS[tier].copy()
        
        # 应用镜头类型调整
        if shot_type and shot_type in self.SHOT_TYPE_ADJUSTMENTS:
            adjustments = self.SHOT_TYPE_ADJUSTMENTS[shot_type]
            
            for metric, factor in adjustments.items():
                if metric in thresholds:
                    thresholds[metric] *= factor
                    # 限制在 0-1 范围
                    thresholds[metric] = min(1.0, max(0.0, thresholds[metric]))
        
        logger.debug(f"Dynamic thresholds for {quality_tier}/{shot_type}: {thresholds}")
        
        return thresholds
    
    def get_threshold(
        self,
        metric: str,
        quality_tier: str = "STANDARD",
        shot_type: str = None
    ) -> float:
        """
        获取单个指标的阈值
        
        Args:
            metric: 指标名称
            quality_tier: 质量档位
            shot_type: 镜头类型
            
        Returns:
            float: 阈值
        """
        thresholds = self.get_dynamic_thresholds(quality_tier, shot_type)
        
        return thresholds.get(metric, 0.75)  # 默认 0.75
