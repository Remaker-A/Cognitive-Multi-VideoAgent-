"""
图像解码缓存 - 避免重复解码
"""
import logging
from typing import Optional, Dict
from PIL import Image
import io
import base64
import hashlib

logger = logging.getLogger(__name__)


class ImageDecodeCache:
    """
    图像解码缓存

    Features:
    - LRU缓存解码后的图像
    - 基于内容哈希的缓存键
    - 内存限制

    Example:
        cache = ImageDecodeCache(max_size=100)
        image = cache.get_or_decode(image_data)
    """

    def __init__(self, max_size: int = 100):
        """
        初始化缓存

        Args:
            max_size: 最大缓存数量
        """
        self.max_size = max_size
        self._cache: Dict[str, Image.Image] = {}
        self._access_order = []
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0
        }

    def get_or_decode(self, image_data: str) -> Optional[Image.Image]:
        """
        获取或解码图像

        Args:
            image_data: 图像数据（base64或URL）

        Returns:
            Optional[Image.Image]: PIL图像对象
        """
        # 计算缓存键
        cache_key = self._compute_cache_key(image_data)

        # 检查缓存
        if cache_key in self._cache:
            logger.debug(f"Image decode cache hit: {cache_key[:8]}")
            self.stats["hits"] += 1
            self._update_access(cache_key)
            return self._cache[cache_key]

        # 解码图像
        self.stats["misses"] += 1
        image = self._decode_image(image_data)

        if image:
            # 添加到缓存
            self._add_to_cache(cache_key, image)
            logger.debug(f"Image decoded and cached: {cache_key[:8]}")

        return image

    def _compute_cache_key(self, image_data: str) -> str:
        """计算缓存键"""
        # 使用SHA256哈希（只取前1000字符以提高性能）
        sample = image_data[:1000] if len(image_data) > 1000 else image_data
        return hashlib.sha256(sample.encode()).hexdigest()

    def _decode_image(self, image_data: str) -> Optional[Image.Image]:
        """解码图像"""
        try:
            if image_data.startswith("data:image"):
                # Base64解码
                base64_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(base64_data)
                return Image.open(io.BytesIO(image_bytes))
            elif image_data.startswith("http://") or image_data.startswith("https://"):
                # URL加载
                import requests
                response = requests.get(image_data, timeout=10)
                response.raise_for_status()
                return Image.open(io.BytesIO(response.content))
            else:
                # 尝试作为文件路径
                return Image.open(image_data)

        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None

    def _add_to_cache(self, key: str, image: Image.Image):
        """添加到缓存"""
        # 如果缓存已满，移除最旧的
        if len(self._cache) >= self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
            self.stats["evictions"] += 1
            logger.debug(f"Evicted oldest image from cache: {oldest_key[:8]}")

        self._cache[key] = image
        self._access_order.append(key)

    def _update_access(self, key: str):
        """更新访问顺序（LRU）"""
        if key in self._access_order:
            self._access_order.remove(key)
            self._access_order.append(key)

    def clear(self):
        """清空缓存"""
        self._cache.clear()
        self._access_order.clear()
        logger.info("Image decode cache cleared")

    def get_stats(self) -> Dict[str, any]:
        """获取缓存统计"""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0.0

        return {
            **self.stats,
            "total_requests": total_requests,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache),
            "max_size": self.max_size
        }


# 全局单例
image_decode_cache = ImageDecodeCache(max_size=100)
