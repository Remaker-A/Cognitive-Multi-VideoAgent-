"""
ArtDirector Agent

负责视觉 DNA 管理和特征提取。
"""

import logging
from typing import Dict, Any

from src.infrastructure.event_bus import Event, EventType
from .feature_extractor import FeatureExtractor
from .dna_manager import DNAManager
from .merge_strategy import MergeStrategyType


logger = logging.getLogger(__name__)


class ArtDirector:
    """
    ArtDirector Agent
    
    负责：
    - 视觉特征提取
    - DNA Bank 更新
    - 多版本 embedding 管理
    - Prompt 调整建议
    """
    
    def __init__(self, blackboard, event_bus):
        """
        初始化 ArtDirector
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化组件
        self.feature_extractor = FeatureExtractor()
        self.dna_manager = DNAManager(blackboard)
        
        logger.info("ArtDirector Agent initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.IMAGE_GENERATED:
                await self.extract_and_update_dna(event)
            elif event.type == EventType.PREVIEW_VIDEO_READY:
                await self.extract_from_video(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def extract_and_update_dna(self, event: Event) -> None:
        """
        从图像提取特征并更新 DNA
        
        Args:
            event: IMAGE_GENERATED 事件
        """
        project_id = event.project_id
        payload = event.payload
        
        artifact_url = payload.get("artifact_url")
        keyframe_id = payload.get("keyframe_id")
        
        if not artifact_url:
            logger.warning("No artifact_url in event")
            return
        
        logger.info(f"Extracting features from {keyframe_id}")
        
        try:
            # 1. 提取特征
            features = self.feature_extractor.extract_features(artifact_url)
            
            # 2. 获取角色信息
            # TODO: 从 keyframe 获取角色列表
            characters = self._get_characters_from_keyframe(project_id, keyframe_id)
            
            if not characters:
                logger.info("No characters in keyframe, skipping DNA update")
                return
            
            # 3. 为每个角色更新 DNA
            for character_id in characters:
                dna = self.dna_manager.update_dna_bank(
                    project_id,
                    character_id,
                    features,
                    source=keyframe_id,
                    strategy=MergeStrategyType.WEIGHTED_AVERAGE
                )
                
                if dna:
                    # 发布 DNA 更新事件
                    await self.event_bus.publish(Event(
                        project_id=project_id,
                        type=EventType.DNA_BANK_UPDATED,
                        actor="ArtDirector",
                        payload={
                            "character_id": character_id,
                            "version": len(dna["embeddings"]),
                            "confidence": features.get("confidence"),
                            "source": keyframe_id
                        },
                        causation_id=event.event_id
                    ))
                    
                    logger.info(f"DNA updated for {character_id}")
            
        except Exception as e:
            logger.error(f"Failed to extract and update DNA: {e}", exc_info=True)
    
    async def extract_from_video(self, event: Event) -> None:
        """
        从视频提取特征
        
        Args:
            event: PREVIEW_VIDEO_READY 事件
        """
        # TODO: 实现视频特征提取
        logger.info("Video feature extraction not yet implemented")
    
    def suggest_prompt_adjustments(
        self,
        project_id: str,
        shot_id: str
    ) -> Dict[str, Any]:
        """
        建议 prompt 调整
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            
        Returns:
            Dict: Prompt 调整建议
        """
        try:
            # 获取 shot 信息
            shot = self.blackboard.get_shot(project_id, shot_id)
            characters = shot.get("characters", [])
            
            if not characters:
                return {}
            
            # 获取 DNA tokens
            dna_tokens = []
            for character_id in characters:
                tokens = self.dna_manager.get_dna_tokens(
                    project_id,
                    character_id
                )
                dna_tokens.extend(tokens)
            
            adjustments = {
                "dna_tokens": dna_tokens,
                "weight_adjustments": {
                    "character_consistency": 1.2,
                    "color_palette": 1.1
                },
                "negative_prompts": [
                    "inconsistent_face",
                    "color_shift",
                    "different_appearance"
                ]
            }
            
            return adjustments
            
        except Exception as e:
            logger.error(f"Failed to suggest prompt adjustments: {e}")
            return {}
    
    def _get_characters_from_keyframe(
        self,
        project_id: str,
        keyframe_id: str
    ) -> list:
        """从 keyframe 获取角色列表"""
        try:
            # TODO: 实现从 Blackboard 获取 keyframe 的角色信息
            # 这里返回空列表作为占位符
            return []
            
        except Exception as e:
            logger.error(f"Failed to get characters: {e}")
            return []
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ArtDirector Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ArtDirector Agent stopped")
