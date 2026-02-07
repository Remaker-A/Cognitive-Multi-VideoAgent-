"""
Physics & Logic Checker

检测视频序列中的物理规律违反和内容逻辑错误。
集成多模态 LLM 提升检测准确性，同时控制成本。
"""

__version__ = "0.1.0"
__author__ = "VideoGen Team"

from .physics_logic_checker import PhysicsLogicChecker
from .data_structures import (
    Detection,
    Track,
    PhysicsError,
    LogicError,
    CheckResult,
    ErrorCandidate,
    VerificationResult
)

__all__ = [
    "PhysicsLogicChecker",
    "Detection",
    "Track",
    "PhysicsError",
    "LogicError",
    "CheckResult",
    "ErrorCandidate",
    "VerificationResult"
]
