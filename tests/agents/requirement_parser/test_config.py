"""
RequirementParser Agent 配置测试

Requirements: 7.1, 7.2, 7.3, 7.4, 7.5
"""

import pytest
import os
from unittest.mock import patch
from src.agents.requirement_parser.config import (
    RequirementParserConfig,
    get_config,
    load_config_from_file
)
from src.agents.requirement_parser.exceptions import ConfigurationError


class TestRequirementParserConfig:
    """RequirementParser 配置测试套件"""
    
    def test_config_initialization_with_defaults(self):
        """测试：使用默认值初始化配置"""
        # Arrange & Act
        with patch.dict(os.environ, {"REQ_PARSER_DEEPSEEK_API_KEY": "test_key"}):
            config = RequirementParserConfig()
        
        # Assert
        assert config.agent_name == "RequirementParserAgent"
        assert config.max_retries == 3
        assert config.timeout_seconds == 30
        assert config.confidence_threshold == 0.6
        assert config.default_quality_tier == "balanced"
        assert config.default_aspect_ratio == "9:16"
    
    def test_config_initialization_with_custom_values(self):
        """测试：使用自定义值初始化配置"""
        # Arrange & Act
        config = RequirementParserConfig(
            agent_name="CustomAgent",
            deepseek_api_key="custom_key",
            max_retries=5,
            timeout_seconds=60,
            confidence_threshold=0.7
        )
        
        # Assert
        assert config.agent_name == "CustomAgent"
        assert config.deepseek_api_key == "custom_key"
        assert config.max_retries == 5
        assert config.timeout_seconds == 60
        assert config.confidence_threshold == 0.7
    
    def test_config_validation_missing_api_key(self):
        """测试：缺少API Key时验证失败 (Requirement 7.4)"""
        # Arrange
        config = RequirementParserConfig(deepseek_api_key="")
        
        # Act & Assert
        with pytest.raises(ConfigurationError, match="DeepSeek API Key is required"):
            config.validate_required_config()
    
    def test_config_validation_invalid_confidence_threshold_high(self):
        """测试：置信度阈值过高 (Requirement 7.4, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Confidence threshold must be between 0 and 1"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                confidence_threshold=1.5
            )
    
    def test_config_validation_invalid_confidence_threshold_low(self):
        """测试：置信度阈值过低 (Requirement 7.4, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Confidence threshold must be between 0 and 1"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                confidence_threshold=-0.1
            )
    
    def test_config_validation_negative_max_retries(self):
        """测试：负数的最大重试次数 (Requirement 7.2, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Max retries must be non-negative"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                max_retries=-1
            )
    
    def test_config_validation_excessive_max_retries(self):
        """测试：过大的最大重试次数 (Requirement 7.2, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Max retries should not exceed 10"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                max_retries=15
            )
    
    def test_config_validation_invalid_timeout_zero(self):
        """测试：超时时间为0 (Requirement 7.2, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Timeout seconds must be positive"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                timeout_seconds=0
            )
    
    def test_config_validation_invalid_timeout_negative(self):
        """测试：负数超时时间 (Requirement 7.2, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Timeout seconds must be positive"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                timeout_seconds=-10
            )
    
    def test_config_validation_excessive_timeout(self):
        """测试：过大的超时时间 (Requirement 7.2, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Timeout should not exceed 300 seconds"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                timeout_seconds=500
            )
    
    def test_get_model_config(self):
        """测试：获取模型配置"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            deepseek_api_endpoint="https://test.com/api",
            deepseek_model_name="TestModel",
            timeout_seconds=45,
            max_retries=5
        )
        
        # Act
        model_config = config.get_model_config()
        
        # Assert
        assert model_config["api_key"] == "test_key"
        assert model_config["endpoint"] == "https://test.com/api"
        assert model_config["model_name"] == "TestModel"
        assert model_config["timeout"] == 45
        assert model_config["max_retries"] == 5
    
    def test_get_default_global_spec_config(self):
        """测试：获取默认GlobalSpec配置"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            default_quality_tier="high",
            default_aspect_ratio="16:9",
            default_resolution="1920x1080",
            default_fps=60
        )
        
        # Act
        spec_config = config.get_default_global_spec_config()
        
        # Assert
        assert spec_config["quality_tier"] == "high"
        assert spec_config["aspect_ratio"] == "16:9"
        assert spec_config["resolution"] == "1920x1080"
        assert spec_config["fps"] == 60
    
    def test_config_from_environment_variables(self):
        """测试：从环境变量读取配置"""
        # Arrange
        env_vars = {
            "REQ_PARSER_AGENT_NAME": "EnvAgent",
            "REQ_PARSER_DEEPSEEK_API_KEY": "env_key",
            "REQ_PARSER_MAX_RETRIES": "7",
            "REQ_PARSER_CONFIDENCE_THRESHOLD": "0.8"
        }
        
        # Act
        with patch.dict(os.environ, env_vars, clear=True):
            config = RequirementParserConfig()
        
        # Assert
        assert config.agent_name == "EnvAgent"
        assert config.deepseek_api_key == "env_key"
        assert config.max_retries == 7
        assert config.confidence_threshold == 0.8
    
    def test_config_extra_fields_forbidden(self):
        """测试：禁止额外字段 (Requirement 7.5)"""
        # Act & Assert
        with pytest.raises((ValueError, ConfigurationError)):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                unknown_field="value"
            )
    
    def test_config_validation_invalid_quality_tier(self):
        """测试：无效的质量档位 (Requirement 7.3, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Invalid quality tier"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                default_quality_tier="ultra"
            )
    
    def test_config_validation_invalid_aspect_ratio(self):
        """测试：无效的宽高比 (Requirement 7.3, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Invalid aspect ratio"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                default_aspect_ratio="21:9"
            )
    
    def test_config_validation_invalid_api_endpoint(self):
        """测试：无效的API端点 (Requirement 7.1, 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="API endpoint must start with"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                deepseek_api_endpoint="ftp://invalid.com"
            )
    
    def test_config_validation_invalid_file_size_negative(self):
        """测试：负数文件大小限制 (Requirement 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Max file size must be positive"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                max_file_size_mb=-10
            )
    
    def test_config_validation_excessive_file_size(self):
        """测试：过大的文件大小限制 (Requirement 7.5)"""
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Max file size should not exceed 1000 MB"):
            RequirementParserConfig(
                deepseek_api_key="test_key",
                max_file_size_mb=2000
            )
    
    def test_get_file_processing_config(self):
        """测试：获取文件处理配置"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            max_file_size_mb=50
        )
        
        # Act
        file_config = config.get_file_processing_config()
        
        # Assert
        assert file_config["max_file_size_mb"] == 50
        assert "jpg" in file_config["supported_image_formats"]
        assert "mp4" in file_config["supported_video_formats"]
        assert "mp3" in file_config["supported_audio_formats"]
    
    def test_get_performance_config(self):
        """测试：获取性能配置"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            batch_size=20,
            max_concurrent_requests=10,
            timeout_seconds=45
        )
        
        # Act
        perf_config = config.get_performance_config()
        
        # Assert
        assert perf_config["batch_size"] == 20
        assert perf_config["max_concurrent_requests"] == 10
        assert perf_config["timeout_seconds"] == 45
    
    def test_to_dict_masks_api_key(self):
        """测试：转换为字典时脱敏API Key"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="sk-1234567890abcdefghijklmnop"
        )
        
        # Act
        config_dict = config.to_dict()
        
        # Assert
        assert "deepseek_api_key" in config_dict
        assert config_dict["deepseek_api_key"] != "sk-1234567890abcdefghijklmnop"
        assert "..." in config_dict["deepseek_api_key"]
    
    def test_get_config_function(self):
        """测试：get_config函数 (Requirement 7.4)"""
        # Arrange & Act
        with patch.dict(os.environ, {"REQ_PARSER_DEEPSEEK_API_KEY": "test_key"}):
            config = get_config(validate=False)
        
        # Assert
        assert config is not None
        assert isinstance(config, RequirementParserConfig)
    
    def test_validate_required_config_missing_event_bus(self):
        """测试：缺少Event Bus URL (Requirement 7.4)"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            event_bus_url=""
        )
        
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Event Bus URL is required"):
            config.validate_required_config()
    
    def test_validate_required_config_missing_blackboard(self):
        """测试：缺少Blackboard URL (Requirement 7.4)"""
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            blackboard_url=""
        )
        
        # Act & Assert
        with pytest.raises(ConfigurationError, match="Blackboard URL is required"):
            config.validate_required_config()
    
    def test_config_valid_quality_tiers(self):
        """测试：所有有效的质量档位 (Requirement 7.3)"""
        valid_tiers = ["low", "balanced", "high"]
        
        for tier in valid_tiers:
            config = RequirementParserConfig(
                deepseek_api_key="test_key",
                default_quality_tier=tier
            )
            assert config.default_quality_tier == tier
    
    def test_config_valid_aspect_ratios(self):
        """测试：所有有效的宽高比 (Requirement 7.3)"""
        valid_ratios = ["16:9", "9:16", "1:1", "4:3", "3:4"]
        
        for ratio in valid_ratios:
            config = RequirementParserConfig(
                deepseek_api_key="test_key",
                default_aspect_ratio=ratio
            )
            assert config.default_aspect_ratio == ratio