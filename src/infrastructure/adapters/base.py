"""
基础 Adapter 接口

定义所有模型 Adapter 的基础接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import logging


logger = logging.getLogger(__name__)


class BaseAdapter(ABC):
    """
    基础 Adapter 抽象类
    
    所有模型 Adapter 必须继承此类并实现相应方法。
    """
    
    def __init__(self, model_name: str, api_key: str = None):
        """
        初始化 Adapter
        
        Args:
            model_name: 模型名称
            api_key: API 密钥（可选）
        """
        self.model_name = model_name
        self.api_key = api_key
        logger.info(f"Initialized {self.__class__.__name__} for model: {model_name}")
    
    @abstractmethod
    async def generate(self, **kwargs) -> Any:
        """
        生成接口（抽象方法）
        
        子类必须实现此方法。
        
        Args:
            **kwargs: 生成参数
            
        Returns:
            GenerationResult: 生成结果
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, result: Any) -> float:
        """
        计算成本（抽象方法）
        
        子类必须实现此方法。
        
        Args:
            result: 生成结果
            
        Returns:
            float: 成本（美元）
        """
        pass
    
    def validate_params(self, params: Dict[str, Any], required: list) -> bool:
        """
        验证参数
        
        Args:
            params: 参数字典
            required: 必需参数列表
            
        Returns:
            bool: 验证是否通过
        """
        for param in required:
            if param not in params:
                logger.error(f"Missing required parameter: {param}")
                return False
        
        return True
    
    async def health_check(self) -> bool:
        """
        健康检查
        
        Returns:
            bool: 服务是否健康
        """
        # 默认实现，子类可覆盖
        return True
