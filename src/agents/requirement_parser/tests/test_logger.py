"""
RequirementParser Agent 日志测试
"""

import pytest
import logging
from src.agents.requirement_parser.logger import setup_logger, StructuredFormatter


class TestLogger:
    """日志功能测试套件"""
    
    def test_setup_logger_creates_logger(self):
        """测试：创建日志记录器"""
        # Act
        logger = setup_logger(name="test_logger")
        
        # Assert
        assert logger is not None
        assert logger.name == "test_logger"
        assert logger.level == logging.INFO
    
    def test_setup_logger_with_custom_level(self):
        """测试：使用自定义日志级别"""
        # Act
        logger = setup_logger(name="test_debug_logger", level=logging.DEBUG)
        
        # Assert
        assert logger.level == logging.DEBUG
    
    def test_setup_logger_has_handlers(self):
        """测试：日志记录器有处理器"""
        # Act
        logger = setup_logger(name="test_handler_logger")
        
        # Assert
        assert len(logger.handlers) > 0
    
    def test_structured_formatter_basic_format(self):
        """测试：结构化格式化器基本格式"""
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Act
        formatted = formatter.format(record)
        
        # Assert
        assert "timestamp=" in formatted
        assert "level=INFO" in formatted
        assert "logger=test" in formatted
        assert "message=Test message" in formatted
    
    def test_structured_formatter_with_extra_fields(self):
        """测试：结构化格式化器包含额外字段"""
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.event_id = "evt_123"
        record.project_id = "proj_456"
        record.cost = 0.05
        
        # Act
        formatted = formatter.format(record)
        
        # Assert
        assert "event_id=evt_123" in formatted
        assert "project_id=proj_456" in formatted
        assert "cost=0.05" in formatted
    
    def test_logger_no_duplicate_handlers(self):
        """测试：不会重复添加处理器"""
        # Act
        logger1 = setup_logger(name="test_dup_logger")
        handler_count1 = len(logger1.handlers)
        
        logger2 = setup_logger(name="test_dup_logger")
        handler_count2 = len(logger2.handlers)
        
        # Assert
        assert handler_count1 == handler_count2
        assert logger1 is logger2  # 应该返回同一个实例