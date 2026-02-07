"""
视频生成器 - 使用 Sora2 Adapter

基于 Sora2 视频生成模型。
"""

import os
import logging
from typing import Optional, Dict, Any

import sys
from pathlib import Path

# 添加 src 目录到路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from adapters.implementations.sora2_adapter import Sora2Adapter


logger = logging.getLogger(__name__)


class VideoGenerator:
    """视频生成器 - 使用 Sora2 Adapter"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化视频生成器
        
        Args:
            api_key: API 密钥，如果未提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("VIDEO_API_KEY", "")
        self.adapter = Sora2Adapter(api_key=self.api_key)
        
        logger.info(f"VideoGenerator initialized with Sora2 adapter")
    
    async def generate(
        self,
        prompt: str,
        first_frame_image: Optional[str] = None,
        duration: int = 6,
        resolution: str = "1080P",
        motion_strength: float = 0.5,
        seed: int = -1,
        **kwargs
    ) -> Dict[str, Any]:
        """
        生成视频
        
        Args:
            prompt: 视频描述
            first_frame_image: 首帧图像 URL（可选）
            duration: 视频时长（秒）
            resolution: 视频分辨率（如 "1080P", "720P"）
            motion_strength: 运动强度 (0-1)
            seed: 随机种子
            **kwargs: 其他参数
            
        Returns:
            Dict: 包含生成结果的字典
        """
        try:
            # 解析分辨率
            width, height = self._parse_resolution(resolution)
            
            # 调用 Sora2 adapter
            result = await self.adapter.generate(
                prompt=prompt,
                duration=float(duration),
                fps=24,
                width=width,
                height=height,
                seed=seed,
                motion_strength=motion_strength,
                first_frame_image=first_frame_image,
                **kwargs
            )
            
            # 转换为字典格式
            return {
                "success": result.success,
                "video_url": result.artifact_url,
                "prompt": prompt,
                "task_id": result.metadata.get("task_id") if result.metadata else None,
                "task_status": "SUCCEEDED" if result.success else "FAILED",
                "duration": result.duration,
                "resolution": f"{result.width}x{result.height}",
                "fps": result.fps,
                "frames": result.frames,
                "cost": result.cost,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Video generation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt,
                "task_status": "FAILED"
            }
    
    async def extend_video(
        self,
        video_url: str,
        extend_duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        延长视频
        
        Args:
            video_url: 原视频 URL
            extend_duration: 延长时长（秒）
            **kwargs: 其他参数
            
        Returns:
            Dict: 包含延长结果的字典
        """
        try:
            result = await self.adapter.extend_video(
                video_url=video_url,
                extend_duration=extend_duration,
                **kwargs
            )
            
            return {
                "success": result.success,
                "video_url": result.artifact_url,
                "duration": result.duration,
                "task_status": "SUCCEEDED" if result.success else "FAILED",
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Video extension failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "task_status": "FAILED"
            }
    
    async def interpolate(
        self,
        start_image_url: str,
        end_image_url: str,
        duration: float = 5.0,
        **kwargs
    ) -> Dict[str, Any]:
        """
        图像插值生成视频
        
        Args:
            start_image_url: 起始图像 URL
            end_image_url: 结束图像 URL
            duration: 视频时长
            **kwargs: 其他参数
            
        Returns:
            Dict: 包含插值结果的字典
        """
        try:
            result = await self.adapter.interpolate(
                start_image_url=start_image_url,
                end_image_url=end_image_url,
                duration=duration,
                **kwargs
            )
            
            return {
                "success": result.success,
                "video_url": result.artifact_url,
                "duration": result.duration,
                "task_status": "SUCCEEDED" if result.success else "FAILED",
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Interpolation failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "task_status": "FAILED"
            }
    
    async def generate_from_shots(
        self,
        shots: list,
        resolution: str = "1080P",
        duration: int = 6
    ) -> Dict[str, Any]:
        """
        从镜头列表生成视频
        
        Args:
            shots: 镜头列表，每个镜头包含 description 和 image_url
            resolution: 视频分辨率
            duration: 视频时长
            
        Returns:
            Dict: 包含生成结果的字典
        """
        if not shots:
            return {
                "success": False,
                "error": "No shots provided",
                "task_status": "FAILED"
            }
        
        # 合并所有镜头的描述
        descriptions = [shot.get("description", "") for shot in shots]
        combined_prompt = " | ".join(descriptions)
        
        # 使用第一个镜头的图像作为首帧
        first_frame_image = None
        if shots and "image_url" in shots[0]:
            first_frame_image = shots[0]["image_url"]
        
        return await self.generate(
            prompt=combined_prompt,
            first_frame_image=first_frame_image,
            duration=duration,
            resolution=resolution
        )
    
    def _parse_resolution(self, resolution: str) -> tuple:
        """
        解析分辨率字符串
        
        Args:
            resolution: 分辨率字符串（如 "1080P", "720P", "1024x1024"）
            
        Returns:
            tuple: (width, height)
        """
        resolution_map = {
            "1080P": (1920, 1080),
            "720P": (1280, 720),
            "480P": (854, 480),
            "4K": (3840, 2160),
            "1024x1024": (1024, 1024),
            "1328x1328": (1328, 1328),
        }
        
        # 如果是标准分辨率名称
        if resolution.upper() in resolution_map:
            return resolution_map[resolution.upper()]
        
        # 如果是 "WxH" 格式
        if "x" in resolution.lower():
            try:
                width, height = resolution.lower().split("x")
                return (int(width), int(height))
            except (ValueError, AttributeError):
                pass
        
        # 默认返回 1080P
        logger.warning(f"Unknown resolution: {resolution}, using 1080P")
        return (1920, 1080)
    
    async def close(self):
        """关闭资源"""
        await self.adapter.close()
