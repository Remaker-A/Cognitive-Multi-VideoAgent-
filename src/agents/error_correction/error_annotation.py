"""
错误标注数据模型

定义用户错误标注的数据结构。
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from .error_classifier import ErrorSeverity


logger = logging.getLogger(__name__)


class AnnotationStatus(str, Enum):
    """标注状态"""
    PENDING = "pending"           # 待处理
    PROCESSING = "processing"     # 处理中
    FIXED = "fixed"              # 已修复
    REJECTED = "rejected"        # 已拒绝


class RegionType(str, Enum):
    """标注区域类型"""
    RECTANGLE = "rectangle"  # 矩形
    POLYGON = "polygon"      # 多边形
    POINT = "point"          # 点


@dataclass
class AnnotationRegion:
    """标注区域"""
    type: RegionType
    coordinates: List[Dict[str, float]]  # [{"x": 0.5, "y": 0.3}, ...]
    width: Optional[int] = None
    height: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value,
            "coordinates": self.coordinates,
            "width": self.width,
            "height": self.height
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnnotationRegion':
        """从字典创建"""
        return cls(
            type=RegionType(data["type"]),
            coordinates=data["coordinates"],
            width=data.get("width"),
            height=data.get("height")
        )


@dataclass
class ErrorAnnotation:
    """
    错误标注
    
    用户手动标注的错误信息。
    """
    annotation_id: str
    project_id: str
    shot_id: str
    artifact_url: str
    
    # 标注区域
    region: AnnotationRegion
    
    # 错误信息
    error_type: str
    error_category: str  # "hand", "face", "pose", "physics", "text", "other"
    error_description: str
    severity: ErrorSeverity
    
    # 元数据
    annotated_by: str
    annotated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: AnnotationStatus = AnnotationStatus.PENDING
    
    # 修复信息
    repair_level: Optional[int] = None
    repair_result: Optional[Dict[str, Any]] = None
    fixed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "annotation_id": self.annotation_id,
            "project_id": self.project_id,
            "shot_id": self.shot_id,
            "artifact_url": self.artifact_url,
            "region": self.region.to_dict(),
            "error_type": self.error_type,
            "error_category": self.error_category,
            "error_description": self.error_description,
            "severity": self.severity.value,
            "annotated_by": self.annotated_by,
            "annotated_at": self.annotated_at,
            "status": self.status.value,
            "repair_level": self.repair_level,
            "repair_result": self.repair_result,
            "fixed_at": self.fixed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorAnnotation':
        """从字典创建"""
        return cls(
            annotation_id=data["annotation_id"],
            project_id=data["project_id"],
            shot_id=data["shot_id"],
            artifact_url=data["artifact_url"],
            region=AnnotationRegion.from_dict(data["region"]),
            error_type=data["error_type"],
            error_category=data["error_category"],
            error_description=data["error_description"],
            severity=ErrorSeverity(data["severity"]),
            annotated_by=data["annotated_by"],
            annotated_at=data.get("annotated_at", datetime.now().isoformat()),
            status=AnnotationStatus(data.get("status", "pending")),
            repair_level=data.get("repair_level"),
            repair_result=data.get("repair_result"),
            fixed_at=data.get("fixed_at")
        )
    
    def update_status(self, status: AnnotationStatus) -> None:
        """更新状态"""
        self.status = status
        
        if status == AnnotationStatus.FIXED:
            self.fixed_at = datetime.now().isoformat()
    
    def set_repair_result(
        self,
        repair_level: int,
        repair_result: Dict[str, Any]
    ) -> None:
        """设置修复结果"""
        self.repair_level = repair_level
        self.repair_result = repair_result
        self.update_status(AnnotationStatus.PROCESSING)


# 错误类型映射
ERROR_TYPE_CATEGORIES = {
    "hand": [
        "hand_finger_count_wrong",
        "hand_deformed",
        "hand_missing",
        "hand_other"
    ],
    "face": [
        "face_missing_eyes",
        "face_missing_nose",
        "face_missing_mouth",
        "face_expression_abnormal",
        "face_asymmetric",
        "face_other"
    ],
    "pose": [
        "pose_unnatural",
        "pose_anatomically_impossible",
        "pose_limb_missing",
        "pose_other"
    ],
    "physics": [
        "physics_gravity_violation",
        "physics_perspective_wrong",
        "physics_floating_object",
        "physics_other"
    ],
    "text": [
        "text_gibberish",
        "text_spelling_error",
        "text_blurry",
        "text_other"
    ],
    "other": [
        "other_quality_issue",
        "other_style_issue",
        "other_content_issue"
    ]
}
