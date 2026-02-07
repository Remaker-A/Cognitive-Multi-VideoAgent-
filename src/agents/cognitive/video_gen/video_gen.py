"""
VideoGen Agent

负责视频生成和质量分析。
"""

import logging
from typing import Dict, Any

from src.infrastructure.event_bus import Event, EventType
from src.adapters.implementations import RunwayAdapter
from .frame_extractor import FrameExtractor
from .temporal_coherence import TemporalCoherence
from .optical_flow_analyzer import OpticalFlowAnalyzer


logger = logging.getLogger(__name__)


class VideoGen:
    """
    VideoGen Agent
    
    负责：
    - 视频生成
    - 时间连贯性计算
    - 光流分析
    - 帧 embedding 提取
    """
    
    def __init__(self, blackboard, event_bus, storage_service=None):
        """
        初始化 VideoGen
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            storage_service: Storage Service 实例（可选）
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.storage = storage_service
        
        # 初始化 adapters
        self.adapters = {
            "runway": RunwayAdapter()
        }
        
        # 初始化分析工具
        self.frame_extractor = FrameExtractor()
        self.temporal_coherence = TemporalCoherence()
        self.optical_flow = OpticalFlowAnalyzer()
        
        # 质量阈值
        self.coherence_threshold = 0.85
        self.smoothness_threshold = 0.75
        
        logger.info("VideoGen Agent initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.PREVIEW_VIDEO_REQUESTED:
                await self.generate_preview_video(event)
            elif event.type == EventType.FINAL_VIDEO_REQUESTED:
                await self.generate_final_video(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def generate_preview_video(self, event: Event) -> None:
        """
        生成预览视频
        
        Args:
            event: PREVIEW_VIDEO_REQUESTED 事件
        """
        project_id = event.project_id
        preview_request = event.payload.get("preview_request", {})
        shot_id = preview_request.get("shot_id")
        
        logger.info(f"Generating preview video for shot {shot_id}")
        
        try:
            # 选择 adapter
            model = "runway"  # 默认使用 Runway
            adapter = self.adapters.get(model)
            
            # 生成视频
            generation_result = await adapter.generate(
                prompt=preview_request.get("description", ""),
                duration=preview_request.get("duration", 5.0),
                fps=preview_request.get("fps", 12),  # 预览用低帧率
                width=preview_request.get("resolution", 256),
                height=preview_request.get("resolution", 256)
            )
            
            if not generation_result.success:
                logger.error(f"Video generation failed: {generation_result.error}")
                return
            
            # TODO: 下载视频到本地进行分析
            # 这里假设 artifact_url 是本地路径
            video_path = generation_result.artifact_url
            
            # 分析视频质量
            quality_metrics = await self._analyze_video_quality(video_path)
            
            # 保存到 Blackboard
            self.blackboard.update_shot(project_id, shot_id, {
                "preview_video_url": generation_result.artifact_url,
                "preview_quality": quality_metrics,
                "preview_cost": generation_result.cost
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.PREVIEW_VIDEO_READY,
                actor="VideoGen",
                payload={
                    "shot_id": shot_id,
                    "video_url": generation_result.artifact_url,
                    "quality_metrics": quality_metrics,
                    "cost": generation_result.cost
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Preview video generated: {shot_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate preview video: {e}", exc_info=True)
    
    async def generate_final_video(self, event: Event) -> None:
        """
        生成最终视频
        
        Args:
            event: FINAL_VIDEO_REQUESTED 事件
        """
        # TODO: 实现最终视频生成
        logger.info("Final video generation not yet implemented")
    
    async def _analyze_video_quality(self, video_path: str) -> Dict[str, Any]:
        """
        分析视频质量
        
        Args:
            video_path: 视频路径
            
        Returns:
            Dict: 质量指标
        """
        metrics = {}
        
        # 1. 提取帧
        frames = self.frame_extractor.extract_frames(video_path, num_frames=10)
        
        # 2. 提取 embeddings
        if frames:
            embeddings = self.frame_extractor.extract_embeddings(frames)
            metrics["has_embeddings"] = embeddings is not None
            metrics["num_frames"] = len(frames)
        
        # 3. 计算时间连贯性
        coherence_score = self.temporal_coherence.calculate(video_path)
        if coherence_score is not None:
            metrics["temporal_coherence"] = coherence_score
            metrics["coherence_pass"] = coherence_score >= self.coherence_threshold
        
        # 4. 分析光流
        flow_metrics = self.optical_flow.analyze(video_path)
        if flow_metrics:
            metrics["optical_flow"] = flow_metrics
            metrics["smoothness_pass"] = flow_metrics.get("smoothness", 0) >= self.smoothness_threshold
        
        logger.info(f"Video quality metrics: {metrics}")
        
        return metrics
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("VideoGen Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("VideoGen Agent stopped")
