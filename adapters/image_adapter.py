"""
图像模型 Adapter 接口
"""

from abc import abstractmethod
from typing import Optional
import logging

from .base import BaseAdapter
from .schemas import ImageGenerationResult


logger = logging.getLogger(__name__)


class ImageModelAdapter(BaseAdapter):
    """
    图像模型 Adapter 抽象类
    
    所有图像生成模型（SDXL, DALL-E, Midjourney 等）必须继承此类。
    """
    
    @abstractmethod
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
            seed: 随机种子（-1 表示随机）
            cfg_scale: CFG 强度
            steps: 采样步数
            sampler: 采样器名称
            control_map: ControlNet 控制图（可选）
            **kwargs: 其他模型特定参数
            
        Returns:
            ImageGenerationResult: 生成结果
        """
        pass
    
    async def generate_batch(
        self,
        prompts: list[str],
        **kwargs
    ) -> list[ImageGenerationResult]:
        """
        批量生成图像
        
        Args:
            prompts: Prompt 列表
            **kwargs: 生成参数
            
        Returns:
            list[ImageGenerationResult]: 生成结果列表
        """
        results = []
        
        for prompt in prompts:
            result = await self.generate(prompt=prompt, **kwargs)
            results.append(result)
        
        return results
