"""
ErrorCorrectionAgent

负责检测和修复 AI 生成内容中的视觉错误。
"""

import logging
from typing import Dict, Any, List

from src.infrastructure.event_bus import Event, EventType
from .error_classifier import ErrorClassifier, ErrorSeverity
from .hand_detector import HandDetector
from .face_detector import FaceDetector
from .pose_detector import PoseDetector
from .physics_detector import PhysicsDetector
from .text_detector import TextDetector
from .repair_strategy import RepairStrategy
from .repair_validator import RepairValidator


logger = logging.getLogger(__name__)


class ErrorCorrection:
    """
    ErrorCorrection Agent
    
    负责：
    - 检测视觉错误
    - 错误严重程度分级
    - 智能修复策略
    - 修复效果验证
    - 发布错误报告
    """
    
    def __init__(self, blackboard, event_bus):
        """
        初始化 ErrorCorrection
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化检测器
        self.error_classifier = ErrorClassifier()
        self.hand_detector = HandDetector()
        self.face_detector = FaceDetector()
        self.pose_detector = PoseDetector()
        self.physics_detector = PhysicsDetector()
        self.text_detector = TextDetector()
        
        # 初始化修复组件
        self.repair_strategy = RepairStrategy(blackboard, event_bus)
        self.repair_validator = RepairValidator({
            "hand": self.hand_detector,
            "face": self.face_detector,
            "pose": self.pose_detector,
            "physics": self.physics_detector,
            "text": self.text_detector
        })
        
        # 初始化用户错误处理器
        from .user_error_handler import UserErrorHandler
        self.user_error_handler = UserErrorHandler(
            blackboard,
            event_bus,
            self.repair_strategy
        )
        
        logger.info("ErrorCorrection Agent initialized with repair and user annotation capabilities")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.IMAGE_GENERATED:
                await self.detect_image_errors(event)
            elif event.type == EventType.PREVIEW_VIDEO_READY:
                await self.detect_video_errors(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def detect_image_errors(self, event: Event) -> None:
        """
        检测图像错误
        
        Args:
            event: IMAGE_GENERATED 事件
        """
        project_id = event.project_id
        payload = event.payload
        
        artifact_url = payload.get("artifact_url")
        shot_id = payload.get("shot_id")
        
        logger.info(f"Detecting errors in image for shot {shot_id}")
        
        try:
            # 运行所有检测器
            all_errors = []
            
            # 1. 手部检测
            hand_errors = self.hand_detector.detect_hand_errors(artifact_url)
            all_errors.extend(hand_errors)
            
            # 2. 面部检测
            face_errors = self.face_detector.detect_face_errors(artifact_url)
            all_errors.extend(face_errors)
            
            # 3. 姿态检测
            pose_errors = self.pose_detector.detect_pose_errors(artifact_url)
            all_errors.extend(pose_errors)
            
            # 4. 物理规律检测
            physics_errors = self.physics_detector.detect_physics_violations(artifact_url)
            all_errors.extend(physics_errors)
            
            # 5. 文字检测
            text_errors = self.text_detector.detect_text_errors(artifact_url)
            all_errors.extend(text_errors)
            
            # 错误分级
            classified = self.error_classifier.classify_errors(all_errors)
            
            # 保存到 Blackboard
            self.blackboard.update_shot(project_id, shot_id, {
                "error_report": classified
            })
            
            # 如果有严重错误，发布事件
            if classified["requires_fix"]:
                await self.event_bus.publish(Event(
                    project_id=project_id,
                    type=EventType.ERROR_DETECTED,
                    actor="ErrorCorrection",
                    payload={
                        "shot_id": shot_id,
                        "error_report": classified,
                        "artifact_url": artifact_url
                    },
                    causation_id=event.event_id
                ))
                
                logger.warning(f"Errors detected in shot {shot_id}: {classified['stats']}")
            else:
                logger.info(f"No significant errors detected in shot {shot_id}")
            
        except Exception as e:
            logger.error(f"Failed to detect image errors: {e}", exc_info=True)
    
    async def detect_video_errors(self, event: Event) -> None:
        """
        检测视频错误
        
        Args:
            event: PREVIEW_VIDEO_READY 事件
        """
        # TODO: 实现视频错误检测
        logger.info("Video error detection not yet implemented")
    
    def detect_errors(
        self,
        artifact_url: str,
        artifact_type: str = "image"
    ) -> Dict[str, Any]:
        """
        检测错误（同步方法）
        
        Args:
            artifact_url: Artifact URL
            artifact_type: Artifact 类型
            
        Returns:
            Dict: 错误报告
        """
        all_errors = []
        
        try:
            if artifact_type == "image":
                # 运行所有检测器
                all_errors.extend(self.hand_detector.detect_hand_errors(artifact_url))
                all_errors.extend(self.face_detector.detect_face_errors(artifact_url))
                all_errors.extend(self.pose_detector.detect_pose_errors(artifact_url))
                all_errors.extend(self.physics_detector.detect_physics_violations(artifact_url))
                all_errors.extend(self.text_detector.detect_text_errors(artifact_url))
            
            # 错误分级
            classified = self.error_classifier.classify_errors(all_errors)
            
            return classified
            
        except Exception as e:
            logger.error(f"Error detection failed: {e}", exc_info=True)
            return {
                "errors_by_severity": {
                    ErrorSeverity.CRITICAL: [],
                    ErrorSeverity.HIGH: [],
                    ErrorSeverity.MEDIUM: [],
                    ErrorSeverity.LOW: []
                },
                "stats": {"total_errors": 0},
                "requires_fix": False
            }
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ErrorCorrection Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ErrorCorrection Agent stopped")
