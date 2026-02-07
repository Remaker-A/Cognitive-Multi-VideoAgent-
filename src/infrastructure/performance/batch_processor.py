"""
批处理处理器 - 支持并发批处理和智能分组
"""
import asyncio
from typing import List, Callable, TypeVar, Generic, Optional
from dataclasses import dataclass
import logging

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger(__name__)


@dataclass
class BatchConfig:
    """批处理配置"""
    max_concurrent: int = 4  # 最大并发数
    batch_size: int = 10  # 批次大小
    timeout: float = 300.0  # 超时时间（秒）
    retry_on_failure: bool = True
    max_retries: int = 3


class BatchProcessor(Generic[T, R]):
    """
    通用批处理器

    Features:
    - 并发控制（Semaphore）
    - 批次分组
    - 错误处理和重试
    - 进度跟踪

    Example:
        processor = BatchProcessor(BatchConfig(max_concurrent=4))
        results = await processor.process_batch(
            items=prompts,
            processor_func=generate_image
        )
    """

    def __init__(self, config: BatchConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent)
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "retried": 0
        }

    async def process_batch(
        self,
        items: List[T],
        processor_func: Callable,
        **kwargs
    ) -> List[Optional[R]]:
        """
        批量处理

        Args:
            items: 待处理项列表
            processor_func: 处理函数（可以是async或sync）
            **kwargs: 传递给处理函数的参数

        Returns:
            List[Optional[R]]: 处理结果列表，失败项为None
        """
        self.stats["total"] = len(items)
        logger.info(f"Starting batch processing: {len(items)} items")

        # 创建任务
        tasks = [
            self._process_with_semaphore(item, processor_func, **kwargs)
            for item in items
        ]

        # 并发执行
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理异常
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Item {i} failed: {result}")
                self.stats["failed"] += 1
                final_results.append(None)
            else:
                self.stats["success"] += 1
                final_results.append(result)

        logger.info(f"Batch processing complete: {self.stats}")
        return final_results

    async def _process_with_semaphore(
        self,
        item: T,
        processor_func: Callable,
        **kwargs
    ) -> R:
        """使用信号量控制并发"""
        async with self.semaphore:
            return await self._process_with_retry(item, processor_func, **kwargs)

    async def _process_with_retry(
        self,
        item: T,
        processor_func: Callable,
        **kwargs
    ) -> R:
        """带重试的处理"""
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                # 检查函数是否是协程
                if asyncio.iscoroutinefunction(processor_func):
                    result = await asyncio.wait_for(
                        processor_func(item, **kwargs),
                        timeout=self.config.timeout
                    )
                else:
                    # 同步函数在executor中运行
                    loop = asyncio.get_event_loop()
                    result = await asyncio.wait_for(
                        loop.run_in_executor(None, processor_func, item, **kwargs),
                        timeout=self.config.timeout
                    )
                return result

            except asyncio.TimeoutError:
                last_error = TimeoutError(f"Timeout after {self.config.timeout}s")
                logger.warning(f"Attempt {attempt + 1} timeout for item")
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1} failed: {e}")

            if attempt < self.config.max_retries - 1 and self.config.retry_on_failure:
                self.stats["retried"] += 1
                # 指数退避
                await asyncio.sleep(2 ** attempt)

        raise last_error

    def get_stats(self) -> dict:
        """获取处理统计"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计"""
        self.stats = {
            "total": 0,
            "success": 0,
            "failed": 0,
            "retried": 0
        }
