"""
图像模型 Adapter 接口

优化：
- 集成批处理器实现真正的并发批量生成
"""

from abc import abstractmethod
from typing import Optional, List
import logging

from .base import BaseAdapter
from .schemas import ImageGenerationResult

# 导入性能优化组件
from src.infrastructure.performance import BatchProcessor, BatchConfig


logger = logging.getLogger(__name__)


class ImageModelAdapter(BaseAdapter):
    """
    图像模型 Adapter 抽象类

    所有图像生成模型（SDXL, DALL-E, Midjourney 等）必须继承此类。

    优化特性：
    - 使用批处理器实现并发批量生成
    - 自动重试和错误处理
    - 可配置的并发数和超时
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 初始化批处理器（可通过配置覆盖）
        batch_config = BatchConfig(
            max_concurrent=kwargs.get('max_concurrent', 4),
            batch_size=kwargs.get('batch_size', 10),
            timeout=kwargs.get('timeout', 300.0),
            retry_on_failure=kwargs.get('retry_on_failure', True),
            max_retries=kwargs.get('max_retries', 3)
        )
        self.batch_processor = BatchProcessor(batch_config)

        logger.info(f"ImageModelAdapter initialized with batch processing (max_concurrent={batch_config.max_concurrent})")
    
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
        prompts: List[str],
        **kwargs
    ) -> List[ImageGenerationResult]:
        """
        批量生成图像（并发优化版本）

        优化：
        - 使用批处理器实现真正的并发生成
        - 自动重试失败的请求
        - 超时控制

        Args:
            prompts: Prompt 列表
            **kwargs: 生成参数

        Returns:
            list[ImageGenerationResult]: 生成结果列表（失败项为None）
        """
        logger.info(f"Starting batch generation for {len(prompts)} prompts (concurrent)")

        # 使用批处理器并发生成
        results = await self.batch_processor.process_batch(
            items=prompts,
            processor_func=lambda prompt: self.generate(prompt=prompt, **kwargs)
        )

        # 获取统计信息
        stats = self.batch_processor.get_stats()
        logger.info(
            f"Batch generation complete: "
            f"success={stats['success']}, "
            f"failed={stats['failed']}, "
            f"retried={stats['retried']}"
        )

        return results
