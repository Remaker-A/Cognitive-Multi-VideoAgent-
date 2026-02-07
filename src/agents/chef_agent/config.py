"""
ChefAgent 配置管理

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Dict, Any


class ConfigurationError(Exception):
    """配置错误异常"""

    pass


class ChefAgentConfig(BaseSettings):
    """
    ChefAgent 配置

    从环境变量或 .env 文件读取配置

    Requirements:
    - 7.1: 从环境变量读取配置
    - 7.2: 支持配置超时时间、重试次数等参数
    - 7.3: 支持配置默认的质量档位和预算参数
    - 7.4: 验证所有必需配置项的存在性
    - 7.5: 配置无效时报错并提供修复建议
    """

    # Agent 基础配置
    agent_name: str = "ChefAgent"

    # Event Bus 配置
    event_bus_url: str = "redis://localhost:6379"

    # Blackboard 配置
    blackboard_url: str = "http://localhost:8000"

    # DeepSeek API 配置（用于 AI 决策辅助）
    deepseek_api_key: str = (
        "HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg"
    )
    deepseek_api_endpoint: str = (
        "https://www.sophnet.com/api/open-apis/v1/chat/completions"
    )
    deepseek_model_name: str = "DeepSeek-V3.2"

    # 预算配置 (Requirement 7.3)
    base_budget_per_second: float = 3.0  # 每秒基准预算（美元）
    quality_multiplier_high: float = 1.5
    quality_multiplier_balanced: float = 1.0
    quality_multiplier_fast: float = 0.6

    # 预算预警阈值 (Requirement 7.3)
    budget_warning_threshold: float = 0.8  # 80%
    budget_exceeded_threshold: float = 1.0  # 100%
    budget_prediction_threshold: float = 1.2  # 120%

    # 失败评估配置 (Requirement 7.2)
    max_retry_count: int = 3
    cost_impact_threshold: float = 20.0  # 美元

    # 人工介入配置 (Requirement 7.2)
    human_gate_timeout_minutes: int = 60

    # 错误恢复配置 (Requirement 7.2)
    max_retries: int = 3
    initial_retry_delay: float = 1.0  # 秒
    retry_backoff_factor: float = 2.0

    # 默认成本估算 (Requirement 7.3)
    default_cost_image: float = 0.05
    default_cost_video_per_second: float = 0.50
    default_cost_music_per_second: float = 0.02
    default_cost_voice_per_second: float = 0.02

    model_config = {
        "env_file": ".env",
        "env_prefix": "CHEF_",  # 环境变量前缀，例如 CHEF_BASE_BUDGET_PER_SECOND
        "extra": "forbid",  # 禁止额外字段
    }

    @field_validator("base_budget_per_second")
    @classmethod
    def validate_base_budget(cls, v: float) -> float:
        """验证基准预算 (Requirement 7.4, 7.5)"""
        if v <= 0:
            raise ConfigurationError(
                f"Base budget per second must be positive. Got: {v}\n"
                f"Fix: Set CHEF_BASE_BUDGET_PER_SECOND to a positive value (e.g., 3.0)"
            )
        if v > 100:
            raise ConfigurationError(
                f"Base budget per second seems too high. Got: {v}\n"
                f"Fix: Set CHEF_BASE_BUDGET_PER_SECOND to a reasonable value (e.g., 3.0)"
            )
        return v

    @field_validator("budget_warning_threshold")
    @classmethod
    def validate_warning_threshold(cls, v: float) -> float:
        """验证预警阈值 (Requirement 7.4, 7.5)"""
        if not 0 < v < 1:
            raise ConfigurationError(
                f"Budget warning threshold must be between 0 and 1. Got: {v}\n"
                f"Fix: Set CHEF_BUDGET_WARNING_THRESHOLD to a value between 0.0 and 1.0 (e.g., 0.8)"
            )
        return v

    @field_validator("max_retry_count")
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """验证最大重试次数 (Requirement 7.4, 7.5)"""
        if v < 0:
            raise ConfigurationError(
                f"Max retry count must be non-negative. Got: {v}\n"
                f"Fix: Set CHEF_MAX_RETRY_COUNT to a non-negative integer (e.g., 3)"
            )
        if v > 10:
            raise ConfigurationError(
                f"Max retry count should not exceed 10. Got: {v}\n"
                f"Fix: Set CHEF_MAX_RETRY_COUNT to a value between 0 and 10"
            )
        return v

    @field_validator("cost_impact_threshold")
    @classmethod
    def validate_cost_threshold(cls, v: float) -> float:
        """验证成本影响阈值 (Requirement 7.4, 7.5)"""
        if v <= 0:
            raise ConfigurationError(
                f"Cost impact threshold must be positive. Got: {v}\n"
                f"Fix: Set CHEF_COST_IMPACT_THRESHOLD to a positive value (e.g., 20.0)"
            )
        return v

    def get_quality_multiplier(self, quality_tier: str) -> float:
        """
        获取质量档位乘数 (Requirement 7.3)

        Args:
            quality_tier: 质量档位（high, balanced, fast）

        Returns:
            float: 质量乘数
        """
        multipliers = {
            "high": self.quality_multiplier_high,
            "balanced": self.quality_multiplier_balanced,
            "fast": self.quality_multiplier_fast,
        }
        return multipliers.get(quality_tier, self.quality_multiplier_balanced)

    def get_default_cost(self, event_type: str) -> float:
        """
        获取默认成本估算 (Requirement 7.3)

        Args:
            event_type: 事件类型

        Returns:
            float: 默认成本（美元）
        """
        cost_map = {
            "IMAGE_GENERATED": self.default_cost_image,
            "VIDEO_GENERATED": self.default_cost_video_per_second,
            "MUSIC_COMPOSED": self.default_cost_music_per_second,
            "VOICE_RENDERED": self.default_cost_voice_per_second,
        }
        return cost_map.get(event_type, 0.01)

    def to_dict(self) -> Dict[str, Any]:
        """
        将配置转换为字典（隐藏敏感信息）

        Returns:
            配置字典，API Key 被脱敏
        """
        config_dict = self.model_dump()
        # 脱敏 API Key
        if config_dict.get("deepseek_api_key"):
            key = config_dict["deepseek_api_key"]
            config_dict["deepseek_api_key"] = (
                f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
            )
        return config_dict


# 创建全局配置实例
def get_config(validate: bool = True) -> ChefAgentConfig:
    """
    获取配置实例 (Requirement 7.4, 7.5)

    Args:
        validate: 是否验证必需配置项

    Returns:
        配置实例

    Raises:
        ConfigurationError: 配置验证失败时
    """
    try:
        cfg = ChefAgentConfig()
    except Exception as e:
        raise ConfigurationError(
            f"Configuration initialization failed: {str(e)}\n"
            f"Please check your environment variables or .env file."
        )

    return cfg


# 全局配置实例
config = get_config(validate=False)  # 延迟验证，避免导入时失败
