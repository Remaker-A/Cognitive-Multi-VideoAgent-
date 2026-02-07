"""
ImageGen Agent

负责图像生成任务。
"""

import logging
from typing import Dict, Any

from src.infrastructure.event_bus import Event, EventType
from src.adapters.implementations import SDXLAdapter, QwenAdapter
from .embedding_extractor import EmbeddingExtractor
from .clip_scorer import CLIPScorer


logger = logging.getLogger(__name__)


class ImageGen:
    """
    ImageGen Agent
    
    负责：
    - 图像生成
    - Embedding 提取
    - CLIP 相似度计算
    - 失败重试
    """
    
    def __init__(self, blackboard, event_bus, storage_service=None):
        """
        初始化 ImageGen
        
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
            "sdxl-1.0": SDXLAdapter(),
            "qwen-2.5": QwenAdapter(),
        }
        
        # 初始化工具
        self.embedding_extractor = EmbeddingExtractor()
        self.clip_scorer = CLIPScorer()
        
        # 配置
        self.max_retries = 2
        self.clip_threshold = 0.25
        
        logger.info("ImageGen Agent initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.KEYFRAME_REQUESTED:
                await self.generate_image(event)
            elif event.type == EventType.PROMPT_ADJUSTMENT:
                await self.regenerate_with_adjustment(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def generate_image(self, event: Event) -> None:
        """
        生成图像
        
        Args:
            event: KEYFRAME_REQUESTED 事件
        """
        project_id = event.project_id
        keyframe_request = event.payload.get("keyframe_request", {})
        shot_id = keyframe_request.get("shot_id")
        keyframe_id = keyframe_request.get("keyframe_id")
        
        logger.info(f"Generating image for keyframe {keyframe_id}")
        
        try:
            # 生成图像（带重试）
            result = await self._generate_with_retry(
                project_id,
                keyframe_request,
                retry_count=0
            )
            
            if not result["success"]:
                logger.error(f"Image generation failed after retries")
                # TODO: 上报 ChefAgent
                return
            
            # 保存到 Blackboard
            self.blackboard.update_keyframe(project_id, keyframe_id, {
                "artifact_url": result["artifact_url"],
                "embedding": result.get("embedding"),
                "clip_score": result.get("clip_score"),
                "cost": result.get("cost")
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.IMAGE_GENERATED,
                actor="ImageGen",
                payload={
                    "shot_id": shot_id,
                    "keyframe_id": keyframe_id,
                    "artifact_url": result["artifact_url"],
                    "clip_score": result.get("clip_score"),
                    "cost": result.get("cost")
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Image generated: {keyframe_id}, CLIP: {result.get('clip_score', 0):.4f}")
            
        except Exception as e:
            logger.error(f"Failed to generate image: {e}", exc_info=True)
    
    async def _generate_with_retry(
        self,
        project_id: str,
        keyframe_request: Dict[str, Any],
        retry_count: int
    ) -> Dict[str, Any]:
        """
        带重试的图像生成
        
        Args:
            project_id: 项目 ID
            keyframe_request: Keyframe 请求
            retry_count: 重试次数
            
        Returns:
            Dict: 生成结果
        """
        # 获取 prompt 配置（从 Blackboard）
        shot_id = keyframe_request.get("shot_id")
        shot = self.blackboard.get_shot(project_id, shot_id)
        prompt_config = shot.get("prompt_config", {})
        
        # 选择 adapter (default to qwen-2.5)
        model = prompt_config.get("model", "qwen-2.5")
        adapter = self.adapters.get(model, self.adapters["qwen-2.5"])
        
        # 生成图像
        generation_result = await adapter.generate(
            prompt=prompt_config.get("positive", ""),
            negative_prompt=prompt_config.get("negative", ""),
            seed=prompt_config.get("seed", -1),
            cfg_scale=prompt_config.get("cfg_scale", 7.5),
            steps=prompt_config.get("steps", 30),
            width=keyframe_request.get("width", 1024),
            height=keyframe_request.get("height", 1024)
        )
        
        if not generation_result.success:
            if retry_count < self.max_retries:
                logger.warning(f"Generation failed, retrying ({retry_count + 1}/{self.max_retries})")
                return await self._generate_with_retry(project_id, keyframe_request, retry_count + 1)
            else:
                return {"success": False, "error": generation_result.error}
        
        # 提取 embedding
        embedding = self.embedding_extractor.extract(generation_result.artifact_url)
        
        # 计算 CLIP 相似度
        clip_score = self.clip_scorer.calculate_similarity(
            generation_result.artifact_url,
            prompt_config.get("positive", "")
        )
        
        # 检查质量
        if clip_score and clip_score < self.clip_threshold:
            if retry_count < self.max_retries:
                logger.warning(f"Low CLIP score ({clip_score:.4f}), retrying")
                # TODO: 调整 prompt
                return await self._generate_with_retry(project_id, keyframe_request, retry_count + 1)
        
        return {
            "success": True,
            "artifact_url": generation_result.artifact_url,
            "embedding": embedding,
            "clip_score": clip_score,
            "cost": generation_result.cost
        }
    
    async def regenerate_with_adjustment(self, event: Event) -> None:
        """
        使用调整后的 prompt 重新生成
        
        Args:
            event: PROMPT_ADJUSTMENT 事件
        """
        # TODO: 实现 prompt 调整重生成
        logger.info("Prompt adjustment regeneration not yet implemented")
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ImageGen Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ImageGen Agent stopped")
