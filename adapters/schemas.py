"""
统一输出 Schema

定义所有 Adapter 的标准化输出格式。
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import numpy as np


@dataclass
class GenerationResult:
    """
    基础生成结果
    
    所有 Adapter 的输出基类。
    """
    success: bool
    artifact_url: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    cost: float = 0.0
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "artifact_url": self.artifact_url,
            "metadata": self.metadata,
            "cost": self.cost,
            "error": self.error
        }


@dataclass
class ImageGenerationResult(GenerationResult):
    """图像生成结果"""
    width: int = 1024
    height: int = 1024
    format: str = "png"
    embedding: Optional[np.ndarray] = None
    clip_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = super().to_dict()
        base.update({
            "width": self.width,
            "height": self.height,
            "format": self.format,
            "clip_score": self.clip_score,
            "has_embedding": self.embedding is not None
        })
        return base


@dataclass
class VideoGenerationResult(GenerationResult):
    """视频生成结果"""
    duration: float = 5.0
    fps: int = 24
    frames: int = 120
    width: int = 1024
    height: int = 1024
    format: str = "mp4"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = super().to_dict()
        base.update({
            "duration": self.duration,
            "fps": self.fps,
            "frames": self.frames,
            "width": self.width,
            "height": self.height,
            "format": self.format
        })
        return base


@dataclass
class VoiceGenerationResult(GenerationResult):
    """语音生成结果"""
    duration: float = 0.0
    sample_rate: int = 24000
    format: str = "mp3"
    phoneme_timestamps: Optional[Dict] = None
    voice_embedding: Optional[np.ndarray] = None
    wer: Optional[float] = None  # Word Error Rate
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = super().to_dict()
        base.update({
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "format": self.format,
            "wer": self.wer,
            "has_phoneme_timestamps": self.phoneme_timestamps is not None,
            "has_voice_embedding": self.voice_embedding is not None
        })
        return base


@dataclass
class MusicGenerationResult(GenerationResult):
    """音乐生成结果"""
    duration: float = 30.0
    sample_rate: int = 44100
    format: str = "mp3"
    tempo: Optional[int] = None
    key: Optional[str] = None
    music_markers: Optional[Dict] = None  # Beat markers for editing
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        base = super().to_dict()
        base.update({
            "duration": self.duration,
            "sample_rate": self.sample_rate,
            "format": self.format,
            "tempo": self.tempo,
            "key": self.key,
            "has_music_markers": self.music_markers is not None
        })
        return base
