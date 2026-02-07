"""
DNA Token 注入器

负责从 DNA Bank 提取和注入视觉一致性 tokens。
"""

import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class DNAInjector:
    """
    DNA Token 注入器
    
    从 DNA Bank 提取角色的视觉一致性 tokens。
    """
    
    def __init__(self, blackboard):
        """
        初始化注入器
        
        Args:
            blackboard: Shared Blackboard 实例
        """
        self.blackboard = blackboard
    
    def get_dna_tokens(self, project_id: str, character_name: str) -> List[str]:
        """
        获取角色的 DNA tokens
        
        Args:
            project_id: 项目 ID
            character_name: 角色名称
            
        Returns:
            List[str]: DNA tokens 列表
        """
        try:
            # 从 Blackboard 获取 DNA Bank
            project = self.blackboard.get_project(project_id)
            
            if not project:
                logger.warning(f"Project {project_id} not found")
                return []
            
            dna_bank = project.get("dna_bank", {})
            
            if character_name not in dna_bank:
                logger.debug(f"No DNA tokens for character: {character_name}")
                return []
            
            character_dna = dna_bank[character_name]
            
            # 提取 tokens
            tokens = []
            
            # 1. 外观特征 tokens
            if "appearance_tokens" in character_dna:
                tokens.extend(character_dna["appearance_tokens"])
            
            # 2. 风格特征 tokens
            if "style_tokens" in character_dna:
                tokens.extend(character_dna["style_tokens"])
            
            # 3. 置信度过滤
            tokens = self.filter_by_confidence(tokens, min_confidence=0.6)
            
            logger.info(f"Extracted {len(tokens)} DNA tokens for {character_name}")
            
            return tokens
            
        except Exception as e:
            logger.error(f"Failed to get DNA tokens: {e}")
            return []
    
    def filter_by_confidence(self, tokens: List[Any], min_confidence: float = 0.6) -> List[str]:
        """
        根据置信度过滤 tokens
        
        Args:
            tokens: Token 列表
            min_confidence: 最小置信度阈值
            
        Returns:
            List[str]: 过滤后的 tokens
        """
        filtered = []
        
        for token in tokens:
            if isinstance(token, dict):
                # Token 是字典格式，包含 text 和 confidence
                confidence = token.get("confidence", 1.0)
                if confidence >= min_confidence:
                    text = token.get("text", str(token))
                    filtered.append(text)
            elif isinstance(token, str):
                # Token 是字符串，直接使用
                filtered.append(token)
            else:
                # 其他类型，转为字符串
                filtered.append(str(token))
        
        return filtered
    
    def get_all_character_tokens(self, project_id: str, characters: List[str]) -> List[str]:
        """
        获取多个角色的 DNA tokens
        
        Args:
            project_id: 项目 ID
            characters: 角色名称列表
            
        Returns:
            List[str]: 所有角色的 DNA tokens
        """
        all_tokens = []
        
        for character in characters:
            tokens = self.get_dna_tokens(project_id, character)
            all_tokens.extend(tokens)
        
        # 去重
        all_tokens = list(dict.fromkeys(all_tokens))
        
        return all_tokens
