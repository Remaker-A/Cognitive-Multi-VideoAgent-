"""
共享模型管理器 - 单例模式管理所有深度学习模型
"""
import logging
import threading
from typing import Dict, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class ModelType(Enum):
    """模型类型"""
    CLIP = "clip"
    DINOV2 = "dinov2"
    OPTICAL_FLOW = "optical_flow"


@dataclass
class ModelConfig:
    """模型配置"""
    model_type: ModelType
    model_name: str
    device: str = "auto"  # cuda, cpu, auto
    precision: str = "fp16"  # fp32, fp16, int8
    max_batch_size: int = 8
    cache_dir: Optional[str] = None


class SharedModelManager:
    """
    共享模型管理器（单例）

    Features:
    - 单例模式，全局唯一实例
    - 延迟加载模型
    - 自动GPU/CPU回退
    - 引用计数管理
    - 线程安全

    Example:
        manager = SharedModelManager()
        model, processor = manager.get_clip_model()
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self.models: Dict[str, Any] = {}
        self.processors: Dict[str, Any] = {}
        self.ref_counts: Dict[str, int] = {}
        self.device = self._detect_device()

        logger.info(f"SharedModelManager initialized on device: {self.device}")

    def _detect_device(self) -> str:
        """检测可用设备"""
        try:
            import torch
            if torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                logger.info(f"CUDA available: {device_name}")
                return "cuda"
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                logger.info("MPS (Apple Silicon) available")
                return "mps"
            else:
                logger.info("Using CPU")
                return "cpu"
        except ImportError:
            logger.warning("PyTorch not installed, defaulting to CPU")
            return "cpu"

    def get_clip_model(
        self,
        model_name: str = "openai/clip-vit-base-patch32",
        cache_dir: Optional[str] = None
    ) -> Tuple[Any, Any]:
        """
        获取CLIP模型（单例）

        Args:
            model_name: 模型名称
            cache_dir: 缓存目录

        Returns:
            tuple: (model, processor)
        """
        cache_key = f"clip_{model_name}"

        if cache_key not in self.models:
            logger.info(f"Loading CLIP model: {model_name}")
            self._load_clip_model(model_name, cache_key, cache_dir)

        # 增加引用计数
        self.ref_counts[cache_key] = self.ref_counts.get(cache_key, 0) + 1

        return self.models[cache_key], self.processors[cache_key]

    def _load_clip_model(self, model_name: str, cache_key: str, cache_dir: Optional[str] = None):
        """加载CLIP模型"""
        try:
            from transformers import CLIPModel, CLIPProcessor
            import torch

            # 加载模型和处理器
            model = CLIPModel.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )
            processor = CLIPProcessor.from_pretrained(
                model_name,
                cache_dir=cache_dir
            )

            # 移动到设备
            model = model.to(self.device)

            # 设置为评估模式
            model.eval()

            # 可选：使用半精度（仅GPU）
            if self.device == "cuda":
                try:
                    model = model.half()
                    logger.info("Using FP16 precision")
                except Exception as e:
                    logger.warning(f"Failed to convert to FP16: {e}")

            self.models[cache_key] = model
            self.processors[cache_key] = processor

            logger.info(f"CLIP model loaded successfully: {model_name} on {self.device}")

        except Exception as e:
            logger.error(f"Failed to load CLIP model: {e}")
            raise

    def release_model(self, model_type: str, model_name: str):
        """
        释放模型引用

        Args:
            model_type: 模型类型
            model_name: 模型名称
        """
        cache_key = f"{model_type}_{model_name}"

        if cache_key in self.ref_counts:
            self.ref_counts[cache_key] -= 1

            # 如果引用计数为0，可以考虑卸载（可选）
            if self.ref_counts[cache_key] <= 0:
                logger.debug(f"Model {cache_key} ref count is 0, keeping in memory for reuse")

    def get_memory_usage(self) -> Dict[str, Any]:
        """获取内存使用情况"""
        try:
            import torch
            if self.device == "cuda":
                return {
                    "allocated_gb": torch.cuda.memory_allocated() / 1024**3,
                    "reserved_gb": torch.cuda.memory_reserved() / 1024**3,
                    "device": self.device,
                    "device_name": torch.cuda.get_device_name(0)
                }
        except Exception as e:
            logger.warning(f"Failed to get memory usage: {e}")

        return {"device": self.device}

    def clear_cache(self):
        """清理缓存"""
        try:
            import torch
            if self.device == "cuda":
                torch.cuda.empty_cache()
                logger.info("GPU cache cleared")
        except Exception as e:
            logger.warning(f"Failed to clear cache: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "loaded_models": list(self.models.keys()),
            "ref_counts": self.ref_counts.copy(),
            "device": self.device,
            "memory_usage": self.get_memory_usage()
        }


# 全局单例实例
model_manager = SharedModelManager()
