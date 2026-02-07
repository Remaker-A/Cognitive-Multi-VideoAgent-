"""
ConsistencyGuardian Agent

负责视觉一致性检测和质量保证。
"""

import logging
from typing import Dict, Any, List

from src.infrastructure.event_bus import Event, EventType
from .threshold_manager import ThresholdManager
from .clip_detector import CLIPDetector
from .face_detector import FaceDetector
from .palette_detector import PaletteDetector
from .flow_detector import FlowDetector
from .continuity_checker import ContinuityChecker
from .auto_fix_strategy import AutoFixStrategy


logger = logging.getLogger(__name__)


class ConsistencyGuardian:
    """
    ConsistencyGuardian Agent
    
    负责：
    - CLIP 相似度检测
    - 面部一致性检测
    - 色彩一致性检测
    - 光流流畅度检测
    - 跨 Shot 连贯性检测
    - 自动修复策略
    - 动态阈值管理
    """
    
    def __init__(self, blackboard, event_bus):
        """
        初始化 ConsistencyGuardian
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化检测器
        self.threshold_manager = ThresholdManager()
        self.clip_detector = CLIPDetector()
        self.face_detector = FaceDetector()
        self.palette_detector = PaletteDetector()
        self.flow_detector = FlowDetector()
        self.continuity_checker = ContinuityChecker()
        self.auto_fix_strategy = AutoFixStrategy(blackboard, event_bus)
        
        logger.info("ConsistencyGuardian Agent initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.IMAGE_GENERATED:
                await self.check_image_quality(event)
            elif event.type == EventType.PREVIEW_VIDEO_READY:
                await self.check_video_quality(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def check_image_quality(self, event: Event) -> None:
        """
        检查图像质量
        
        Args:
            event: IMAGE_GENERATED 事件
        """
        project_id = event.project_id
        payload = event.payload
        
        artifact_url = payload.get("artifact_url")
        shot_id = payload.get("shot_id")
        
        logger.info(f"Checking image quality for shot {shot_id}")
        
        try:
            # 获取质量档位
            project = self.blackboard.get_project(project_id)
            quality_tier = project.get("quality_tier", "STANDARD")
            
            # 获取 shot 类型
            shot = self.blackboard.get_shot(project_id, shot_id)
            shot_type = shot.get("type", "general")
            
            # 获取动态阈值
            thresholds = self.threshold_manager.get_dynamic_thresholds(
                quality_tier,
                shot_type
            )
            
            # 运行检测
            qa_results = {
                "shot_id": shot_id,
                "quality_tier": quality_tier,
                "shot_type": shot_type,
                "thresholds": thresholds,
                "checks": {},
                "passed": True
            }
            
            # TODO: 实现具体的检测逻辑
            # 这里是占位符
            
            # 发布 QA 报告
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.QA_REPORT,
                actor="ConsistencyGuardian",
                payload={
                    "qa_results": qa_results
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"QA check completed for {shot_id}: {'PASSED' if qa_results['passed'] else 'FAILED'}")
            
        except Exception as e:
            logger.error(f"Failed to check image quality: {e}", exc_info=True)
    
    async def check_video_quality(self, event: Event) -> None:
        """
        检查视频质量
        
        Args:
            event: PREVIEW_VIDEO_READY 事件
        """
        project_id = event.project_id
        payload = event.payload
        
        video_url = payload.get("video_url")
        shot_id = payload.get("shot_id")
        
        logger.info(f"Checking video quality for shot {shot_id}")
        
        try:
            # 获取质量档位
            project = self.blackboard.get_project(project_id)
            quality_tier = project.get("quality_tier", "STANDARD")
            
            # 获取动态阈值
            thresholds = self.threshold_manager.get_dynamic_thresholds(quality_tier)
            
            # 运行检测
            qa_results = {
                "shot_id": shot_id,
                "quality_tier": quality_tier,
                "thresholds": thresholds,
                "checks": {},
                "passed": True
            }
            
            # 光流流畅度检测
            if video_url:
                # TODO: 下载视频到本地
                # flow_smoothness = self.flow_detector.check_smoothness(video_path)
                pass
            
            # 发布 QA 报告
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.QA_REPORT,
                actor="ConsistencyGuardian",
                payload={
                    "qa_results": qa_results
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Video QA check completed for {shot_id}")
            
        except Exception as e:
            logger.error(f"Failed to check video quality: {e}", exc_info=True)
    
    async def run_qa_checks(
        self,
        project_id: str,
        artifacts: List[Dict[str, Any]],
        quality_tier: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        运行 QA 检测
        
        Args:
            project_id: 项目 ID
            artifacts: 待检测的 artifacts
            quality_tier: 质量档位
            
        Returns:
            Dict: QA 结果
        """
        logger.info(f"Running QA checks for {len(artifacts)} artifacts")
        
        # 获取动态阈值
        thresholds = self.threshold_manager.get_dynamic_thresholds(quality_tier)
        
        results = {
            "total_artifacts": len(artifacts),
            "passed": 0,
            "failed": 0,
            "checks": []
        }
        
        # TODO: 实现批量检测逻辑
        
        return results
    
    async def check_shot_continuity(
        self,
        project_id: str,
        shot1_id: str,
        shot2_id: str
    ) -> Dict[str, Any]:
        """
        检查相邻 shot 的连贯性
        
        Args:
            project_id: 项目 ID
            shot1_id: Shot 1 ID
            shot2_id: Shot 2 ID
            
        Returns:
            Dict: 连贯性检测结果
        """
        logger.info(f"Checking continuity between {shot1_id} and {shot2_id}")
        
        try:
            # 获取 shot 数据
            shot1 = self.blackboard.get_shot(project_id, shot1_id)
            shot2 = self.blackboard.get_shot(project_id, shot2_id)
            
            if not shot1 or not shot2:
                logger.error("Shot not found")
                return {}
            
            # 准备数据
            shot1_data = {
                "shot_id": shot1_id,
                "last_frame": shot1.get("last_frame_url")  # TODO: 从 Blackboard 获取
            }
            
            shot2_data = {
                "shot_id": shot2_id,
                "first_frame": shot2.get("first_frame_url")  # TODO: 从 Blackboard 获取
            }
            
            # 运行连贯性检测
            results = self.continuity_checker.check_shot_continuity(
                shot1_data,
                shot2_data
            )
            
            # 如果连贯性不足，发布事件
            if not results.get("passed"):
                await self.event_bus.publish(Event(
                    project_id=project_id,
                    type=EventType.CONSISTENCY_FAILED,
                    actor="ConsistencyGuardian",
                    payload={
                        "check_type": "shot_continuity",
                        "shot1_id": shot1_id,
                        "shot2_id": shot2_id,
                        "results": results
                    }
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to check shot continuity: {e}", exc_info=True)
            return {}
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ConsistencyGuardian Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ConsistencyGuardian Agent stopped")
