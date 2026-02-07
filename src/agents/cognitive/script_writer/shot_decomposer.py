"""
Shot 分解器

将场景描述分解为独立的 shots。
"""

import logging
import re
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class ShotDecomposer:
    """
    Shot 分解器
    
    将场景分解为多个可生成的 shots。
    """
    
    def __init__(self):
        """初始化分解器"""
        # Shot 时长范围（秒）
        self.min_shot_duration = 3
        self.max_shot_duration = 7
        self.default_shot_duration = 5
    
    def break_into_shots(
        self,
        scene: Dict[str, Any],
        target_duration: float
    ) -> List[Dict[str, Any]]:
        """
        将场景分解为 shots
        
        Args:
            scene: 场景数据
            target_duration: 目标时长（秒）
            
        Returns:
            List[Dict]: Shot 列表
        """
        # 如果场景已经包含 shots，直接返回
        if "shots" in scene and scene["shots"]:
            return scene["shots"]
        
        # 从描述中分解
        description = scene.get("description", "")
        
        if not description:
            logger.warning(f"Empty scene description for {scene.get('scene_id')}")
            return []
        
        # 分割句子
        sentences = self._split_sentences(description)
        
        if not sentences:
            return []
        
        # 计算每个 shot 的时长
        num_shots = len(sentences)
        duration_per_shot = target_duration / num_shots
        
        # 调整到合理范围
        if duration_per_shot < self.min_shot_duration:
            # 合并句子
            sentences = self._merge_sentences(sentences, target_duration)
            num_shots = len(sentences)
            duration_per_shot = target_duration / num_shots
        elif duration_per_shot > self.max_shot_duration:
            # 拆分句子
            sentences = self._split_long_sentences(sentences, target_duration)
            num_shots = len(sentences)
            duration_per_shot = target_duration / num_shots
        
        # 创建 shots
        shots = []
        scene_id = scene.get("scene_id", "S001")
        
        for i, sentence in enumerate(sentences):
            shot = {
                "shot_id": f"{scene_id}_{i+1:03d}",
                "description": sentence.strip(),
                "duration": min(max(duration_per_shot, self.min_shot_duration), self.max_shot_duration),
                "characters": scene.get("characters", []),
                "environment": scene.get("environment", ""),
                "type": self._infer_shot_type(sentence),
                "dialogue": self._extract_dialogue(sentence)
            }
            shots.append(shot)
        
        logger.info(f"Decomposed scene {scene_id} into {len(shots)} shots")
        
        return shots
    
    def _split_sentences(self, text: str) -> List[str]:
        """
        分割句子
        
        Args:
            text: 文本
            
        Returns:
            List[str]: 句子列表
        """
        # 使用正则表达式分割
        sentences = re.split(r'[.!?]+\s+', text)
        
        # 过滤空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _merge_sentences(self, sentences: List[str], target_duration: float) -> List[str]:
        """
        合并短句子
        
        Args:
            sentences: 句子列表
            target_duration: 目标时长
            
        Returns:
            List[str]: 合并后的句子列表
        """
        if len(sentences) <= 1:
            return sentences
        
        # 计算需要的 shot 数量
        target_shots = max(1, int(target_duration / self.default_shot_duration))
        
        if len(sentences) <= target_shots:
            return sentences
        
        # 合并句子
        merged = []
        sentences_per_shot = len(sentences) // target_shots
        
        for i in range(0, len(sentences), sentences_per_shot):
            chunk = sentences[i:i+sentences_per_shot]
            merged.append(". ".join(chunk))
        
        return merged
    
    def _split_long_sentences(self, sentences: List[str], target_duration: float) -> List[str]:
        """
        拆分长句子
        
        Args:
            sentences: 句子列表
            target_duration: 目标时长
            
        Returns:
            List[str]: 拆分后的句子列表
        """
        split_sentences = []
        
        for sentence in sentences:
            # 如果句子包含逗号，可以拆分
            if ',' in sentence:
                parts = sentence.split(',')
                # 每2-3个短语组成一个 shot
                for i in range(0, len(parts), 2):
                    chunk = ",".join(parts[i:i+2]).strip()
                    if chunk:
                        split_sentences.append(chunk)
            else:
                split_sentences.append(sentence)
        
        return split_sentences
    
    def _infer_shot_type(self, description: str) -> str:
        """
        推断 shot 类型
        
        Args:
            description: Shot 描述
            
        Returns:
            str: Shot 类型
        """
        desc_lower = description.lower()
        
        # 角色特写
        if any(word in desc_lower for word in ["face", "eyes", "expression", "close-up"]):
            return "character_portrait"
        
        # 动作场景
        if any(word in desc_lower for word in ["walking", "running", "moving", "action"]):
            return "action_scene"
        
        # 环境展示
        if any(word in desc_lower for word in ["landscape", "scenery", "view", "environment"]):
            return "environment_establishing"
        
        # 对话场景
        if any(word in desc_lower for word in ["talking", "speaking", "conversation", "dialogue"]):
            return "dialogue"
        
        return "general"
    
    def _extract_dialogue(self, description: str) -> str:
        """
        提取对话
        
        Args:
            description: Shot 描述
            
        Returns:
            str: 对话内容
        """
        # 查找引号中的内容
        dialogue_match = re.search(r'"([^"]*)"', description)
        if dialogue_match:
            return dialogue_match.group(1)
        
        dialogue_match = re.search(r"'([^']*)'", description)
        if dialogue_match:
            return dialogue_match.group(1)
        
        return ""
