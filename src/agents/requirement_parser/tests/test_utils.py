"""
RequirementParser Agent 工具函数测试
"""

import pytest
from src.agents.requirement_parser.utils import (
    generate_id,
    generate_project_id,
    clean_text,
    extract_key_phrases,
    detect_language,
    estimate_duration_from_text,
    determine_aspect_ratio,
    calculate_resolution,
    validate_file_format,
    format_file_size,
    measure_confidence
)


class TestUtilityFunctions:
    """工具函数测试套件"""
    
    def test_generate_id_with_default_prefix(self):
        """测试：使用默认前缀生成ID"""
        # Act
        id1 = generate_id()
        id2 = generate_id()
        
        # Assert
        assert id1.startswith("req_")
        assert id2.startswith("req_")
        assert id1 != id2  # 确保唯一性
        assert len(id1) == 16  # req_ + 12字符
    
    def test_generate_id_with_custom_prefix(self):
        """测试：使用自定义前缀生成ID"""
        # Act
        custom_id = generate_id(prefix="test")
        
        # Assert
        assert custom_id.startswith("test_")
        assert len(custom_id) == 17  # test_ + 12字符
    
    def test_generate_project_id_format(self):
        """测试：项目ID格式正确"""
        # Act
        project_id = generate_project_id()
        
        # Assert
        assert project_id.startswith("PROJ-")
        assert len(project_id.split("-")) == 3  # PROJ-YYYYMMDD-XXXXXXXX
    
    def test_clean_text_removes_extra_whitespace(self):
        """测试：清理多余空白字符"""
        # Arrange
        text = "  This   has   extra   spaces  "
        
        # Act
        cleaned = clean_text(text)
        
        # Assert
        assert cleaned == "This has extra spaces"
    
    def test_clean_text_empty_input(self):
        """测试：空输入返回空字符串"""
        # Act
        result = clean_text("")
        
        # Assert
        assert result == ""
    
    def test_extract_key_phrases(self):
        """测试：提取关键短语"""
        # Arrange
        text = "The quick brown fox jumps over the lazy dog"
        
        # Act
        phrases = extract_key_phrases(text, max_phrases=3)
        
        # Assert
        assert len(phrases) <= 3
        assert all(len(phrase) > 3 for phrase in phrases)
    
    def test_detect_language_chinese(self):
        """测试：检测中文"""
        # Arrange
        text = "这是一段中文文本"
        
        # Act
        language = detect_language(text)
        
        # Assert
        assert language == "zh"
    
    def test_detect_language_english(self):
        """测试：检测英文"""
        # Arrange
        text = "This is an English text"
        
        # Act
        language = detect_language(text)
        
        # Assert
        assert language == "en"
    
    def test_estimate_duration_from_explicit_seconds(self):
        """测试：从明确的秒数估算时长"""
        # Arrange
        text = "创建一个45秒的视频"
        
        # Act
        duration = estimate_duration_from_text(text)
        
        # Assert
        assert duration == 45
    
    def test_estimate_duration_from_minutes(self):
        """测试：从分钟数估算时长"""
        # Arrange
        text = "Make a 2 minute video"
        
        # Act
        duration = estimate_duration_from_text(text)
        
        # Assert
        assert duration == 120
    
    def test_estimate_duration_from_text_length(self):
        """测试：基于文本长度估算时长"""
        # Arrange
        short_text = "Short video"
        long_text = " ".join(["word"] * 60)
        
        # Act
        short_duration = estimate_duration_from_text(short_text)
        long_duration = estimate_duration_from_text(long_text)
        
        # Assert
        assert short_duration < long_duration
    
    def test_determine_aspect_ratio_with_preference(self):
        """测试：使用用户偏好确定宽高比"""
        # Act
        ratio = determine_aspect_ratio(user_preference="16:9")
        
        # Assert
        assert ratio == "16:9"
    
    def test_determine_aspect_ratio_default(self):
        """测试：默认宽高比"""
        # Act
        ratio = determine_aspect_ratio()
        
        # Assert
        assert ratio == "9:16"
    
    def test_calculate_resolution_balanced_quality(self):
        """测试：计算平衡质量的分辨率"""
        # Act
        resolution = calculate_resolution("9:16", "balanced")
        
        # Assert
        assert resolution == "1080x1920"
    
    def test_calculate_resolution_high_quality(self):
        """测试：计算高质量的分辨率"""
        # Act
        resolution = calculate_resolution("16:9", "high")
        
        # Assert
        assert resolution == "1920x1080"
    
    def test_calculate_resolution_fast_quality(self):
        """测试：计算快速质量的分辨率"""
        # Act
        resolution = calculate_resolution("9:16", "fast")
        
        # Assert
        assert resolution == "720x1280"
    
    def test_validate_file_format_valid(self):
        """测试：验证有效的文件格式"""
        # Act
        is_valid = validate_file_format("image.jpg", ["jpg", "png"])
        
        # Assert
        assert is_valid is True
    
    def test_validate_file_format_invalid(self):
        """测试：验证无效的文件格式"""
        # Act
        is_valid = validate_file_format("document.pdf", ["jpg", "png"])
        
        # Assert
        assert is_valid is False
    
    def test_validate_file_format_case_insensitive(self):
        """测试：文件格式验证不区分大小写"""
        # Act
        is_valid = validate_file_format("IMAGE.JPG", ["jpg", "png"])
        
        # Assert
        assert is_valid is True
    
    def test_format_file_size_bytes(self):
        """测试：格式化字节大小"""
        # Act
        formatted = format_file_size(512)
        
        # Assert
        assert "512" in formatted
        assert "B" in formatted
    
    def test_format_file_size_kilobytes(self):
        """测试：格式化KB大小"""
        # Act
        formatted = format_file_size(2048)
        
        # Assert
        assert "2.00" in formatted
        assert "KB" in formatted
    
    def test_format_file_size_megabytes(self):
        """测试：格式化MB大小"""
        # Act
        formatted = format_file_size(5 * 1024 * 1024)
        
        # Assert
        assert "5.00" in formatted
        assert "MB" in formatted
    
    def test_measure_confidence_equal_weights(self):
        """测试：计算均等权重的置信度"""
        # Arrange
        scores = {"text": 0.8, "visual": 0.6, "audio": 0.7}
        
        # Act
        confidence = measure_confidence(scores)
        
        # Assert
        assert 0.6 < confidence < 0.8
        assert abs(confidence - 0.7) < 0.01
    
    def test_measure_confidence_custom_weights(self):
        """测试：计算自定义权重的置信度"""
        # Arrange
        scores = {"text": 0.8, "visual": 0.6}
        weights = {"text": 2.0, "visual": 1.0}
        
        # Act
        confidence = measure_confidence(scores, weights)
        
        # Assert
        # (0.8*2 + 0.6*1) / (2+1) = 2.2/3 ≈ 0.733
        assert abs(confidence - 0.733) < 0.01
    
    def test_measure_confidence_empty_scores(self):
        """测试：空分数返回0"""
        # Act
        confidence = measure_confidence({})
        
        # Assert
        assert confidence == 0.0