"""
SDXL Adapter 实现

基于 Stable Diffusion XL 的图像生成适配器。
"""

import logging
import os
from typing import Optional
import aiohttp
import asyncio

from ..image_adapter import ImageModelAdapter
from ..schemas import ImageGenerationResult


logger = logging.getLogger(__name__)


class SDXLAdapter(ImageModelAdapter):
    """
    SDXL (Stable Diffusion XL) Adapter
    
    支持 SDXL 1.0 图像生成。
    """
    
    def __init__(self, api_key: str = None, api_url: str = None):
        """
        初始化 SDXL Adapter
        
        Args:
            api_key: API 密钥
            api_url: API 端点 URL
        """
        super().__init__(model_name="sdxl-1.0", api_key=api_key)
        
        # API 配置
        self.api_url = api_url or os.getenv(
            "SDXL_API_URL",
            "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
        )
        
        self.api_key = api_key or os.getenv("STABILITY_API_KEY", "")
        
        # 参数配置
        self.default_width = 1024
        self.default_height = 1024
        self.cost_per_image = 0.02  # $0.02 per image
        
        logger.info(f"SDXL Adapter initialized with URL: {self.api_url}")
    
    async def generate(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1024,
        height: int = 1024,
        seed: int = -1,
        cfg_scale: float = 7.5,
        steps: int = 30,
        sampler: str = "DPM++ 2M Karras",
        control_map: Optional[dict] = None,
        **kwargs
    ) -> ImageGenerationResult:
        """
        生成图像
        
        Args:
            prompt: 正向 prompt
            negative_prompt: 负向 prompt
            width: 图像宽度
            height: 图像高度
            seed: 随机种子
            cfg_scale: CFG 强度
            steps: 采样步数
            sampler: 采样器（SDXL 不使用此参数）
            control_map: ControlNet（暂不支持）
            **kwargs: 其他参数
            
        Returns:
            ImageGenerationResult: 生成结果
        """
        logger.info(f"Generating image with SDXL: {prompt[:50]}...")
        
        try:
            # 构建请求参数
            request_data = {
                "text_prompts": [
                    {
                        "text": prompt,
                        "weight": 1.0
                    }
                ],
                "cfg_scale": cfg_scale,
                "height": height,
                "width": width,
                "steps": steps,
                "samples": 1
            }
            
            # 添加 negative prompt
            if negative_prompt:
                request_data["text_prompts"].append({
                    "text": negative_prompt,
                    "weight": -1.0
                })
            
            # 添加种子
            if seed >= 0:
                request_data["seed"] = seed
            
            # 调用 API
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.api_url,
                    json=request_data,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=300)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"SDXL API error: {error_text}")
                        
                        return ImageGenerationResult(
                            success=False,
                            artifact_url="",
                            error=f"API error: {response.status}",
                            cost=0.0
                        )
                    
                    result_data = await response.json()
            
            # 提取图像数据
            if not result_data.get("artifacts"):
                return ImageGenerationResult(
                    success=False,
                    artifact_url="",
                    error="No artifacts in response",
                    cost=0.0
                )
            
            artifact = result_data["artifacts"][0]
            
            # 这里应该上传到 S3，暂时使用 base64
            # TODO: 集成 Storage Service
            artifact_url = f"data:image/png;base64,{artifact['base64']}"
            
            # 创建结果
            result = ImageGenerationResult(
                success=True,
                artifact_url=artifact_url,
                width=width,
                height=height,
                format="png",
                cost=self.cost_per_image,
                metadata={
                    "model": self.model_name,
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "seed": artifact.get("seed", seed),
                    "cfg_scale": cfg_scale,
                    "steps": steps
                }
            )
            
            logger.info("Image generated successfully")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error("SDXL API timeout")
            return ImageGenerationResult(
                success=False,
                artifact_url="",
                error="API timeout",
                cost=0.0
            )
        
        except Exception as e:
            logger.error(f"SDXL generation failed: {e}", exc_info=True)
            return ImageGenerationResult(
                success=False,
                artifact_url="",
                error=str(e),
                cost=0.0
            )
    
    def calculate_cost(self, result: ImageGenerationResult) -> float:
        """
        计算成本
        
        Args:
            result: 生成结果
            
        Returns:
            float: 成本（美元）
        """
        if not result.success:
            return 0.0
        
        # SDXL 基础成本
        base_cost = self.cost_per_image
        
        # 根据分辨率调整（超过 1024x1024 可能需要额外费用）
        if result.width > 1024 or result.height > 1024:
            base_cost *= 1.5
        
        return base_cost
