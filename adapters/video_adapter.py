"""
视频模型 Adapter 接口
"""

from abc import abstractmethod
from typing import Optional, List
import logging

from .base import BaseAdapter
from .schemas import VideoGenerationResult


logger = logging.getLogger(__name__)


class VideoModelAdapter(BaseAdapter):
    """
    视频模型 Adapter 抽象类
    
    所有视频生成模型（Sora, Veo, Runway 等）必须继承此类。
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        duration: float = 5.0,
        fps: int = 24,
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        motion_strength: float = 0.5,
        keyframes: Optional[List[str]] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        生成视频
        
        Args:
            prompt: Prompt 描述
            duration: 视频时长（秒）
            fps: 帧率
            width: 视频宽度
            height: 视频高度
            seed: 随机种子
            motion_strength: 运动强度 (0-1)
            keyframes: 关键帧图像 URL 列表（可选）
            **kwargs: 其他模型特定参数
            
        Returns:
            VideoGenerationResult: 生成结果
        """
        pass
    
    async def extend_video(
        self,
        video_url: str,
        extend_duration: float = 5.0,
        **kwargs
    ) -> VideoGenerationResult:
        """
        延长视频
        
        Args:
            video_url: 原视频 URL
            extend_duration: 延长时长（秒）
            **kwargs: 其他参数
            
        Returns:
            VideoGenerationResult: 延长后的视频
        """
        raise NotImplementedError("Video extension not supported by this adapter")
    
    async def interpolate(
        self,
        start_image_url: str,
        end_image_url: str,
        duration: float = 5.0,
        **kwargs
    ) -> VideoGenerationResult:
        """
        图像插值生成视频
        
        Args:
            start_image_url: 起始图像 URL
            end_image_url: 结束图像 URL
            duration: 视频时长
            **kwargs: 其他参数
            
        Returns:
            VideoGenerationResult: 插值视频
        """
        raise NotImplementedError("Image interpolation not supported by this adapter")
