"""
错误分级器

对检测到的错误进行严重程度分级。
"""

import logging
from typing import Dict, Any, List
from enum import Enum


logger = logging.getLogger(__name__)


class ErrorSeverity(str, Enum):
    """错误严重程度"""
    CRITICAL = "CRITICAL"  # 严重：必须修复
    HIGH = "HIGH"          # 高：强烈建议修复
    MEDIUM = "MEDIUM"      # 中：建议修复
    LOW = "LOW"            # 低：可选修复


class ErrorClassifier:
    """
    错误分级器
    
    对检测到的错误进行严重程度分级。
    """
    
    # 错误类型到严重程度的映射
    SEVERITY_MAP = {
        # 手部错误
        "hand_finger_count_wrong": ErrorSeverity.CRITICAL,
        "hand_deformed": ErrorSeverity.HIGH,
        "hand_missing": ErrorSeverity.CRITICAL,
        
        # 面部错误
        "face_missing_eyes": ErrorSeverity.CRITICAL,
        "face_missing_nose": ErrorSeverity.CRITICAL,
        "face_missing_mouth": ErrorSeverity.CRITICAL,
        "face_expression_abnormal": ErrorSeverity.HIGH,
        "face_asymmetric": ErrorSeverity.MEDIUM,
        
        # 姿态错误
        "pose_unnatural": ErrorSeverity.HIGH,
        "pose_anatomically_impossible": ErrorSeverity.CRITICAL,
        "pose_limb_missing": ErrorSeverity.CRITICAL,
        
        # 物理规律错误
        "physics_gravity_violation": ErrorSeverity.HIGH,
        "physics_perspective_wrong": ErrorSeverity.MEDIUM,
        "physics_floating_object": ErrorSeverity.HIGH,
        
        # 文字错误
        "text_gibberish": ErrorSeverity.MEDIUM,
        "text_spelling_error": ErrorSeverity.LOW,
        "text_blurry": ErrorSeverity.LOW,
    }
    
    def __init__(self):
        """初始化分级器"""
        logger.info("ErrorClassifier initialized")
    
    def classify_errors(
        self,
        errors: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        对错误进行分级
        
        Args:
            errors: 错误列表
            
        Returns:
            Dict: 分级后的错误
        """
        classified = {
            ErrorSeverity.CRITICAL: [],
            ErrorSeverity.HIGH: [],
            ErrorSeverity.MEDIUM: [],
            ErrorSeverity.LOW: []
        }
        
        for error in errors:
            severity = self.classify_severity(error)
            classified[severity].append(error)
        
        # 计算统计
        stats = {
            "total_errors": len(errors),
            "critical_count": len(classified[ErrorSeverity.CRITICAL]),
            "high_count": len(classified[ErrorSeverity.HIGH]),
            "medium_count": len(classified[ErrorSeverity.MEDIUM]),
            "low_count": len(classified[ErrorSeverity.LOW])
        }
        
        return {
            "errors_by_severity": classified,
            "stats": stats,
            "requires_fix": stats["critical_count"] > 0 or stats["high_count"] > 0
        }
    
    def classify_severity(self, error: Dict[str, Any]) -> ErrorSeverity:
        """
        分类单个错误的严重程度
        
        Args:
            error: 错误信息
            
        Returns:
            ErrorSeverity: 严重程度
        """
        error_type = error.get("type", "unknown")
        
        # 从映射表获取严重程度
        severity = self.SEVERITY_MAP.get(error_type, ErrorSeverity.MEDIUM)
        
        # 根据置信度调整
        confidence = error.get("confidence", 1.0)
        
        if confidence < 0.5:
            # 低置信度的错误降级
            if severity == ErrorSeverity.CRITICAL:
                severity = ErrorSeverity.HIGH
            elif severity == ErrorSeverity.HIGH:
                severity = ErrorSeverity.MEDIUM
        
        return severity
