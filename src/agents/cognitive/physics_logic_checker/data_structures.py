"""
数据结构定义

定义 Physics & Logic Checker 使用的所有数据类。
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional
from enum import Enum
import numpy as np


class ErrorType(str, Enum):
    """错误类型"""
    # 物理错误
    GRAVITY_VIOLATION = "gravity_violation"
    MOTION_ANOMALY = "motion_anomaly"
    SPATIAL_INCONSISTENCY = "spatial_inconsistency"
    
    # 逻辑错误
    CONTINUITY_ERROR = "continuity_error"
    STATE_JUMP = "state_jump"
    TEMPORAL_ERROR = "temporal_error"


class Severity(str, Enum):
    """严重性等级"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Detection:
    """对象检测结果"""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2
    class_id: int
    class_name: str
    confidence: float
    frame_id: int
    features: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "bbox": self.bbox,
            "class_id": self.class_id,
            "class_name": self.class_name,
            "confidence": self.confidence,
            "frame_id": self.frame_id
        }


@dataclass
class Track:
    """对象跟踪结果"""
    track_id: int
    detections: List[Detection] = field(default_factory=list)
    positions: List[Tuple[float, float]] = field(default_factory=list)
    velocities: List[float] = field(default_factory=list)
    state: str = "active"  # active, lost, terminated
    
    def add_detection(self, detection: Detection):
        """添加检测结果"""
        self.detections.append(detection)
        # 计算中心位置
        x1, y1, x2, y2 = detection.bbox
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        self.positions.append((center_x, center_y))
    
    def compute_velocity(self) -> float:
        """计算平均速度"""
        if len(self.positions) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(1, len(self.positions)):
            x1, y1 = self.positions[i-1]
            x2, y2 = self.positions[i]
            distance = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            total_distance += distance
        
        return total_distance / (len(self.positions) - 1)


@dataclass
class PhysicsError:
    """物理错误"""
    error_type: ErrorType
    severity: Severity
    frame_range: Tuple[int, int]
    description: str
    confidence: float
    affected_objects: List[int] = field(default_factory=list)  # track_ids
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "frame_range": self.frame_range,
            "description": self.description,
            "confidence": self.confidence,
            "affected_objects": self.affected_objects,
            "metadata": self.metadata
        }


@dataclass
class LogicError:
    """逻辑错误"""
    error_type: ErrorType
    severity: Severity
    frame_range: Tuple[int, int]
    description: str
    confidence: float
    affected_objects: List[int] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "error_type": self.error_type.value,
            "severity": self.severity.value,
            "frame_range": self.frame_range,
            "description": self.description,
            "confidence": self.confidence,
            "affected_objects": self.affected_objects,
            "metadata": self.metadata
        }


@dataclass
class ErrorCandidate:
    """错误候选（用于 LLM 验证）"""
    type: ErrorType
    severity: Severity
    frame_indices: List[int]
    confidence: float
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "type": self.type.value,
            "severity": self.severity.value,
            "frame_indices": self.frame_indices,
            "confidence": self.confidence,
            "context": self.context
        }


@dataclass
class VerificationResult:
    """LLM 验证结果"""
    is_error: bool
    confidence: float
    reasoning: str
    severity: Severity
    suggestions: List[str] = field(default_factory=list)
    model_used: str = ""
    cost: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "is_error": self.is_error,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "model_used": self.model_used,
            "cost": self.cost
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VerificationResult':
        """从字典创建"""
        return cls(
            is_error=data["is_error"],
            confidence=data["confidence"],
            reasoning=data["reasoning"],
            severity=Severity(data["severity"]),
            suggestions=data.get("suggestions", []),
            model_used=data.get("model_used", ""),
            cost=data.get("cost", 0.0)
        )


@dataclass
class CheckResult:
    """检查结果"""
    physics_errors: List[PhysicsError] = field(default_factory=list)
    logic_errors: List[LogicError] = field(default_factory=list)
    overall_score: float = 1.0  # 0-1, 1表示无错误
    passed: bool = True
    summary: Dict[str, Any] = field(default_factory=dict)
    llm_cost: float = 0.0
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "physics_errors": [e.to_dict() for e in self.physics_errors],
            "logic_errors": [e.to_dict() for e in self.logic_errors],
            "overall_score": self.overall_score,
            "passed": self.passed,
            "summary": self.summary,
            "llm_cost": self.llm_cost,
            "processing_time": self.processing_time
        }
    
    def add_physics_error(self, error: PhysicsError):
        """添加物理错误"""
        self.physics_errors.append(error)
        self._update_score()
    
    def add_logic_error(self, error: LogicError):
        """添加逻辑错误"""
        self.logic_errors.append(error)
        self._update_score()
    
    def _update_score(self):
        """更新总体分数"""
        total_errors = len(self.physics_errors) + len(self.logic_errors)
        if total_errors == 0:
            self.overall_score = 1.0
            self.passed = True
        else:
            # 根据错误数量和严重性计算分数
            penalty = 0.0
            for error in self.physics_errors + self.logic_errors:
                if error.severity == Severity.CRITICAL:
                    penalty += 0.3
                elif error.severity == Severity.HIGH:
                    penalty += 0.2
                elif error.severity == Severity.MEDIUM:
                    penalty += 0.1
                else:
                    penalty += 0.05
            
            self.overall_score = max(0.0, 1.0 - penalty)
            self.passed = self.overall_score >= 0.7
