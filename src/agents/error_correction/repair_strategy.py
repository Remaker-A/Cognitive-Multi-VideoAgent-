"""
修复策略管理器

实现四层智能修复策略。
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum


logger = logging.getLogger(__name__)


class RepairLevel(int, Enum):
    """修复级别"""
    INPAINTING = 1          # 局部 inpainting
    CONTROLNET = 2          # ControlNet 控制重生成
    FULL_REGENERATION = 3   # 完全重新生成
    HUMAN_INTERVENTION = 4  # 人工介入


class RepairStrategy:
    """
    修复策略管理器
    
    实现四层智能修复策略。
    """
    
    def __init__(self, blackboard, event_bus):
        """
        初始化修复策略
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        logger.info("RepairStrategy initialized")
    
    def select_repair_level(
        self,
        error_report: Dict[str, Any]
    ) -> RepairLevel:
        """
        选择修复级别
        
        Args:
            error_report: 错误报告
            
        Returns:
            RepairLevel: 修复级别
        """
        stats = error_report.get("stats", {})
        critical_count = stats.get("critical_count", 0)
        high_count = stats.get("high_count", 0)
        
        errors_by_severity = error_report.get("errors_by_severity", {})
        
        # 检查是否是局部错误
        is_localized = self._is_localized_error(errors_by_severity)
        
        # 决策逻辑
        if critical_count == 1 and is_localized:
            # 单个局部严重错误 → Inpainting
            return RepairLevel.INPAINTING
        
        elif critical_count <= 2 or high_count <= 3:
            # 少量错误 → ControlNet
            return RepairLevel.CONTROLNET
        
        elif critical_count > 2 or high_count > 3:
            # 多个错误 → 完全重新生成
            return RepairLevel.FULL_REGENERATION
        
        else:
            # 其他情况 → 人工介入
            return RepairLevel.HUMAN_INTERVENTION
    
    async def apply_repair(
        self,
        project_id: str,
        shot_id: str,
        artifact_url: str,
        error_report: Dict[str, Any],
        repair_level: RepairLevel
    ) -> Dict[str, Any]:
        """
        应用修复策略
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            artifact_url: 原始图像 URL
            error_report: 错误报告
            repair_level: 修复级别
            
        Returns:
            Dict: 修复结果
        """
        logger.info(f"Applying repair level {repair_level} for shot {shot_id}")
        
        if repair_level == RepairLevel.INPAINTING:
            return await self.apply_inpainting(project_id, shot_id, artifact_url, error_report)
        
        elif repair_level == RepairLevel.CONTROLNET:
            return await self.apply_controlnet(project_id, shot_id, artifact_url, error_report)
        
        elif repair_level == RepairLevel.FULL_REGENERATION:
            return await self.apply_full_regeneration(project_id, shot_id, error_report)
        
        elif repair_level == RepairLevel.HUMAN_INTERVENTION:
            return await self.trigger_human_intervention(project_id, shot_id, error_report)
        
        return {"success": False, "error": "Unknown repair level"}
    
    async def apply_inpainting(
        self,
        project_id: str,
        shot_id: str,
        artifact_url: str,
        error_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 1: 局部 Inpainting 修复
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            artifact_url: 原始图像 URL
            error_report: 错误报告
            
        Returns:
            Dict: 修复结果
        """
        logger.info("Applying Level 1: Inpainting repair")
        
        try:
            # 获取错误位置
            errors = self._get_critical_errors(error_report)
            
            # 生成 mask（标记需要修复的区域）
            mask = self._generate_repair_mask(errors)
            
            # TODO: 调用 Inpainting 模型
            # repaired_image = inpainting_model.inpaint(
            #     image=artifact_url,
            #     mask=mask,
            #     prompt="fix the error"
            # )
            
            # 发布修复请求事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.ERROR_CORRECTION_REQUESTED,
                actor="ErrorCorrection",
                payload={
                    "repair_level": 1,
                    "repair_type": "inpainting",
                    "shot_id": shot_id,
                    "artifact_url": artifact_url,
                    "mask": mask,
                    "errors": errors
                }
            ))
            
            logger.info("Inpainting repair request published")
            
            return {
                "success": True,
                "repair_level": 1,
                "repair_type": "inpainting",
                "status": "requested"
            }
            
        except Exception as e:
            logger.error(f"Inpainting repair failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def apply_controlnet(
        self,
        project_id: str,
        shot_id: str,
        artifact_url: str,
        error_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 2: ControlNet 控制重生成
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            artifact_url: 原始图像 URL
            error_report: 错误报告
            
        Returns:
            Dict: 修复结果
        """
        logger.info("Applying Level 2: ControlNet repair")
        
        try:
            # 确定 ControlNet 类型
            controlnet_type = self._select_controlnet_type(error_report)
            
            # TODO: 调用 ControlNet 模型
            # repaired_image = controlnet_model.generate(
            #     control_image=artifact_url,
            #     control_type=controlnet_type,
            #     prompt=original_prompt
            # )
            
            # 发布修复请求事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.ERROR_CORRECTION_REQUESTED,
                actor="ErrorCorrection",
                payload={
                    "repair_level": 2,
                    "repair_type": "controlnet",
                    "shot_id": shot_id,
                    "artifact_url": artifact_url,
                    "controlnet_type": controlnet_type,
                    "error_report": error_report
                }
            ))
            
            logger.info(f"ControlNet repair request published: {controlnet_type}")
            
            return {
                "success": True,
                "repair_level": 2,
                "repair_type": "controlnet",
                "controlnet_type": controlnet_type,
                "status": "requested"
            }
            
        except Exception as e:
            logger.error(f"ControlNet repair failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def apply_full_regeneration(
        self,
        project_id: str,
        shot_id: str,
        error_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 3: 完全重新生成
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            error_report: 错误报告
            
        Returns:
            Dict: 修复结果
        """
        logger.info("Applying Level 3: Full regeneration")
        
        try:
            # 发布重新生成请求
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.ERROR_CORRECTION_REQUESTED,
                actor="ErrorCorrection",
                payload={
                    "repair_level": 3,
                    "repair_type": "full_regeneration",
                    "shot_id": shot_id,
                    "error_report": error_report,
                    "reason": "Multiple critical errors detected"
                }
            ))
            
            logger.info("Full regeneration request published")
            
            return {
                "success": True,
                "repair_level": 3,
                "repair_type": "full_regeneration",
                "status": "requested"
            }
            
        except Exception as e:
            logger.error(f"Full regeneration failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def trigger_human_intervention(
        self,
        project_id: str,
        shot_id: str,
        error_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 4: 人工介入
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            error_report: 错误报告
            
        Returns:
            Dict: 修复结果
        """
        logger.warning("Triggering Level 4: Human intervention")
        
        try:
            # 发布人工介入事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.HUMAN_GATE_TRIGGERED,
                actor="ErrorCorrection",
                payload={
                    "repair_level": 4,
                    "repair_type": "human_intervention",
                    "shot_id": shot_id,
                    "error_report": error_report,
                    "reason": "Automatic repair failed or too complex"
                }
            ))
            
            logger.warning(f"Human intervention triggered for shot {shot_id}")
            
            return {
                "success": True,
                "repair_level": 4,
                "repair_type": "human_intervention",
                "status": "awaiting_human_review"
            }
            
        except Exception as e:
            logger.error(f"Human intervention trigger failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _is_localized_error(self, errors_by_severity: Dict) -> bool:
        """判断是否是局部错误"""
        critical_errors = errors_by_severity.get("CRITICAL", [])
        
        if len(critical_errors) != 1:
            return False
        
        error = critical_errors[0]
        error_type = error.get("type", "")
        
        # 手部、面部错误通常是局部的
        localized_types = [
            "hand_finger_count_wrong",
            "hand_deformed",
            "face_missing_eyes",
            "face_missing_nose",
            "face_missing_mouth"
        ]
        
        return error_type in localized_types
    
    def _get_critical_errors(self, error_report: Dict[str, Any]) -> list:
        """获取严重错误"""
        errors_by_severity = error_report.get("errors_by_severity", {})
        return errors_by_severity.get("CRITICAL", [])
    
    def _generate_repair_mask(self, errors: list) -> Optional[str]:
        """生成修复 mask"""
        # TODO: 根据错误位置生成 mask
        # 这里返回占位符
        return None
    
    def _select_controlnet_type(self, error_report: Dict[str, Any]) -> str:
        """选择 ControlNet 类型"""
        errors = self._get_critical_errors(error_report)
        
        for error in errors:
            error_type = error.get("type", "")
            
            # 姿态错误 → Pose ControlNet
            if "pose" in error_type:
                return "pose"
            
            # 深度/透视错误 → Depth ControlNet
            if "physics_perspective" in error_type:
                return "depth"
        
        # 默认使用 Canny
        return "canny"
