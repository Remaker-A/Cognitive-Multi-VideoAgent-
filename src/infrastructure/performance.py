import asyncio
from typing import List, Any, Callable
from dataclasses import dataclass

@dataclass
class BatchConfig:
    max_concurrent: int = 4
    batch_size: int = 10
    timeout: float = 300.0
    retry_on_failure: bool = True
    max_retries: int = 3

class BatchProcessor:
    def __init__(self, config: BatchConfig):
        self.config = config
        self.stats = {"success": 0, "failed": 0, "retried": 0}

    async def process_batch(self, items: List[Any], processor_func: Callable) -> List[Any]:
        results = []
        # Simple sequential processing for now
        for item in items:
            try:
                res = await processor_func(item)
                results.append(res)
                self.stats["success"] += 1
            except Exception as e:
                results.append(None)
                self.stats["failed"] += 1
        return results

    def get_stats(self):
        return self.stats
