"""
Adapters - 模型适配器层

提供统一的 AI 模型调用接口。
"""

from .base import BaseAdapter
from .schemas import (
    GenerationResult,
    ImageGenerationResult,
    VideoGenerationResult,
    VoiceGenerationResult,
    MusicGenerationResult
)
from .image_adapter import ImageModelAdapter
from .video_adapter import VideoModelAdapter
from .voice_adapter import VoiceModelAdapter
from .music_adapter import MusicModelAdapter

__all__ = [
    'BaseAdapter',
    'GenerationResult',
    'ImageGenerationResult',
    'VideoGenerationResult',
    'VoiceGenerationResult',
    'MusicGenerationResult',
    'ImageModelAdapter',
    'VideoModelAdapter',
    'VoiceModelAdapter',
    'MusicModelAdapter',
]
