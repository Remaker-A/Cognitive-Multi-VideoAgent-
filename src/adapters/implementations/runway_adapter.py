"""
Runway Adapter 实现

基于 Runway Gen-3 的视频生成适配器。
"""

import logging
import os
from typing import Optional, List
import aiohttp
import asyncio

from ..video_adapter import VideoModelAdapter
from ..schemas import VideoGenerationResult


logger = logging.getLogger(__name__)


class RunwayAdapter(VideoModelAdapter):
    """
    Runway Gen-3 Adapter
    
    支持 Runway 视频生成。
    """
    
    def __init__(self, api_key: str = None):
        """
        初始化 Runway Adapter
        
        Args:
            api_key: API 密钥
        """
        super().__init__(model_name="runway-gen3", api_key=api_key)
        
        # API 配置
        self.api_url = os.getenv(
            "RUNWAY_API_URL",
            "https://api.runwayml.com/v1/generate"
        )
        
        self.api_key = api_key or os.getenv("RUNWAY_API_KEY", "")
        
        # 参数配置
        self.cost_per_second = 0.05  # $0.05 per second
        self.max_duration = 10  # 最大 10 秒
        
        logger.info(f"Runway Adapter initialized")
    
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
        logger.info(f"Generating video with Runway: {prompt[:50]}...")
        
        # 限制时长
        duration = min(duration, self.max_duration)
        
        try:
            # 构建请求参数
            request_data = {
                "prompt": prompt,
                "duration": duration,
                "resolution": f"{width}x{height}",
                "fps": fps,
                "motion_strength": motion_strength
            }
            
            # 添加种子
            if seed >= 0:
                request_data["seed"] = seed
            
            # 添加关键帧（如果有）
            if keyframes:
                request_data["keyframes"] = keyframes
            
            # 调用 API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                # 1. 提交生成任务
                async with session.post(
                    self.api_url,
                    json=request_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Runway API error: {error_text}")
                        
                        return VideoGenerationResult(
                            success=False,
                            artifact_url="",
                            error=f"API error: {response.status}",
                            cost=0.0
                        )
                    
                    result_data = await response.json()
                    task_id = result_data.get("task_id")
                
                if not task_id:
                    return VideoGenerationResult(
                        success=False,
                        artifact_url="",
                        error="No task_id in response",
                        cost=0.0
                    )
                
                # 2. 轮询任务状态
                video_url = await self._poll_task_status(session, task_id, headers)
                
                if not video_url:
                    return VideoGenerationResult(
                        success=False,
                        artifact_url="",
                        error="Task failed or timeout",
                        cost=0.0
                    )
            
            # 计算帧数
            frames = int(duration * fps)
            
            # 创建结果
            result = VideoGenerationResult(
                success=True,
                artifact_url=video_url,
                duration=duration,
                fps=fps,
                frames=frames,
                width=width,
                height=height,
                format="mp4",
                cost=self.calculate_cost_by_duration(duration),
                metadata={
                    "model": self.model_name,
                    "prompt": prompt,
                    "motion_strength": motion_strength,
                    "seed": seed
                }
            )
            
            logger.info(f"Video generated successfully: {duration}s, {frames} frames")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("Runway API timeout")
            return VideoGenerationResult(
                success=False,
                artifact_url="",
                error="API timeout",
                cost=0.0
            )
        
        except Exception as e:
            logger.error(f"Runway generation failed: {e}", exc_info=True)
            return VideoGenerationResult(
                success=False,
                artifact_url="",
                error=str(e),
                cost=0.0
            )
    
    async def _poll_task_status(
        self,
        session: aiohttp.ClientSession,
        task_id: str,
        headers: dict,
        max_attempts: int = 60,
        interval: float = 5.0
    ) -> Optional[str]:
        """
        轮询任务状态
        
        Args:
            session: HTTP session
            task_id: 任务 ID
            headers: 请求头
            max_attempts: 最大尝试次数
            interval: 轮询间隔（秒）
            
        Returns:
            Optional[str]: 视频 URL
        """
        status_url = f"{self.api_url}/status/{task_id}"
        
        for attempt in range(max_attempts):
            try:
                async with session.get(status_url, headers=headers) as response:
                    if response.status != 200:
                        logger.warning(f"Status check failed: {response.status}")
                        await asyncio.sleep(interval)
                        continue
                    
                    data = await response.json()
                    status = data.get("status")
                    
                    if status == "completed":
                        video_url = data.get("video_url")
                        logger.info(f"Task completed: {task_id}")
                        return video_url
                    
                    elif status == "failed":
                        logger.error(f"Task failed: {data.get('error')}")
                        return None
                    
                    # 仍在处理中
                    logger.debug(f"Task status: {status}, attempt {attempt + 1}/{max_attempts}")
                    await asyncio.sleep(interval)
                    
            except Exception as e:
                logger.error(f"Status check error: {e}")
                await asyncio.sleep(interval)
        
        logger.error(f"Task timeout after {max_attempts} attempts")
        return None
    
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
