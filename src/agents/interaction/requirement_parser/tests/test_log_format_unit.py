"""
日志格式和指标记录完整性单元测试

测试结构化日志格式和指标记录的完整性

Validates: Requirements 8.5
"""

import pytest
import logging
import json
from io import StringIO

from ..logger import setup_logger, StructuredFormatter
from ..metrics_collector import MetricsCollector
from ...models import Money, ConfidenceLevel


class TestStructuredLogFormat:
    """结构化日志格式测试"""
    
    def test_log_format_contains_required_fields(self):
        """
        测试：日志格式包含所有必需字段
        
        Validates: Requirements 8.5
        """
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="requirement_parser",
            level=logging.INFO,
            pathname="agent.py",
            lineno=100,
            msg="Processing user input",
            args=(),
            exc_info=None
        )
        
        # Act
        formatted = formatter.format(record)
        
        # Assert - 验证必需字段存在
        assert "timestamp=" in formatted
        assert "level=INFO" in formatted
        assert "logger=requirement_parser" in formatted
        assert "message=Processing user input" in formatted
        
        # 验证格式使用管道符分隔
        assert " | " in formatted
    
    def test_log_format_with_performance_metrics(self):
        """
        测试：日志格式包含性能指标
        
        Validates: Requirements 8.1, 8.5
        """
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="requirement_parser",
            level=logging.INFO,
            pathname="agent.py",
            lineno=100,
            msg="API call completed",
            args=(),
            exc_info=None
        )
        
        # 添加性能指标
        record.latency_ms = 1500
        record.cost = 0.05
        
        # Act
        formatted = formatter.format(record)
        
        # Assert
        assert "latency_ms=1500" in formatted
        assert "cost=0.05" in formatted
    
    def test_log_format_with_project_context(self):
        """
        测试：日志格式包含项目上下文
        
        Validates: Requirements 8.5
        """
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="requirement_parser",
            level=logging.INFO,
            pathname="agent.py",
            lineno=100,
            msg="Processing started",
            args=(),
            exc_info=None
        )
        
        # 添加项目上下文
        record.project_id = "proj_abc123"
        record.event_id = "evt_xyz789"
        record.step = "preprocessing"
        
        # Act
        formatted = formatter.format(record)
        
        # Assert
        assert "project_id=proj_abc123" in formatted
        assert "event_id=evt_xyz789" in formatted
        assert "step=preprocessing" in formatted
    
    def test_log_format_with_exception(self):
        """
        测试：日志格式包含异常信息
        
        Validates: Requirements 8.4, 8.5
        """
        # Arrange
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="requirement_parser",
            level=logging.ERROR,
            pathname="agent.py",
            lineno=100,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        
        # Act
        formatted = formatter.format(record)
        
        # Assert
        assert "exception=" in formatted
        assert "ValueError" in formatted
        assert "Test error" in formatted
    
    def test_log_format_timestamp_is_iso_format(self):
        """
        测试：时间戳使用 ISO 格式
        
        Validates: Requirements 8.5
        """
        # Arrange
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None
        )
        
        # Act
        formatted = formatter.format(record)
        
        # Assert - 提取时间戳并验证格式
        parts = formatted.split(" | ")
        timestamp_part = [p for p in parts if p.startswith("timestamp=")][0]
        timestamp_value = timestamp_part.split("=")[1]
        
        # ISO 格式应该包含 'T' 和可能的时区信息
        assert "T" in timestamp_value or "-" in timestamp_value
    
    def test_logger_integration_with_metrics(self):
        """
        测试：日志记录器与指标集成
        
        Validates: Requirements 8.1, 8.2, 8.5
        """
        # Arrange
        logger = setup_logger(name="test_metrics_logger")
        
        # 捕获日志输出
        stream = StringIO()
        handler = logging.StreamHandler(stream)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
        
        # Act
        logger.info(
            "API call completed",
            extra={
                "latency_ms": 2000,
                "cost": 0.1,
                "project_id": "test_proj"
            }
        )
        
        # Get output
        output = stream.getvalue()
        
        # Assert
        assert "latency_ms=2000" in output
        assert "cost=0.1" in output
        assert "project_id=test_proj" in output


