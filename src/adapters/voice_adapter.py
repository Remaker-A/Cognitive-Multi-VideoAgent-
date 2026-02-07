"""
语音模型 Adapter 接口
"""

from abc import abstractmethod
from typing import Optional, Dict
import logging

from .base import BaseAdapter
from .schemas import VoiceGenerationResult


logger = logging.getLogger(__name__)


class VoiceModelAdapter(BaseAdapter):
    """
    语音模型 Adapter 抽象类
    
    所有语音合成模型（MiniMax, ElevenLabs 等）必须继承此类。
    """
    
    @abstractmethod
    async def generate(
        self,
        text: str,
        voice_id: str,
        speed: float = 1.0,
        pitch: float = 1.0,
        volume: float = 1.0,
        emotion: Optional[str] = None,
        language: str = "zh",
        sample_rate: int = 24000,
        **kwargs
    ) -> VoiceGenerationResult:
        """
        生成语音
        
        Args:
            text: 文本内容
            voice_id: 声音 ID
            speed: 语速 (0.5-2.0)
            pitch: 音调 (0.5-2.0)
            volume: 音量 (0-1)
            emotion: 情绪（可选）
            language: 语言代码
            sample_rate: 采样率
            **kwargs: 其他模型特定参数
            
        Returns:
            VoiceGenerationResult: 生成结果
        """
        pass
    
    async def clone_voice(
        self,
        audio_samples: list[str],
        name: str,
        **kwargs
    ) -> str:
        """
        克隆声音
        
        Args:
            audio_samples: 音频样本 URL 列表
            name: 声音名称
            **kwargs: 其他参数
            
        Returns:
            str: 新的 voice_id
        """
        raise NotImplementedError("Voice cloning not supported by this adapter")
    
    async def get_available_voices(self) -> Dict[str, Dict]:
        """
        获取可用声音列表
        
        Returns:
            Dict: 声音 ID 到声音信息的映射
        """
        raise NotImplementedError("Voice listing not supported by this adapter")
