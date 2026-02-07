"""
RequirementParser Agent 閰嶇疆绠＄悊灞炴€ф祴璇?

Property 7: Configuration Management
Validates: Requirements 7.1, 7.2, 7.3, 7.4, 7.5

Feature: requirement-parser-agent, Property 7: Configuration Management
"""

import pytest
import os
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import patch
from src.agents.requirement_parser.config import (
    RequirementParserConfig,
    get_config
)
from src.agents.requirement_parser.exceptions import ConfigurationError


# 绛栫暐锛氱敓鎴愭湁鏁堢殑閰嶇疆鍊?
valid_api_keys = st.text(min_size=10, max_size=100, alphabet=st.characters(
    whitelist_categories=('Lu', 'Ll', 'Nd'),
    whitelist_characters='-_'
))

valid_urls = st.sampled_from([
    "http://localhost:8000",
    "https://api.example.com",
    "https://test.sophnet.com/api",
    "http://192.168.1.1:9000"
])

valid_quality_tiers = st.sampled_from(["low", "balanced", "high"])
valid_aspect_ratios = st.sampled_from(["16:9", "9:16", "1:1", "4:3", "3:4"])
valid_confidence_thresholds = st.floats(min_value=0.0, max_value=1.0)
valid_max_retries = st.integers(min_value=0, max_value=10)
valid_timeouts = st.integers(min_value=1, max_value=300)
valid_file_sizes = st.integers(min_value=1, max_value=1000)


