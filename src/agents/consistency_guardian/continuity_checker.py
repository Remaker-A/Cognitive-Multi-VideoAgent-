"""
连贯性检查器

检查相邻 shot 之间的连贯性。
"""

import logging
from typing import Dict, Any, Optional

from .clip_detector import CLIPDetector
from .lighting_detector import LightingDetector
from .palette_detector import PaletteDetector


logger = logging.getLogger(__name__)


class ContinuityChecker:
    """
    连贯性检查器
    
    检查相邻 shot 的视觉连贯性。
    """
    
    def __init__(self):
        """初始化检查器"""
        self.clip_detector = CLIPDetector()
        self.lighting_detector = LightingDetector()
        self.palette_detector = PaletteDetector()
        
        # 权重配置
        self.weights = {
            "visual_similarity": 0.4,
            "lighting_consistency": 0.3,
            "color_consistency": 0.2,
            "position_consistency": 0.1
        }
        
        logger.info("ContinuityChecker initialized")
    
    def check_shot_continuity(
        self,
        shot1_data: Dict[str, Any],
        shot2_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        检查两个 shot 的连贯性
        
        Args:
            shot1_data: Shot 1 数据（包含最后一帧）
            shot2_data: Shot 2 数据（包含第一帧）
            
        Returns:
            Dict: 连贯性检测结果
        """
        logger.info(f"Checking continuity between shots")
        
        try:
            # 获取关键帧
            frame1 = shot1_data.get("last_frame")
            frame2 = shot2_data.get("first_frame")
            
            if not frame1 or not frame2:
                logger.warning("Missing frames for continuity check")
                return self._empty_result()
            
            results = {
                "shot1_id": shot1_data.get("shot_id"),
                "shot2_id": shot2_data.get("shot_id"),
                "checks": {}
            }
            
            # 1. 视觉相似度检测
            visual_sim = self.clip_detector.check_similarity(frame1, frame2)
            if visual_sim is not None:
                results["checks"]["visual_similarity"] = {
                    "score": visual_sim,
                    "passed": visual_sim >= 0.70
                }
            
            # 2. 光照一致性检测
            lighting_cons = self.lighting_detector.detect_lighting_change(frame1, frame2)
            if lighting_cons is not None:
                results["checks"]["lighting_consistency"] = {
                    "score": lighting_cons,
                    "passed": lighting_cons >= 0.75
                }
            
            # 3. 颜色一致性检测
            color_cons = self.palette_detector.check_consistency([frame1, frame2])
            if color_cons is not None:
                results["checks"]["color_consistency"] = {
                    "score": color_cons,
                    "passed": color_cons >= 0.70
                }
            
            # 4. 位置一致性检测（简化版）
            # TODO: 实现真正的特征点匹配
            position_cons = 0.75  # 占位符
            results["checks"]["position_consistency"] = {
                "score": position_cons,
                "passed": position_cons >= 0.65
            }
            
            # 5. 计算总体评分
            overall_score = self._calculate_overall_score(results["checks"])
            results["overall_score"] = overall_score
            results["passed"] = overall_score >= 0.70
            
            logger.info(f"Continuity check: {overall_score:.4f} ({'PASSED' if results['passed'] else 'FAILED'})")
            
            return results
            
        except Exception as e:
            logger.error(f"Continuity check failed: {e}", exc_info=True)
            return self._empty_result()
    
    def _calculate_overall_score(self, checks: Dict[str, Any]) -> float:
        """
        计算总体连贯性评分
        
        Args:
            checks: 各项检测结果
            
        Returns:
            float: 总体评分 (0-1)
        """
        total_score = 0.0
        total_weight = 0.0
        
        for check_name, weight in self.weights.items():
            if check_name in checks:
                score = checks[check_name].get("score", 0)
                total_score += score * weight
                total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return total_score / total_weight
    
    def _empty_result(self) -> Dict[str, Any]:
        """返回空结果"""
        return {
            "shot1_id": None,
            "shot2_id": None,
            "checks": {},
            "overall_score": 0.0,
            "passed": False
        }
