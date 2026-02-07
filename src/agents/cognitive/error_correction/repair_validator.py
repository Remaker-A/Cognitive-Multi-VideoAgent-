"""
修复效果验证器

验证修复后的图像质量。
"""

import logging
from typing import Dict, Any, Optional


logger = logging.getLogger(__name__)


class RepairValidator:
    """
    修复效果验证器
    
    验证修复后的图像是否解决了原始错误。
    """
    
    def __init__(self, error_detectors):
        """
        初始化验证器
        
        Args:
            error_detectors: 错误检测器字典
        """
        self.hand_detector = error_detectors.get("hand")
        self.face_detector = error_detectors.get("face")
        self.pose_detector = error_detectors.get("pose")
        self.physics_detector = error_detectors.get("physics")
        self.text_detector = error_detectors.get("text")
        
        logger.info("RepairValidator initialized")
    
    def validate_repair(
        self,
        original_image: str,
        repaired_image: str,
        original_errors: list,
        error_classifier
    ) -> Dict[str, Any]:
        """
        验证修复效果
        
        Args:
            original_image: 原始图像
            repaired_image: 修复后的图像
            original_errors: 原始错误列表
            error_classifier: 错误分级器
            
        Returns:
            Dict: 验证结果
        """
        logger.info("Validating repair effectiveness")
        
        try:
            # 重新检测修复后的图像
            new_errors = self._detect_all_errors(repaired_image)
            
            # 分类新错误
            new_classified = error_classifier.classify_errors(new_errors)
            
            # 比较修复前后
            validation = self._compare_errors(
                original_errors,
                new_errors,
                new_classified
            )
            
            logger.info(f"Validation complete: {validation['status']}")
            
            return validation
            
        except Exception as e:
            logger.error(f"Validation failed: {e}", exc_info=True)
            return {
                "status": "validation_failed",
                "error": str(e)
            }
    
    def _detect_all_errors(self, image_data: str) -> list:
        """重新检测所有错误"""
        all_errors = []
        
        if self.hand_detector:
            all_errors.extend(self.hand_detector.detect_hand_errors(image_data))
        
        if self.face_detector:
            all_errors.extend(self.face_detector.detect_face_errors(image_data))
        
        if self.pose_detector:
            all_errors.extend(self.pose_detector.detect_pose_errors(image_data))
        
        if self.physics_detector:
            all_errors.extend(self.physics_detector.detect_physics_violations(image_data))
        
        if self.text_detector:
            all_errors.extend(self.text_detector.detect_text_errors(image_data))
        
        return all_errors
    
    def _compare_errors(
        self,
        original_errors: list,
        new_errors: list,
        new_classified: Dict[str, Any]
    ) -> Dict[str, Any]:
        """比较修复前后的错误"""
        # 计算错误数量变化
        original_count = len(original_errors)
        new_count = len(new_errors)
        
        # 计算改善分数
        improvement_score = max(0.0, (original_count - new_count) / max(1, original_count))
        
        # 检查是否引入了新的严重错误
        new_critical = new_classified["stats"]["critical_count"]
        new_high = new_classified["stats"]["high_count"]
        
        # 判断修复状态
        if new_count == 0:
            status = "fully_fixed"
        elif new_count < original_count and new_critical == 0:
            status = "partially_fixed"
        elif new_count >= original_count or new_critical > 0:
            status = "not_fixed_or_worse"
        else:
            status = "unknown"
        
        return {
            "status": status,
            "original_error_count": original_count,
            "new_error_count": new_count,
            "improvement_score": improvement_score,
            "errors_fixed": original_count - new_count,
            "new_critical_errors": new_critical,
            "new_high_errors": new_high,
            "requires_further_repair": new_critical > 0 or new_high > 2
        }
