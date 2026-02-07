"""
Sora2 Adapter 实现

基于 OmniMaaS API 的 Sora2 视频生成适配器。
"""

import logging
import os
import asyncio
from typing import Optional, List
import httpx

from .video_adapter import VideoModelAdapter
from .schemas import VideoGenerationResult


from src.infrastructure.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class Sora2Adapter(VideoModelAdapter):
    """
    Sora2 Adapter
    
    支持 Sora2 视频生成，通过 OmniMaaS API。
    """
    
    def __init__(self, api_key: str = None):
        """
        初始化 Sora2 Adapter
        
        Args:
            api_key: API 密钥
        """
        super().__init__(model_name="sora-2", api_key=api_key)
        
        # API 配置 removed from init to support dynamic loading in generate
        # self.api_url and self.api_key will be refreshed in generate()
        
        self.cost_per_second = 0.08  # $0.08 per second (Sora2 定价)
        self.max_duration = 10  # 最大 10 秒
        
        # HTTP 客户端配置
        self.http_client = httpx.AsyncClient(
            trust_env=False,
            timeout=600.0
        )
        
        logger.info(f"Sora2 Adapter initialized with URL: {self.api_url}")
    
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
            keyframes: 关键帧图像 URL 列表
            **kwargs: 其他参数
            
        Returns:
            VideoGenerationResult: 生成结果
        """
        logger.info(f"Generating video with Sora2: {prompt[:50]}...")

        # Dynamic Config Loading
        self.api_url = ConfigManager.get("VIDEO_API_URL", "https://api.omnimaas.com/v1")
        # If api_key was passed in init (e.g. override), use it? 
        # But usually we want the system config. 
        # Let's verify: if self.api_key was set in init (via argument), we might want to keep it?
        # But the argument default is None.
        # Let's just always load from ConfigManager for simplicity as per requirements.
        self.api_key = ConfigManager.get("VIDEO_API_KEY", "")

        
        # 限制时长
        duration = min(duration, self.max_duration)
        
        try:
            # 构建分辨率字符串
            size = f"{width}x{height}" if width == 720 and height == 1280 else "720x1280" # Sora2 default
            
            # 构建请求参数
            request_data = {
                "model": self.model_name,
                "prompt": prompt
            }
            
            # 注意：OmniMaaS API 不支持 first_frame_image 参数
            # 如果提供了首帧图像，将其添加到 prompt 中
            if first_frame_image := kwargs.get("first_frame_image"):
                prompt = f"{prompt}\n\nReference image: {first_frame_image}"
                request_data["prompt"] = prompt
            
            logger.info(f"Submitting video generation request to {self.api_url}/videos...")
            logger.info(f"Request data: {request_data}")
            
            # 提交视频生成任务
            response = await self.http_client.post(
                f"{self.api_url}/videos",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=request_data
            )
            
            if response.status_code != 200:
                error_msg = f"Failed to submit video generation task: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return VideoGenerationResult(
                    success=False,
                    artifact_url="",
                    error=error_msg,
                    cost=0.0
                )
            
            task_data = response.json()
            task_id = task_data.get("id")
            status = task_data.get("status")
            
            logger.info(f"Task submitted successfully: {task_id}, status: {status}")
            
            # 轮询任务状态
            max_retries = 60  # 最多轮询 60 次
            retry_interval = 5  # 每次间隔 5 秒
            
            for i in range(max_retries):
                logger.info(f"Polling task status {i+1}/{max_retries}...")
                
                try:
                    response = await self.http_client.get(
                        f"{self.api_url}/videos/{task_id}",
                        headers={
                            "Authorization": f"Bearer {self.api_key}"
                        }
                    )
                    
                    if response.status_code == 200:
                        task_data = response.json()
                        status = task_data.get("status")
                        progress = task_data.get("progress", 0)
                        
                        logger.info(f"Task status: {status}, progress: {progress}%")
                        
                        if status in ["succeeded", "completed"]:
                            logger.info(f"Video generation completed successfully!")
                            
                            # 尝试获取视频 URL
                            video_url = (
                                task_data.get("url") or 
                                task_data.get("video_url") or
                                task_data.get("output", {}).get("url") or
                                task_data.get("result", {}).get("url") or
                                task_data.get("data", {}).get("url")
                            )
                            
                            # 如果没有找到视频 URL，使用任务 ID 构建下载 URL
                            if not video_url:
                                video_url = f"{self.api_url}/videos/{task_id}/download"
                                logger.warning(f"No video URL found in response, using download URL: {video_url}")
                            
                            # 计算帧数
                            frames = int(duration * fps)
                            
                            # 计算成本
                            cost = duration * self.cost_per_second
                            
                            result = VideoGenerationResult(
                                success=True,
                                artifact_url=video_url,
                                duration=duration,
                                fps=fps,
                                width=width,
                                height=height,
                                frames=frames,
                                cost=cost,
                                metadata={
                                    "task_id": task_id,
                                    "status": status,
                                    "progress": progress,
                                    "size": task_data.get("size"),
                                    "created_at": task_data.get("created_at"),
                                    "completed_at": task_data.get("completed_at"),
                                    "expires_at": task_data.get("expires_at")
                                }
                            )
                            
                            logger.info(f"Video generation result: success={result.success}, url={result.artifact_url}")
                            return result
                        
                        elif status == "failed":
                            error_msg = task_data.get("error", "Unknown error")
                            logger.error(f"Video generation failed: {error_msg}")
                            return VideoGenerationResult(
                                success=False,
                                artifact_url="",
                                error=error_msg,
                                cost=0.0,
                                metadata={"task_id": task_id, "status": status}
                            )
                        
                        elif status in ["queued", "processing", "in_progress"]:
                            logger.info(f"Task is {status}...")
                            await asyncio.sleep(retry_interval)
                        
                        else:
                            logger.warning(f"Unknown status: {status}")
                            await asyncio.sleep(retry_interval)
                    
                    else:
                        logger.error(f"Failed to poll task status: {response.status_code} - {response.text}")
                        await asyncio.sleep(retry_interval)
                
                except httpx.RequestError as e:
                    logger.warning(f"Network error polling task status: {e}. Retrying...")
                    await asyncio.sleep(retry_interval)
                except Exception as e:
                    logger.error(f"Error polling task status: {e}", exc_info=True)
                    await asyncio.sleep(retry_interval)
            
            # 超时
            error_msg = f"Task timeout after {max_retries * retry_interval} seconds"
            logger.error(error_msg)
            return VideoGenerationResult(
                success=False,
                artifact_url="",
                error=error_msg,
                cost=0.0,
                metadata={"task_id": task_id, "status": "timeout"}
            )
            
        except Exception as e:
            logger.error(f"Sora2 generation failed: {e}", exc_info=True)
            return VideoGenerationResult(
                success=False,
                artifact_url="",
                error=str(e),
                cost=0.0
            )
    
    async def extend_video(
        self,
        video_url: str,
        extend_duration: float = 5.0,
        **kwargs
    ) -> VideoGenerationResult:
        """
        延长视频（暂未实现）
        
        Args:
            video_url: 原视频 URL
            extend_duration: 延长时长（秒）
            **kwargs: 其他参数
            
        Returns:
            VideoGenerationResult: 延长后的视频
        """
        logger.warning("extend_video not implemented for Sora2 via OmniMaaS API")
        return VideoGenerationResult(
            success=False,
            artifact_url="",
            error="Video extension not supported via OmniMaaS API",
            cost=0.0
        )
    
    async def interpolate(
        self,
        start_image_url: str,
        end_image_url: str,
        duration: float = 5.0,
        **kwargs
    ) -> VideoGenerationResult:
        """
        图像插值生成视频（暂未实现）
        
        Args:
            start_image_url: 起始图像 URL
            end_image_url: 结束图像 URL
            duration: 视频时长
            **kwargs: 其他参数
            
        Returns:
            VideoGenerationResult: 插值视频
        """
        logger.warning("interpolate not implemented for Sora2 via OmniMaaS API")
        return VideoGenerationResult(
            success=False,
            artifact_url="",
            error="Image interpolation not supported via OmniMaaS API",
            cost=0.0
        )
    
    def calculate_cost(self, result: VideoGenerationResult) -> float:
        """
        计算成本
        
        Args:
            result: 生成结果
            
        Returns:
            float: 成本（美元）
        """
        if not result.success:
            return 0.0
        
        return self.calculate_cost_by_duration(result.duration)
    
    def calculate_cost_by_duration(self, duration: float) -> float:
        """根据时长计算成本"""
        return duration * self.cost_per_second
    
    async def close(self):
        """关闭 HTTP 客户端"""
        await self.http_client.aclose()
