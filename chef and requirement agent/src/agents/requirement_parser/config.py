"""
RequirementParser Agent 配置管理

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator
from typing import Optional, List, Dict, Any
import os
from pathlib import Path
from .exceptions import ConfigurationError


class RequirementParserConfig(BaseSettings):
    """
    RequirementParser Agent 配置
    
    从环境变量或 .env 文件读取配置
    
    Requirements:
    - 7.1: 从环境变量读取 API Key 和端点配置
    - 7.2: 支持配置超时时间、重试次数等参数
    - 7.3: 支持配置默认的质量档位和宽高比
    - 7.4: 验证所有必需配置项的存在性
    - 7.5: 配置无效时报错并提供修复建议
    """
    
    # Agent 基础配置
    agent_name: str = "RequirementParserAgent"
    
    # Event Bus 配置
    event_bus_url: str = "redis://localhost:6379"
    
    # Blackboard 配置
    blackboard_url: str = "http://localhost:8000"
    
    # DeepSeek API 配置 (Requirement 7.1)
    deepseek_api_key: str = ""  # 默认为空字符串，允许测试环境不设置
    deepseek_api_endpoint: str = "https://www.sophnet.com/api/open-apis/v1/chat/completions"
    deepseek_model_name: str = "DeepSeek-V3.2"
    
    # 业务配置 (Requirement 7.2)
    max_retries: int = 3
    timeout_seconds: int = 30
    confidence_threshold: float = 0.6
    
    # 默认配置 (Requirement 7.3)
    default_quality_tier: str = "balanced"
    default_aspect_ratio: str = "9:16"
    default_resolution: str = "1080x1920"
    default_fps: int = 30
    
    # 文件处理配置
    max_file_size_mb: int = 100
    supported_image_formats: List[str] = ["jpg", "jpeg", "png", "webp"]
    supported_video_formats: List[str] = ["mp4", "avi", "mov", "mkv"]
    supported_audio_formats: List[str] = ["mp3", "wav", "aac", "m4a"]
    
    # 性能配置
    batch_size: int = 10
    max_concurrent_requests: int = 5
    
    model_config = {
        "env_file": ".env",
        "env_prefix": "REQ_PARSER_",  # 环境变量前缀，例如 REQ_PARSER_DEEPSEEK_API_KEY
        "extra": "forbid"  # 禁止额外字段
    }
    
    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence_threshold(cls, v: float) -> float:
        """验证置信度阈值范围 (Requirement 7.4, 7.5)"""
        if not 0 <= v <= 1:
            raise ConfigurationError(
                f"Confidence threshold must be between 0 and 1. Got: {v}\n"
                f"Fix: Set REQ_PARSER_CONFIDENCE_THRESHOLD to a value between 0.0 and 1.0"
            )
        return v
    
    @field_validator('max_retries')
    @classmethod
    def validate_max_retries(cls, v: int) -> int:
        """验证最大重试次数 (Requirement 7.4, 7.5)"""
        if v < 0:
            raise ConfigurationError(
                f"Max retries must be non-negative. Got: {v}\n"
                f"Fix: Set REQ_PARSER_MAX_RETRIES to a non-negative integer (e.g., 3)"
            )
        if v > 10:
            raise ConfigurationError(
                f"Max retries should not exceed 10 for reasonable performance. Got: {v}\n"
                f"Fix: Set REQ_PARSER_MAX_RETRIES to a value between 0 and 10"
            )
        return v
    
    @field_validator('timeout_seconds')
    @classmethod
    def validate_timeout(cls, v: int) -> int:
        """验证超时时间 (Requirement 7.4, 7.5)"""
        if v <= 0:
            raise ConfigurationError(
                f"Timeout seconds must be positive. Got: {v}\n"
                f"Fix: Set REQ_PARSER_TIMEOUT_SECONDS to a positive integer (e.g., 30)"
            )
        if v > 300:
            raise ConfigurationError(
                f"Timeout should not exceed 300 seconds (5 minutes). Got: {v}\n"
                f"Fix: Set REQ_PARSER_TIMEOUT_SECONDS to a value between 1 and 300"
            )
        return v
    
    @field_validator('default_quality_tier')
    @classmethod
    def validate_quality_tier(cls, v: str) -> str:
        """验证质量档位 (Requirement 7.3, 7.5)"""
        valid_tiers = ["low", "balanced", "high"]
        if v not in valid_tiers:
            raise ConfigurationError(
                f"Invalid quality tier: {v}\n"
                f"Fix: Set REQ_PARSER_DEFAULT_QUALITY_TIER to one of: {', '.join(valid_tiers)}"
            )
        return v
    
    @field_validator('default_aspect_ratio')
    @classmethod
    def validate_aspect_ratio(cls, v: str) -> str:
        """验证宽高比格式 (Requirement 7.3, 7.5)"""
        valid_ratios = ["16:9", "9:16", "1:1", "4:3", "3:4"]
        if v not in valid_ratios:
            raise ConfigurationError(
                f"Invalid aspect ratio: {v}\n"
                f"Fix: Set REQ_PARSER_DEFAULT_ASPECT_RATIO to one of: {', '.join(valid_ratios)}"
            )
        return v
    
    @field_validator('deepseek_api_endpoint')
    @classmethod
    def validate_api_endpoint(cls, v: str) -> str:
        """验证API端点格式 (Requirement 7.1, 7.5)"""
        if not v.startswith(('http://', 'https://')):
            raise ConfigurationError(
                f"API endpoint must start with http:// or https://. Got: {v}\n"
                f"Fix: Set REQ_PARSER_DEEPSEEK_API_ENDPOINT to a valid URL"
            )
        return v
    
    @field_validator('max_file_size_mb')
    @classmethod
    def validate_file_size(cls, v: int) -> int:
        """验证文件大小限制 (Requirement 7.5)"""
        if v <= 0:
            raise ConfigurationError(
                f"Max file size must be positive. Got: {v}\n"
                f"Fix: Set REQ_PARSER_MAX_FILE_SIZE_MB to a positive integer"
            )
        if v > 1000:
            raise ConfigurationError(
                f"Max file size should not exceed 1000 MB. Got: {v}\n"
                f"Fix: Set REQ_PARSER_MAX_FILE_SIZE_MB to a reasonable value (e.g., 100)"
            )
        return v
    
    def validate_required_config(self) -> None:
        """
        验证必需配置项的存在性 (Requirement 7.4)
        
        在生产环境中，某些配置项是必需的。
        在测试环境中，可以使用默认值。
        """
        errors = []
        
        # 验证 API Key (Requirement 7.1, 7.4)
        if not self.deepseek_api_key:
            errors.append(
                "DeepSeek API Key is required.\n"
                "Fix: Set REQ_PARSER_DEEPSEEK_API_KEY environment variable."
            )
        
        # 验证 Event Bus URL
        if not self.event_bus_url:
            errors.append(
                "Event Bus URL is required.\n"
                "Fix: Set REQ_PARSER_EVENT_BUS_URL environment variable."
            )
        
        # 验证 Blackboard URL
        if not self.blackboard_url:
            errors.append(
                "Blackboard URL is required.\n"
                "Fix: Set REQ_PARSER_BLACKBOARD_URL environment variable."
            )
        
        if errors:
            raise ConfigurationError(
                "Configuration validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            )
    
    def get_model_config(self) -> Dict[str, Any]:
        """
        获取模型配置 (Requirement 7.1, 7.2)
        
        Returns:
            包含 API 配置的字典
        """
        return {
            "api_key": self.deepseek_api_key,
            "endpoint": self.deepseek_api_endpoint,
            "model_name": self.deepseek_model_name,
            "timeout": self.timeout_seconds,
            "max_retries": self.max_retries
        }
    
    def get_default_global_spec_config(self) -> Dict[str, Any]:
        """
        获取默认 GlobalSpec 配置 (Requirement 7.3)
        
        Returns:
            包含默认视频配置的字典
        """
        return {
            "quality_tier": self.default_quality_tier,
            "aspect_ratio": self.default_aspect_ratio,
            "resolution": self.default_resolution,
            "fps": self.default_fps
        }
    
    def get_file_processing_config(self) -> Dict[str, Any]:
        """
        获取文件处理配置
        
        Returns:
            包含文件处理限制和支持格式的字典
        """
        return {
            "max_file_size_mb": self.max_file_size_mb,
            "supported_image_formats": self.supported_image_formats,
            "supported_video_formats": self.supported_video_formats,
            "supported_audio_formats": self.supported_audio_formats
        }
    
    def get_performance_config(self) -> Dict[str, Any]:
        """
        获取性能配置
        
        Returns:
            包含性能相关配置的字典
        """
        return {
            "batch_size": self.batch_size,
            "max_concurrent_requests": self.max_concurrent_requests,
            "timeout_seconds": self.timeout_seconds
        }
    
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
            config_dict["deepseek_api_key"] = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"
        return config_dict


# 创建全局配置实例（延迟验证，避免测试时失败）
def get_config(validate: bool = True) -> RequirementParserConfig:
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
        cfg = RequirementParserConfig()
    except Exception as e:
        # 捕获 Pydantic 验证错误并转换为友好的错误消息
        raise ConfigurationError(
            f"Configuration initialization failed: {str(e)}\n"
            f"Please check your environment variables or .env file."
        )
    
    # 只在非测试环境验证配置
    if validate and os.getenv("PYTEST_CURRENT_TEST") is None:
        try:
            cfg.validate_required_config()
        except ConfigurationError as e:
            # 在开发环境中，如果配置不完整，给出友好提示
            if os.getenv("ENVIRONMENT") != "production":
                print(f"Configuration Warning: {e}")
                print("Please check your environment variables or .env file.")
            else:
                # 在生产环境中，配置错误应该导致启动失败
                raise
    
    return cfg


def load_config_from_file(config_file: str) -> RequirementParserConfig:
    """
    从指定文件加载配置 (Requirement 7.1)
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置实例
        
    Raises:
        ConfigurationError: 配置文件不存在或格式错误
    """
    config_path = Path(config_file)
    if not config_path.exists():
        raise ConfigurationError(
            f"Configuration file not found: {config_file}\n"
            f"Fix: Create a .env file or set environment variables directly"
        )
    
    try:
        # 临时设置环境变量以指定配置文件
        original_env_file = os.environ.get("ENV_FILE")
        os.environ["ENV_FILE"] = config_file
        
        cfg = RequirementParserConfig()
        
        # 恢复原始环境变量
        if original_env_file:
            os.environ["ENV_FILE"] = original_env_file
        else:
            os.environ.pop("ENV_FILE", None)
        
        return cfg
    except Exception as e:
        raise ConfigurationError(
            f"Failed to load configuration from {config_file}: {str(e)}"
        )


# 全局配置实例
config = get_config(validate=False)  # 延迟验证，避免导入时失败