class TestMetricsRecordingCompleteness:
    """指标记录完整性测试"""
    
    def test_api_call_metric_to_dict_completeness(self):
        """
        测试：API 调用指标转换为字典的完整性
        
        Validates: Requirements 8.1, 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.record_api_call(
            endpoint="https://api.test.com",
            model="test-model",
            latency_ms=1000,
            cost=Money(amount=0.01, currency="USD"),
            tokens_used=100,
            success=True,
            error_type=None
        )
        
        metric_dict = collector.api_call_metrics[0].to_dict()
        
        # Assert - 验证所有必需字段存在
        required_fields = [
            "timestamp",
            "endpoint",
            "model",
            "latency_ms",
            "cost",
            "tokens_used",
            "success",
            "error_type"
        ]
        
        for field in required_fields:
            assert field in metric_dict, f"Missing field: {field}"
        
        # 验证 cost 是字典格式
        assert isinstance(metric_dict["cost"], dict)
        assert "amount" in metric_dict["cost"]
        assert "currency" in metric_dict["cost"]
    
    def test_processing_metric_to_dict_completeness(self):
        """
        测试：处理指标转换为字典的完整性
        
        Validates: Requirements 8.2, 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.record_processing(
            project_id="test_proj",
            processing_stage="full",
            processing_time_ms=2000,
            input_size_bytes=5000,
            text_length=100,
            images_count=2,
            videos_count=1,
            audio_count=0,
            success=True
        )
        
        metric_dict = collector.processing_metrics[0].to_dict()
        
        # Assert - 验证所有必需字段存在
        required_fields = [
            "timestamp",
            "project_id",
            "processing_stage",
            "processing_time_ms",
            "input_size_bytes",
            "text_length",
            "images_count",
            "videos_count",
            "audio_count",
            "success"
        ]
        
        for field in required_fields:
            assert field in metric_dict, f"Missing field: {field}"
    
    def test_confidence_metric_to_dict_completeness(self):
        """
        测试：置信度指标转换为字典的完整性
        
        Validates: Requirements 8.3, 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.record_confidence(
            project_id="test_proj",
            overall_confidence=0.85,
            confidence_level=ConfidenceLevel.HIGH,
            component_scores={
                "text_clarity": 0.9,
                "style_consistency": 0.8,
                "completeness": 0.85
            },
            recommendation="proceed"
        )
        
        metric_dict = collector.confidence_metrics[0].to_dict()
        
        # Assert - 验证所有必需字段存在
        required_fields = [
            "timestamp",
            "project_id",
            "overall_confidence",
            "confidence_level",
            "component_scores",
            "recommendation"
        ]
        
        for field in required_fields:
            assert field in metric_dict, f"Missing field: {field}"
        
        # 验证 component_scores 是字典
        assert isinstance(metric_dict["component_scores"], dict)
        assert len(metric_dict["component_scores"]) > 0
    
    def test_error_metric_to_dict_completeness(self):
        """
        测试：错误指标转换为字典的完整性
        
        Validates: Requirements 8.4, 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # Act
        collector.record_error(
            project_id="test_proj",
            error_type="APITimeoutError",
            error_message="Request timeout after 30s",
            recovery_strategy="retry",
            recovery_success=True
        )
        
        metric_dict = collector.error_metrics[0].to_dict()
        
        # Assert - 验证所有必需字段存在
        required_fields = [
            "timestamp",
            "project_id",
            "error_type",
            "error_message",
            "recovery_strategy",
            "recovery_success"
        ]
        
        for field in required_fields:
            assert field in metric_dict, f"Missing field: {field}"
    
    def test_metrics_snapshot_to_dict_completeness(self):
        """
        测试：指标快照转换为字典的完整性
        
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # 记录一些指标
        collector.record_api_call(
            endpoint="https://api.test.com",
            model="test-model",
            latency_ms=1000,
            cost=Money(amount=0.01, currency="USD"),
            tokens_used=100,
            success=True
        )
        
        collector.record_processing(
            project_id="test_proj",
            processing_stage="full",
            processing_time_ms=2000,
            input_size_bytes=5000,
            text_length=100,
            images_count=1,
            videos_count=0,
            audio_count=0,
            success=True
        )
        
        # Act
        snapshot = collector.get_snapshot()
        snapshot_dict = snapshot.to_dict()
        
        # Assert - 验证所有必需字段存在
        required_fields = [
            "timestamp",
            "total_api_calls",
            "total_processing_requests",
            "total_errors",
            "average_latency_ms",
            "total_cost",
            "confidence_distribution",
            "error_type_distribution",
            "success_rate"
        ]
        
        for field in required_fields:
            assert field in snapshot_dict, f"Missing field: {field}"
    
    def test_metrics_export_structure(self):
        """
        测试：指标导出结构完整性
        
        Validates: Requirements 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # 记录各类指标
        collector.record_api_call(
            endpoint="https://api.test.com",
            model="test-model",
            latency_ms=1000,
            cost=Money(amount=0.01, currency="USD"),
            tokens_used=100,
            success=True
        )
        
        collector.record_processing(
            project_id="test_proj",
            processing_stage="full",
            processing_time_ms=2000,
            input_size_bytes=5000,
            text_length=100,
            images_count=1,
            videos_count=0,
            audio_count=0,
            success=True
        )
        
        collector.record_confidence(
            project_id="test_proj",
            overall_confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            component_scores={"test": 0.8},
            recommendation="proceed"
        )
        
        collector.record_error(
            project_id="test_proj",
            error_type="TestError",
            error_message="Test error",
            recovery_strategy="retry",
            recovery_success=True
        )
        
        # Act
        exported = collector.export_metrics()
        
        # Assert - 验证导出结构
        assert isinstance(exported, dict)
        
        # 验证顶层键
        assert "snapshot" in exported
        assert "api_calls" in exported
        assert "processing" in exported
        assert "confidence" in exported
        assert "errors" in exported
        
        # 验证每个部分都是列表或字典
        assert isinstance(exported["snapshot"], dict)
        assert isinstance(exported["api_calls"], list)
        assert isinstance(exported["processing"], list)
        assert isinstance(exported["confidence"], list)
        assert isinstance(exported["errors"], list)
        
        # 验证数据可以序列化为 JSON（用于日志输出）
        try:
            json_str = json.dumps(exported)
            assert len(json_str) > 0
        except (TypeError, ValueError) as e:
            pytest.fail(f"Metrics export is not JSON serializable: {e}")
    
    def test_metrics_recent_retrieval(self):
        """
        测试：获取最近指标记录
        
        Validates: Requirements 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # 记录多个 API 调用
        for i in range(15):
            collector.record_api_call(
                endpoint="https://api.test.com",
                model="test-model",
                latency_ms=1000 + i,
                cost=Money(amount=0.01, currency="USD"),
                tokens_used=100,
                success=True
            )
        
        # Act
        from ..metrics_collector import MetricType
        recent_10 = collector.get_recent_metrics(MetricType.API_CALL, limit=10)
        
        # Assert
        assert len(recent_10) == 10
        
        # 验证返回的是最近的记录（延迟应该是最大的）
        latencies = [m["latency_ms"] for m in recent_10]
        assert min(latencies) >= 1005  # 应该是后10个记录
    
    def test_metrics_reset_clears_all_data(self):
        """
        测试：重置清除所有指标数据
        
        Validates: Requirements 8.5
        """
        # Arrange
        collector = MetricsCollector()
        
        # 记录各类指标
        collector.record_api_call(
            endpoint="https://api.test.com",
            model="test-model",
            latency_ms=1000,
            cost=Money(amount=0.01, currency="USD"),
            tokens_used=100,
            success=True
        )
        
        collector.record_processing(
            project_id="test_proj",
            processing_stage="full",
            processing_time_ms=2000,
            input_size_bytes=5000,
            text_length=100,
            images_count=1,
            videos_count=0,
            audio_count=0,
            success=True
        )
        
        # Act
        collector.reset()
        
        # Assert - 验证所有数据被清除
        assert len(collector.api_call_metrics) == 0
        assert len(collector.processing_metrics) == 0
        assert len(collector.confidence_metrics) == 0
        assert len(collector.error_metrics) == 0
        assert collector.total_api_calls == 0
        assert collector.total_cost == 0.0
        assert collector.successful_processing == 0
        assert collector.failed_processing == 0
