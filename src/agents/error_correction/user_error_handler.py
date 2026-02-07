"""
用户错误处理器

处理用户手动标注的错误。
"""

import logging
from typing import Dict, Any
import uuid

from .error_annotation import ErrorAnnotation, AnnotationStatus
from .error_classifier import ErrorSeverity


logger = logging.getLogger(__name__)


class UserErrorHandler:
    """
    用户错误处理器
    
    处理用户手动标注和报告的错误。
    """
    
    def __init__(self, blackboard, event_bus, repair_strategy):
        """
        初始化处理器
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            repair_strategy: 修复策略实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.repair_strategy = repair_strategy
        
        logger.info("UserErrorHandler initialized")
    
    async def handle_user_error_report(
        self,
        annotation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        处理用户错误报告
        
        Args:
            annotation_data: 标注数据
            
        Returns:
            Dict: 处理结果
        """
        logger.info(f"Handling user error report for shot {annotation_data.get('shot_id')}")
        
        try:
            # 1. 创建标注对象
            annotation = self._create_annotation(annotation_data)
            
            # 2. 验证标注
            if not self._validate_annotation(annotation):
                return {
                    "success": False,
                    "error": "Invalid annotation data"
                }
            
            # 3. 保存到 Blackboard
            self._save_annotation(annotation)
            
            # 4. 触发修复流程
            repair_result = await self._trigger_repair(annotation)
            
            # 5. 发布事件
            await self._publish_event(annotation, repair_result)
            
            logger.info(f"User error report processed: {annotation.annotation_id}")
            
            return {
                "success": True,
                "annotation_id": annotation.annotation_id,
                "repair_result": repair_result
            }
            
        except Exception as e:
            logger.error(f"Failed to handle user error report: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_annotation(self, data: Dict[str, Any]) -> ErrorAnnotation:
        """创建标注对象"""
        # 生成 annotation_id
        if "annotation_id" not in data:
            data["annotation_id"] = f"ANN-{uuid.uuid4().hex[:8]}"
        
        # 确保必需字段存在
        required_fields = [
            "project_id", "shot_id", "artifact_url",
            "region", "error_type", "error_category",
            "error_description", "severity", "annotated_by"
        ]
        
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        return ErrorAnnotation.from_dict(data)
    
    def _validate_annotation(self, annotation: ErrorAnnotation) -> bool:
        """验证标注"""
        # 检查区域是否有效
        if not annotation.region.coordinates:
            logger.error("Annotation region has no coordinates")
            return False
        
        # 检查错误类型是否有效
        from .error_annotation import ERROR_TYPE_CATEGORIES
        
        if annotation.error_category not in ERROR_TYPE_CATEGORIES:
            logger.error(f"Invalid error category: {annotation.error_category}")
            return False
        
        return True
    
    def _save_annotation(self, annotation: ErrorAnnotation) -> None:
        """保存标注到 Blackboard"""
        try:
            project_id = annotation.project_id
            shot_id = annotation.shot_id
            
            # 获取 shot
            shot = self.blackboard.get_shot(project_id, shot_id)
            
            if not shot:
                logger.error(f"Shot {shot_id} not found")
                return
            
            # 添加标注
            if "user_annotations" not in shot:
                shot["user_annotations"] = []
            
            shot["user_annotations"].append(annotation.to_dict())
            
            # 更新 Blackboard
            self.blackboard.update_shot(project_id, shot_id, shot)
            
            logger.info(f"Annotation saved: {annotation.annotation_id}")
            
        except Exception as e:
            logger.error(f"Failed to save annotation: {e}", exc_info=True)
    
    async def _trigger_repair(
        self,
        annotation: ErrorAnnotation
    ) -> Dict[str, Any]:
        """触发修复流程"""
        try:
            # 根据严重程度选择修复级别
            repair_level = self._select_repair_level(annotation.severity)
            
            # 构建错误报告（模拟自动检测的格式）
            error_report = {
                "errors_by_severity": {
                    annotation.severity.value: [{
                        "type": annotation.error_type,
                        "description": annotation.error_description,
                        "location": annotation.region.to_dict(),
                        "confidence": 1.0  # 用户标注的置信度为 100%
                    }]
                },
                "stats": {
                    "total_errors": 1,
                    "critical_count": 1 if annotation.severity == ErrorSeverity.CRITICAL else 0,
                    "high_count": 1 if annotation.severity == ErrorSeverity.HIGH else 0,
                    "medium_count": 1 if annotation.severity == ErrorSeverity.MEDIUM else 0,
                    "low_count": 1 if annotation.severity == ErrorSeverity.LOW else 0
                },
                "requires_fix": annotation.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
            }
            
            # 应用修复
            repair_result = await self.repair_strategy.apply_repair(
                annotation.project_id,
                annotation.shot_id,
                annotation.artifact_url,
                error_report,
                repair_level
            )
            
            # 更新标注状态
            annotation.set_repair_result(repair_level.value, repair_result)
            self._save_annotation(annotation)
            
            return repair_result
            
        except Exception as e:
            logger.error(f"Failed to trigger repair: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _select_repair_level(self, severity: ErrorSeverity):
        """根据严重程度选择修复级别"""
        from .repair_strategy import RepairLevel
        
        if severity == ErrorSeverity.CRITICAL:
            return RepairLevel.INPAINTING  # 尝试局部修复
        elif severity == ErrorSeverity.HIGH:
            return RepairLevel.CONTROLNET
        elif severity == ErrorSeverity.MEDIUM:
            return RepairLevel.CONTROLNET
        else:
            return RepairLevel.INPAINTING
    
    async def _publish_event(
        self,
        annotation: ErrorAnnotation,
        repair_result: Dict[str, Any]
    ) -> None:
        """发布事件"""
        try:
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=annotation.project_id,
                type=EventType.USER_ERROR_REPORTED,
                actor="ErrorCorrection",
                payload={
                    "annotation_id": annotation.annotation_id,
                    "shot_id": annotation.shot_id,
                    "error_type": annotation.error_type,
                    "severity": annotation.severity.value,
                    "repair_result": repair_result
                }
            ))
            
            logger.info(f"USER_ERROR_REPORTED event published")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}", exc_info=True)
