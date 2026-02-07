"""
合并策略

定义 DNA embedding 的合并策略。
"""

import logging
import numpy as np
from typing import List, Dict, Any
from enum import Enum


logger = logging.getLogger(__name__)


class MergeStrategyType(str, Enum):
    """合并策略类型"""
    WEIGHTED_AVERAGE = "weighted_average"
    LATEST_PRIORITY = "latest_priority"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    MANUAL_SELECTION = "manual_selection"


class MergeStrategy:
    """
    DNA Embedding 合并策略
    
    提供多种合并算法。
    """
    
    @staticmethod
    def weighted_average(
        embeddings: List[Dict[str, Any]],
        use_confidence: bool = True
    ) -> np.ndarray:
        """
        加权平均合并
        
        Args:
            embeddings: Embedding 列表
            use_confidence: 是否使用置信度作为权重
            
        Returns:
            np.ndarray: 合并后的 embedding
        """
        if not embeddings:
            return None
        
        # 提取 embedding 向量和权重
        vectors = []
        weights = []
        
        for emb in embeddings:
            if emb.get("face_embedding") is not None:
                vectors.append(emb["face_embedding"])
                
                if use_confidence:
                    weights.append(emb.get("confidence", 0.5))
                else:
                    weights.append(emb.get("weight", 1.0))
        
        if not vectors:
            return None
        
        # 归一化权重
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # 加权平均
        merged = np.average(vectors, axis=0, weights=weights)
        
        # 归一化
        merged = merged / np.linalg.norm(merged)
        
        logger.debug(f"Merged {len(vectors)} embeddings using weighted average")
        
        return merged
    
    @staticmethod
    def latest_priority(
        embeddings: List[Dict[str, Any]],
        keep_top_n: int = 3
    ) -> np.ndarray:
        """
        最新优先合并
        
        Args:
            embeddings: Embedding 列表
            keep_top_n: 保留最新的 N 个
            
        Returns:
            np.ndarray: 合并后的 embedding
        """
        if not embeddings:
            return None
        
        # 按版本排序（假设版本号递增）
        sorted_embs = sorted(
            embeddings,
            key=lambda x: x.get("version", 0),
            reverse=True
        )
        
        # 取最新的 N 个
        latest = sorted_embs[:keep_top_n]
        
        # 使用加权平均合并
        return MergeStrategy.weighted_average(latest, use_confidence=True)
    
    @staticmethod
    def confidence_threshold(
        embeddings: List[Dict[str, Any]],
        threshold: float = 0.6
    ) -> np.ndarray:
        """
        置信度过滤合并
        
        Args:
            embeddings: Embedding 列表
            threshold: 置信度阈值
            
        Returns:
            np.ndarray: 合并后的 embedding
        """
        if not embeddings:
            return None
        
        # 过滤低置信度
        filtered = [
            emb for emb in embeddings
            if emb.get("confidence", 0) >= threshold
        ]
        
        if not filtered:
            logger.warning(f"No embeddings above threshold {threshold}")
            # 回退到所有 embeddings
            filtered = embeddings
        
        # 使用加权平均合并
        return MergeStrategy.weighted_average(filtered, use_confidence=True)
    
    @staticmethod
    def rebalance_weights(embeddings: List[Dict[str, Any]]) -> None:
        """
        重新平衡权重
        
        Args:
            embeddings: Embedding 列表（会被修改）
        """
        if not embeddings:
            return
        
        # 计算总置信度
        total_confidence = sum(emb.get("confidence", 0) for emb in embeddings)
        
        if total_confidence == 0:
            # 均匀分配
            weight = 1.0 / len(embeddings)
            for emb in embeddings:
                emb["weight"] = weight
        else:
            # 按置信度分配
            for emb in embeddings:
                emb["weight"] = emb.get("confidence", 0) / total_confidence
        
        logger.debug(f"Rebalanced weights for {len(embeddings)} embeddings")
