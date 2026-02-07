"""
Physics & Logic Checker 主检查器

协调所有子检查器，管理检查流程，聚合结果。
"""

import logging
import time
from typing import List, Dict, Any, Optional
import numpy as np

from .data_structures import (
    CheckResult,
    PhysicsError,
    LogicError,
    ErrorCandidate,
    ErrorType,
    Severity
)

logger = logging.getLogger(__name__)


class PhysicsLogicChecker:
    """
    物理和逻辑检查器
    
    检测视频序列中的物理规律违反和内容逻辑错误。
    集成多模态 LLM 提升检测准确性。
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化检查器
        
        Args:
            config: 配置字典
        """
        self.config = config or {}
        
        # 启用功能
        self.enable_physics_check = self.config.get("enable_physics_check", True)
        self.enable_logic_check = self.config.get("enable_logic_check", True)
        self.enable_llm = self.config.get("enable_llm", False)
        
        # LLM 配置
        self.llm_budget = self.config.get("llm_budget", 0.5)  # 每个视频预算
        self.llm_verification_level = self.config.get("llm_verification_level", "lightweight")
        
        # 初始化子检查器（延迟加载）
        self._physics_checkers = None
        self._logic_checkers = None
        self._llm_verifier = None
        self._keyframe_selector = None
        
        logger.info("PhysicsLogicChecker initialized")
        logger.info(f"Physics check: {self.enable_physics_check}")
        logger.info(f"Logic check: {self.enable_logic_check}")
        logger.info(f"LLM verification: {self.enable_llm}")
    
    def _init_physics_checkers(self):
        """初始化物理检查器"""
        if self._physics_checkers is not None:
            return
        
        from .physics.gravity_checker import GravityChecker
        from .physics.motion_checker import MotionChecker
        from .physics.spatial_relation_checker import SpatialRelationChecker
        
        self._physics_checkers = {
            "gravity": GravityChecker(),
            "motion": MotionChecker(),
            "spatial": SpatialRelationChecker()
        }
        
        logger.info("Physics checkers initialized")
    
    def _init_logic_checkers(self):
        """初始化逻辑检查器"""
        if self._logic_checkers is not None:
            return
        
        from .logic.continuity_error_detector import ContinuityErrorDetector
        from .logic.object_state_checker import ObjectStateChecker
        from .logic.temporal_logic_checker import TemporalLogicChecker
        
        self._logic_checkers = {
            "continuity": ContinuityErrorDetector(),
            "state": ObjectStateChecker(),
            "temporal": TemporalLogicChecker()
        }
        
        logger.info("Logic checkers initialized")
    
    def _init_llm_verifier(self):
        """初始化 LLM 验证器"""
        if self._llm_verifier is not None or not self.enable_llm:
            return
        
        from .multimodal.llm_verifier import MultimodalLLMVerifier
        
        self._llm_verifier = MultimodalLLMVerifier(self.config)
        
        logger.info("LLM verifier initialized")
    
    def _init_keyframe_selector(self):
        """初始化关键帧选择器"""
        if self._keyframe_selector is not None:
            return
        
        from .utils.keyframe_selector import KeyFrameSelector
        
        self._keyframe_selector = KeyFrameSelector(self.config)
        
        logger.info("KeyFrame selector initialized")
    
    async def check_video_sequence(
        self,
        frames: List[np.ndarray],
        metadata: Optional[Dict[str, Any]] = None
    ) -> CheckResult:
        """
        检查视频序列
        
        Args:
            frames: 视频帧列表
            metadata: 元数据
            
        Returns:
            CheckResult: 检查结果
        """
        start_time = time.time()
        metadata = metadata or {}
        
        logger.info(f"Starting physics & logic check for {len(frames)} frames")
        
        result = CheckResult()
        
        try:
            # 1. 选择关键帧（如果启用 LLM）
            if self.enable_llm:
                self._init_keyframe_selector()
                keyframe_indices = self._keyframe_selector.select_keyframes(frames)
                logger.info(f"Selected {len(keyframe_indices)} keyframes")
            else:
                keyframe_indices = list(range(len(frames)))
            
            # 2. 物理检查
            if self.enable_physics_check:
                self._init_physics_checkers()
                physics_errors = await self._run_physics_checks(frames, keyframe_indices)
                for error in physics_errors:
                    result.add_physics_error(error)
            
            # 3. 逻辑检查
            if self.enable_logic_check:
                self._init_logic_checkers()
                logic_errors = await self._run_logic_checks(frames, keyframe_indices)
                for error in logic_errors:
                    result.add_logic_error(error)
            
            # 4. LLM 验证（可选）
            if self.enable_llm:
                self._init_llm_verifier()
                await self._verify_with_llm(frames, result)
            
            # 5. 生成摘要
            result.summary = self._generate_summary(result)
            
        except Exception as e:
            logger.error(f"Error during physics & logic check: {e}", exc_info=True)
            result.passed = False
            result.summary = {"error": str(e)}
        
        result.processing_time = time.time() - start_time
        
        logger.info(f"Check completed in {result.processing_time:.2f}s")
        logger.info(f"Found {len(result.physics_errors)} physics errors, "
                   f"{len(result.logic_errors)} logic errors")
        
        return result
    
    async def _run_physics_checks(
        self,
        frames: List[np.ndarray],
        keyframe_indices: List[int]
    ) -> List[PhysicsError]:
        """运行物理检查"""
        errors = []
        
        # 1. 对象检测和跟踪
        tracks = await self._detect_and_track_objects(frames, keyframe_indices)
        
        if not tracks:
            logger.warning("No objects detected, skipping physics checks")
            return errors
        
        # 2. 运行各项物理检查
        if "gravity" in self._physics_checkers:
            gravity_errors = self._physics_checkers["gravity"].check_gravity(tracks, frames)
            errors.extend(gravity_errors)
        
        if "motion" in self._physics_checkers:
            motion_errors = self._physics_checkers["motion"].check_motion(tracks, frames)
            errors.extend(motion_errors)
        
        if "spatial" in self._physics_checkers:
            spatial_errors = self._physics_checkers["spatial"].check_spatial_relations(tracks, frames)
            errors.extend(spatial_errors)
        
        logger.debug(f"Physics checks completed, found {len(errors)} errors")
        return errors
    
    async def _run_logic_checks(
        self,
        frames: List[np.ndarray],
        keyframe_indices: List[int]
    ) -> List[LogicError]:
        """运行逻辑检查"""
        errors = []
        
        # 1. 对象检测和跟踪
        tracks = await self._detect_and_track_objects(frames, keyframe_indices)
        
        if not tracks:
            logger.warning("No objects detected, skipping logic checks")
            return errors
        
        # 2. 运行各项逻辑检查
        if "continuity" in self._logic_checkers:
            continuity_errors = self._logic_checkers["continuity"].check_continuity(tracks, frames)
            errors.extend(continuity_errors)
        
        if "state" in self._logic_checkers:
            state_errors = self._logic_checkers["state"].check_state_transitions(tracks, frames)
            errors.extend(state_errors)
        
        if "temporal" in self._logic_checkers:
            temporal_errors = self._logic_checkers["temporal"].check_temporal_logic(tracks, frames)
            errors.extend(temporal_errors)
        
        logger.debug(f"Logic checks completed, found {len(errors)} errors")
        return errors
    
    async def _detect_and_track_objects(
        self,
        frames: List[np.ndarray],
        keyframe_indices: List[int]
    ) -> List:
        """检测和跟踪对象"""
        from .utils.object_detector import ObjectDetector
        from .utils.object_tracker import ObjectTracker
        
        # 初始化检测器和跟踪器
        detector = ObjectDetector()
        tracker = ObjectTracker()
        
        # 只在关键帧上检测
        for frame_idx in keyframe_indices:
            if frame_idx >= len(frames):
                continue
            
            frame = frames[frame_idx]
            
            # 检测对象
            detections = detector.detect(frame, frame_idx)
            
            # 更新跟踪
            tracker.update(detections)
        
        # 获取所有跟踪
        tracks = tracker.get_all_tracks()
        
        logger.info(f"Detected and tracked {len(tracks)} objects")
        return tracks
    
    async def _verify_with_llm(
        self,
        frames: List[np.ndarray],
        result: CheckResult
    ):
        """使用 LLM 验证错误"""
        # TODO: 实现 LLM 验证逻辑
        logger.debug("LLM verification skipped (not implemented)")
    
    def _generate_summary(self, result: CheckResult) -> Dict[str, Any]:
        """生成检查摘要"""
        total_errors = len(result.physics_errors) + len(result.logic_errors)
        
        # 按严重性分类
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for error in result.physics_errors + result.logic_errors:
            severity_counts[error.severity.value] += 1
        
        # 按类型分类
        error_types = {}
        for error in result.physics_errors + result.logic_errors:
            error_type = error.error_type.value
            error_types[error_type] = error_types.get(error_type, 0) + 1
        
        return {
            "total_errors": total_errors,
            "physics_errors": len(result.physics_errors),
            "logic_errors": len(result.logic_errors),
            "severity_distribution": severity_counts,
            "error_types": error_types,
            "overall_score": result.overall_score,
            "passed": result.passed
        }
