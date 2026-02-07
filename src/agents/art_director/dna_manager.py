"""
DNA Bank 管理器

管理角色的视觉 DNA 和多版本 embeddings。
"""

import logging
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from .merge_strategy import MergeStrategy, MergeStrategyType


logger = logging.getLogger(__name__)


class DNAManager:
    """
    DNA Bank 管理器
    
    负责 DNA 的存储、更新和检索。
    """
    
    def __init__(self, blackboard):
        """
        初始化 DNA Manager
        
        Args:
            blackboard: Shared Blackboard 实例
        """
        self.blackboard = blackboard
        self.confidence_threshold = 0.6
        
        logger.info("DNAManager initialized")
    
    def update_dna_bank(
        self,
        project_id: str,
        character_id: str,
        new_features: Dict[str, Any],
        source: str,
        strategy: MergeStrategyType = MergeStrategyType.WEIGHTED_AVERAGE
    ) -> Dict[str, Any]:
        """
        更新 DNA Bank
        
        Args:
            project_id: 项目 ID
            character_id: 角色 ID
            new_features: 新特征
            source: 来源（如 keyframe_001）
            strategy: 合并策略
            
        Returns:
            Dict: 更新后的 DNA
        """
        logger.info(f"Updating DNA for character: {character_id}")
        
        # 检查置信度
        confidence = new_features.get("confidence", 0)
        
        if confidence < self.confidence_threshold:
            logger.warning(f"Low confidence ({confidence:.4f}), triggering manual review")
            # TODO: 触发人工审核
            return None
        
        # 获取当前 DNA
        current_dna = self.get_dna(project_id, character_id)
        
        if current_dna is None:
            # 创建新 DNA
            current_dna = self._create_new_dna(character_id)
        
        # 添加新版本
        new_version = {
            "version": len(current_dna["embeddings"]) + 1,
            "face_embedding": new_features.get("face_embedding"),
            "palette": new_features.get("palette"),
            "texture": new_features.get("texture"),
            "general_embedding": new_features.get("general_embedding"),
            "weight": 0.0,  # 将在重新平衡时计算
            "confidence": confidence,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        current_dna["embeddings"].append(new_version)
        
        # 重新平衡权重
        MergeStrategy.rebalance_weights(current_dna["embeddings"])
        
        # 合并 embeddings
        merged_embedding = self._merge_embeddings(
            current_dna["embeddings"],
            strategy
        )
        
        current_dna["merged_embedding"] = merged_embedding
        
        # 更新 appearance tokens
        current_dna["appearance_tokens"] = self._generate_appearance_tokens(
            new_features
        )
        
        # 保存到 Blackboard
        self._save_dna(project_id, character_id, current_dna)
        
        logger.info(f"DNA updated: {character_id}, version {new_version['version']}")
        
        return current_dna
    
    def get_dna(
        self,
        project_id: str,
        character_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取 DNA
        
        Args:
            project_id: 项目 ID
            character_id: 角色 ID
            
        Returns:
            Optional[Dict]: DNA 数据
        """
        try:
            project = self.blackboard.get_project(project_id)
            
            if not project:
                return None
            
            dna_bank = project.get("dna_bank", {})
            
            return dna_bank.get(character_id)
            
        except Exception as e:
            logger.error(f"Failed to get DNA: {e}")
            return None
    
    def get_dna_tokens(
        self,
        project_id: str,
        character_id: str,
        version: Optional[int] = None
    ) -> List[str]:
        """
        获取 DNA tokens
        
        Args:
            project_id: 项目 ID
            character_id: 角色 ID
            version: 版本号（None 表示最新）
            
        Returns:
            List[str]: DNA tokens
        """
        dna = self.get_dna(project_id, character_id)
        
        if not dna:
            return []
        
        tokens = dna.get("appearance_tokens", [])
        
        # 添加版本标识
        if version is not None:
            tokens = [f"{token}_v{version}" for token in tokens]
        
        return tokens
    
    def _create_new_dna(self, character_id: str) -> Dict[str, Any]:
        """创建新 DNA"""
        return {
            "character_id": character_id,
            "embeddings": [],
            "merged_embedding": None,
            "appearance_tokens": [],
            "style_tokens": [],
            "created_at": datetime.now().isoformat()
        }
    
    def _merge_embeddings(
        self,
        embeddings: List[Dict[str, Any]],
        strategy: MergeStrategyType
    ) -> Optional[np.ndarray]:
        """合并 embeddings"""
        if strategy == MergeStrategyType.WEIGHTED_AVERAGE:
            return MergeStrategy.weighted_average(embeddings)
        
        elif strategy == MergeStrategyType.LATEST_PRIORITY:
            return MergeStrategy.latest_priority(embeddings)
        
        elif strategy == MergeStrategyType.CONFIDENCE_THRESHOLD:
            return MergeStrategy.confidence_threshold(embeddings)
        
        else:
            logger.warning(f"Unknown strategy: {strategy}, using weighted_average")
            return MergeStrategy.weighted_average(embeddings)
    
    def _generate_appearance_tokens(
        self,
        features: Dict[str, Any]
    ) -> List[str]:
        """
        生成 appearance tokens
        
        基于提取的特征生成描述性 tokens。
        """
        tokens = []
        
        # 从色彩生成 tokens
        palette = features.get("palette", {})
        dominant_colors = palette.get("dominant_colors", [])
        
        if dominant_colors:
            # 取前 2 个主色调
            for color_info in dominant_colors[:2]:
                hex_color = color_info.get("hex", "")
                if hex_color:
                    tokens.append(f"color_{hex_color}")
        
        # TODO: 从其他特征生成更多 tokens
        
        return tokens
    
    def _save_dna(
        self,
        project_id: str,
        character_id: str,
        dna: Dict[str, Any]
    ) -> None:
        """保存 DNA 到 Blackboard"""
        try:
            project = self.blackboard.get_project(project_id)
            
            if not project:
                logger.error(f"Project {project_id} not found")
                return
            
            dna_bank = project.get("dna_bank", {})
            dna_bank[character_id] = dna
            
            self.blackboard.update_project(project_id, {
                "dna_bank": dna_bank
            })
            
        except Exception as e:
            logger.error(f"Failed to save DNA: {e}")
