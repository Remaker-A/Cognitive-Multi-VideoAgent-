"""
音乐模型 Adapter 接口
"""

from abc import abstractmethod
from typing import Optional, List
import logging

from .base import BaseAdapter
from .schemas import MusicGenerationResult


logger = logging.getLogger(__name__)


class MusicModelAdapter(BaseAdapter):
    """
    音乐模型 Adapter 抽象类
    
    所有音乐生成模型（Tunee, Suno 等）必须继承此类。
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        duration: float = 30.0,
        tempo: Optional[int] = None,
        key: Optional[str] = None,
        genre: Optional[str] = None,
        mood: Optional[List[str]] = None,
        instruments: Optional[List[str]] = None,
        sample_rate: int = 44100,
        **kwargs
    ) -> MusicGenerationResult:
        """
        生成音乐
        
        Args:
            prompt: 音乐描述
            duration: 时长（秒）
            tempo: BPM（节奏）
            key: 音调（如 "C major", "A minor"）
            genre: 流派（如 "pop", "classical"）
            mood: 情绪标签列表
            instruments: 乐器列表
            sample_rate: 采样率
            **kwargs: 其他模型特定参数
            
        Returns:
            MusicGenerationResult: 生成结果
        """
        pass
    
    async def extend_music(
        self,
        music_url: str,
        extend_duration: float = 30.0,
        **kwargs
    ) -> MusicGenerationResult:
        """
        延长音乐
        
        Args:
            music_url: 原音乐 URL
            extend_duration: 延长时长（秒）
            **kwargs: 其他参数
            
        Returns:
            MusicGenerationResult: 延长后的音乐
        """
        raise NotImplementedError("Music extension not supported by this adapter")
    
    async def remix(
        self,
        music_url: str,
        remix_style: str,
        **kwargs
    ) -> MusicGenerationResult:
        """
        混音
        
        Args:
            music_url: 原音乐 URL
            remix_style: 混音风格
            **kwargs: 其他参数
            
        Returns:
            MusicGenerationResult: 混音后的音乐
        """
        raise NotImplementedError("Music remix not supported by this adapter")
