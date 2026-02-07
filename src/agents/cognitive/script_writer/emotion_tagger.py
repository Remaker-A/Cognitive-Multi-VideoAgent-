"""
情绪标注器

自动标注 shot 的情绪和氛围。
"""

import logging
from typing import List


logger = logging.getLogger(__name__)


class EmotionTagger:
    """
    情绪标注器
    
    基于关键词匹配和启发式规则标注情绪。
    """
    
    def __init__(self):
        """初始化标注器"""
        # 情绪关键词映射
        self.emotion_keywords = {
            "happy": ["happy", "joyful", "cheerful", "smile", "smiling", "laugh", "laughing", "delight", "merry"],
            "sad": ["sad", "cry", "crying", "tear", "tears", "sorrow", "sorrowful", "melancholy", "grief"],
            "angry": ["angry", "rage", "furious", "mad", "anger", "frustrated", "irritated"],
            "calm": ["calm", "peaceful", "tranquil", "serene", "quiet", "still", "relaxed"],
            "tense": ["tense", "nervous", "anxious", "worried", "uneasy", "stressed"],
            "excited": ["excited", "thrilled", "energetic", "enthusiastic", "eager"],
            "mysterious": ["mysterious", "enigmatic", "unknown", "secret", "hidden"],
            "romantic": ["romantic", "love", "loving", "tender", "affectionate"],
            "dramatic": ["dramatic", "intense", "powerful", "climactic"],
            "nostalgic": ["nostalgic", "reminiscent", "wistful", "longing"]
        }
        
        # 视觉元素到情绪的映射
        self.visual_emotion_map = {
            "sunset": ["warm", "peaceful", "nostalgic"],
            "rain": ["sad", "melancholy", "calm"],
            "storm": ["tense", "dramatic"],
            "sunshine": ["happy", "cheerful"],
            "night": ["mysterious", "calm"],
            "crowd": ["energetic", "excited"],
            "alone": ["lonely", "contemplative"]
        }
    
    def tag_emotions(self, description: str) -> List[str]:
        """
        标注情绪
        
        Args:
            description: Shot 描述
            
        Returns:
            List[str]: 情绪标签列表
        """
        emotions = set()
        desc_lower = description.lower()
        
        # 1. 关键词匹配
        for emotion, keywords in self.emotion_keywords.items():
            if any(keyword in desc_lower for keyword in keywords):
                emotions.add(emotion)
        
        # 2. 视觉元素匹配
        for visual, emotion_tags in self.visual_emotion_map.items():
            if visual in desc_lower:
                emotions.update(emotion_tags)
        
        # 3. 默认情绪
        if not emotions:
            emotions.add("neutral")
        
        result = list(emotions)
        logger.debug(f"Tagged emotions: {result} for description: {description[:50]}...")
        
        return result
    
    def tag_mood_intensity(self, description: str) -> str:
        """
        标注情绪强度
        
        Args:
            description: Shot 描述
            
        Returns:
            str: 强度级别 ("subtle", "moderate", "intense")
        """
        desc_lower = description.lower()
        
        # 强烈关键词
        intense_words = ["very", "extremely", "intensely", "dramatically", "powerfully"]
        if any(word in desc_lower for word in intense_words):
            return "intense"
        
        # 微妙关键词
        subtle_words = ["slightly", "gently", "softly", "subtly", "faintly"]
        if any(word in desc_lower for word in subtle_words):
            return "subtle"
        
        return "moderate"