class TestConfigurationManagementProperty:
    """閰嶇疆绠＄悊灞炴€ф祴璇曞浠?""
    
    @given(
        api_key=valid_api_keys,
        endpoint=valid_urls,
        max_retries=valid_max_retries,
        timeout=valid_timeouts,
        confidence=valid_confidence_thresholds
    )
    @settings(max_examples=20)
    def test_property_valid_config_always_initializes(
        self,
        api_key: str,
        endpoint: str,
        max_retries: int,
        timeout: int,
        confidence: float
    ):
        """
        Property 7: Configuration Management
        
        For any valid configuration values, the RequirementParserConfig should
        successfully initialize without raising exceptions.
        
        Validates: Requirements 7.1, 7.2, 7.4
        """
        # Act
        config = RequirementParserConfig(
            deepseek_api_key=api_key,
            deepseek_api_endpoint=endpoint,
            max_retries=max_retries,
            timeout_seconds=timeout,
            confidence_threshold=confidence
        )
        
        # Assert
        assert config.deepseek_api_key == api_key
        assert config.deepseek_api_endpoint == endpoint
        assert config.max_retries == max_retries
        assert config.timeout_seconds == timeout
        assert config.confidence_threshold == confidence
    
    @given(
        quality_tier=valid_quality_tiers,
        aspect_ratio=valid_aspect_ratios
    )
    @settings(max_examples=20)
    def test_property_default_config_values_are_valid(
        self,
        quality_tier: str,
        aspect_ratio: str
    ):
        """
        Property 7: Configuration Management
        
        For any valid quality tier and aspect ratio, the configuration should
        accept these values and return them correctly in the default config.
        
        Validates: Requirements 7.3
        """
        # Act
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            default_quality_tier=quality_tier,
            default_aspect_ratio=aspect_ratio
        )
        
        default_config = config.get_default_global_spec_config()
        
        # Assert
        assert default_config["quality_tier"] == quality_tier
        assert default_config["aspect_ratio"] == aspect_ratio
        assert "resolution" in default_config
        assert "fps" in default_config
    
    @given(
        confidence=st.floats(min_value=-10.0, max_value=-0.01) | st.floats(min_value=1.01, max_value=10.0)
    )
    @settings(max_examples=20)
    def test_property_invalid_confidence_always_fails(self, confidence: float):
        """
        Property 7: Configuration Management
        
        For any confidence threshold outside [0, 1], the configuration should
        raise a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.4, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                confidence_threshold=confidence
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "Confidence threshold" in error_message
        assert "Fix:" in error_message or "between 0 and 1" in error_message
    
    @given(
        max_retries=st.integers(min_value=-100, max_value=-1)
    )
    @settings(max_examples=20)
    def test_property_negative_retries_always_fails(self, max_retries: int):
        """
        Property 7: Configuration Management
        
        For any negative max_retries value, the configuration should raise
        a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.2, 7.4, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                max_retries=max_retries
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "Max retries" in error_message
        assert "Fix:" in error_message or "non-negative" in error_message
    
    @given(
        timeout=st.integers(min_value=-100, max_value=0)
    )
    @settings(max_examples=20)
    def test_property_invalid_timeout_always_fails(self, timeout: int):
        """
        Property 7: Configuration Management
        
        For any non-positive timeout value, the configuration should raise
        a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.2, 7.4, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                timeout_seconds=timeout
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "Timeout" in error_message
        assert "Fix:" in error_message or "positive" in error_message
    
    @given(
        quality_tier=st.text(min_size=1, max_size=20).filter(
            lambda x: x not in ["low", "balanced", "high"]
        )
    )
    @settings(max_examples=20)
    def test_property_invalid_quality_tier_always_fails(self, quality_tier: str):
        """
        Property 7: Configuration Management
        
        For any quality tier not in the valid set, the configuration should
        raise a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.3, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                default_quality_tier=quality_tier
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "quality tier" in error_message.lower()
        assert "Fix:" in error_message
    
    @given(
        aspect_ratio=st.text(min_size=1, max_size=10).filter(
            lambda x: x not in ["16:9", "9:16", "1:1", "4:3", "3:4"]
        )
    )
    @settings(max_examples=20)
    def test_property_invalid_aspect_ratio_always_fails(self, aspect_ratio: str):
        """
        Property 7: Configuration Management
        
        For any aspect ratio not in the valid set, the configuration should
        raise a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.3, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                default_aspect_ratio=aspect_ratio
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "aspect ratio" in error_message.lower()
        assert "Fix:" in error_message
    
    @given(
        endpoint=st.text(min_size=1, max_size=50).filter(
            lambda x: not x.startswith(('http://', 'https://'))
        )
    )
    @settings(max_examples=20)
    def test_property_invalid_endpoint_always_fails(self, endpoint: str):
        """
        Property 7: Configuration Management
        
        For any API endpoint not starting with http:// or https://, the
        configuration should raise a ConfigurationError with a helpful message.
        
        Validates: Requirements 7.1, 7.5
        """
        # Act & Assert
        with pytest.raises(ConfigurationError) as exc_info:
            RequirementParserConfig(
                deepseek_api_key="test_key",
                deepseek_api_endpoint=endpoint
            )
        
        # Verify error message contains helpful information
        error_message = str(exc_info.value)
        assert "endpoint" in error_message.lower()
        assert "Fix:" in error_message
    
    @given(
        api_key=valid_api_keys,
        max_retries=valid_max_retries,
        timeout=valid_timeouts
    )
    @settings(max_examples=20)
    def test_property_model_config_contains_all_fields(
        self,
        api_key: str,
        max_retries: int,
        timeout: int
    ):
        """
        Property 7: Configuration Management
        
        For any valid configuration, get_model_config() should return a
        dictionary containing all required fields for API communication.
        
        Validates: Requirements 7.1, 7.2
        """
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key=api_key,
            max_retries=max_retries,
            timeout_seconds=timeout
        )
        
        # Act
        model_config = config.get_model_config()
        
        # Assert - all required fields present
        assert "api_key" in model_config
        assert "endpoint" in model_config
        assert "model_name" in model_config
        assert "timeout" in model_config
        assert "max_retries" in model_config
        
        # Assert - values match
        assert model_config["api_key"] == api_key
        assert model_config["max_retries"] == max_retries
        assert model_config["timeout"] == timeout
    
    @given(
        file_size=valid_file_sizes
    )
    @settings(max_examples=20)
    def test_property_file_processing_config_valid(self, file_size: int):
        """
        Property 7: Configuration Management
        
        For any valid file size limit, get_file_processing_config() should
        return a dictionary with all file processing settings.
        
        Validates: Requirements 7.2
        """
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key="test_key",
            max_file_size_mb=file_size
        )
        
        # Act
        file_config = config.get_file_processing_config()
        
        # Assert
        assert file_config["max_file_size_mb"] == file_size
        assert "supported_image_formats" in file_config
        assert "supported_video_formats" in file_config
        assert "supported_audio_formats" in file_config
        assert len(file_config["supported_image_formats"]) > 0
        assert len(file_config["supported_video_formats"]) > 0
        assert len(file_config["supported_audio_formats"]) > 0
    
    @given(
        api_key=valid_api_keys
    )
    @settings(max_examples=20)
    def test_property_to_dict_always_masks_api_key(self, api_key: str):
        """
        Property 7: Configuration Management
        
        For any API key, to_dict() should mask the key to prevent accidental
        exposure in logs or error messages.
        
        Validates: Requirements 7.1, 7.5
        """
        # Arrange
        assume(len(api_key) > 12)  # Only test keys long enough to mask
        
        config = RequirementParserConfig(deepseek_api_key=api_key)
        
        # Act
        config_dict = config.to_dict()
        
        # Assert
        assert "deepseek_api_key" in config_dict
        masked_key = config_dict["deepseek_api_key"]
        
        # Key should be masked (not equal to original)
        assert masked_key != api_key
        
        # Masked key should contain ellipsis
        assert "..." in masked_key
    
    @given(
        env_prefix=st.text(min_size=1, max_size=20, alphabet=st.characters(
            whitelist_categories=('Lu',),
            whitelist_characters='_'
        )),
        api_key=valid_api_keys
    )
    @settings(max_examples=10)
    def test_property_environment_variable_reading(
        self,
        env_prefix: str,
        api_key: str
    ):
        """
        Property 7: Configuration Management
        
        For any environment variable with the correct prefix, the configuration
        should read and apply the value correctly.
        
        Validates: Requirements 7.1
        """
        # Arrange
        env_var_name = f"REQ_PARSER_DEEPSEEK_API_KEY"
        
        # Act
        with patch.dict(os.environ, {env_var_name: api_key}, clear=False):
            config = RequirementParserConfig()
        
        # Assert
        assert config.deepseek_api_key == api_key
    
    @given(
        api_key=valid_api_keys,
        event_bus_url=valid_urls,
        blackboard_url=valid_urls
    )
    @settings(max_examples=20)
    def test_property_validate_required_config_succeeds_with_all_fields(
        self,
        api_key: str,
        event_bus_url: str,
        blackboard_url: str
    ):
        """
        Property 7: Configuration Management
        
        For any configuration with all required fields set, validate_required_config()
        should succeed without raising exceptions.
        
        Validates: Requirements 7.4
        """
        # Arrange
        config = RequirementParserConfig(
            deepseek_api_key=api_key,
            event_bus_url=event_bus_url,
            blackboard_url=blackboard_url
        )
        
        # Act & Assert - should not raise
        config.validate_required_config()
    
    def test_property_missing_required_fields_always_fails(self):
        """
        Property 7: Configuration Management
        
        For any configuration missing required fields (API key, event bus URL,
        or blackboard URL), validate_required_config() should raise a
        ConfigurationError with helpful messages.
        
        Validates: Requirements 7.4, 7.5
        """
        # Test missing API key
        config1 = RequirementParserConfig(deepseek_api_key="")
        with pytest.raises(ConfigurationError) as exc_info:
            config1.validate_required_config()
        assert "API Key" in str(exc_info.value)
        assert "Fix:" in str(exc_info.value)
        
        # Test missing event bus URL
        config2 = RequirementParserConfig(
            deepseek_api_key="test_key",
            event_bus_url=""
        )
        with pytest.raises(ConfigurationError) as exc_info:
            config2.validate_required_config()
        assert "Event Bus" in str(exc_info.value)
        
        # Test missing blackboard URL
        config3 = RequirementParserConfig(
            deepseek_api_key="test_key",
            blackboard_url=""
        )
        with pytest.raises(ConfigurationError) as exc_info:
            config3.validate_required_config()
        assert "Blackboard" in str(exc_info.value)
