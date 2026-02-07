"""
鐩戞帶鍜屾棩蹇楀姛鑳藉睘鎬ф祴璇?

Property 8: Comprehensive Monitoring and Logging
For any operation performed by the RequirementParser, relevant metrics (latency, cost, 
input size, processing time, confidence scores, error types) should be recorded in structured logs

Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import assume
import asyncio

from ..metrics_collector import (
    MetricsCollector,
    APICallMetric,
    ProcessingMetric,
    ConfidenceMetric,
    ErrorMetric,
    MetricType
)
from ...models import Money, ConfidenceLevel


# 绛栫暐瀹氫箟
@st.composite
def api_call_data(draw):
    """鐢熸垚 API 璋冪敤鏁版嵁"""
    return {
        "endpoint": draw(st.sampled_from([
            "https://api.deepseek.com/v1/chat/completions",
            "https://api.deepseek.com/v1/completions"
        ])),
        "model": draw(st.sampled_from(["DeepSeek-V3.2", "DeepSeek-V3", "gpt-4"])),
        "latency_ms": draw(st.integers(min_value=100, max_value=30000)),
        "cost_amount": draw(st.floats(min_value=0.0001, max_value=1.0)),
        "tokens_used": draw(st.integers(min_value=10, max_value=10000)),
        "success": draw(st.booleans()),
        "error_type": draw(st.one_of(
            st.none(),
            st.sampled_from(["APITimeoutError", "APIRateLimitError", "NetworkError"])
        ))
    }


@st.composite
def processing_data(draw):
    """鐢熸垚澶勭悊鏁版嵁"""
    return {
        "project_id": draw(st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        "processing_stage": draw(st.sampled_from(["full", "fallback", "template"])),
        "processing_time_ms": draw(st.integers(min_value=100, max_value=60000)),
        "input_size_bytes": draw(st.integers(min_value=0, max_value=10000000)),
        "text_length": draw(st.integers(min_value=0, max_value=10000)),
        "images_count": draw(st.integers(min_value=0, max_value=10)),
        "videos_count": draw(st.integers(min_value=0, max_value=5)),
        "audio_count": draw(st.integers(min_value=0, max_value=5)),
        "success": draw(st.booleans())
    }


@st.composite
def confidence_data(draw):
    """鐢熸垚缃俊搴︽暟鎹?""
    overall_confidence = draw(st.floats(min_value=0.0, max_value=1.0))
    
    # 鏍规嵁缃俊搴︾‘瀹氱骇鍒?
    if overall_confidence >= 0.8:
        level = ConfidenceLevel.HIGH
    elif overall_confidence >= 0.6:
        level = ConfidenceLevel.MEDIUM
    else:
        level = ConfidenceLevel.LOW
    
    return {
        "project_id": draw(st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        "overall_confidence": overall_confidence,
        "confidence_level": level,
        "component_scores": {
            "text_clarity": draw(st.floats(min_value=0.0, max_value=1.0)),
            "style_consistency": draw(st.floats(min_value=0.0, max_value=1.0)),
            "completeness": draw(st.floats(min_value=0.0, max_value=1.0))
        },
        "recommendation": draw(st.sampled_from(["proceed", "clarify", "human_review"]))
    }


@st.composite
def error_data(draw):
    """鐢熸垚閿欒鏁版嵁"""
    return {
        "project_id": draw(st.text(min_size=10, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
        "error_type": draw(st.sampled_from([
            "DeepSeekAPIError",
            "APITimeoutError",
            "APIRateLimitError",
            "NetworkError",
            "InputValidationError"
        ])),
        "error_message": draw(st.text(min_size=10, max_size=200)),
        "recovery_strategy": draw(st.one_of(
            st.none(),
            st.sampled_from(["retry", "fallback", "template"])
        )),
        "recovery_success": draw(st.booleans())
    }


class TestMonitoringProperties:
    """鐩戞帶鍔熻兘灞炴€ф祴璇?""
    
    @given(api_call_data())
    @settings(max_examples=20, deadline=None)
    def test_api_call_metrics_recording(self, api_data):
        """
        Property 8.1: API 璋冪敤鎸囨爣璁板綍
        
        For any API call, the metrics collector should record latency, cost, 
        tokens used, and success status
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.1
        """
        collector = MetricsCollector()
        
        # 璁板綍 API 璋冪敤
        collector.record_api_call(
            endpoint=api_data["endpoint"],
            model=api_data["model"],
            latency_ms=api_data["latency_ms"],
            cost=Money(amount=api_data["cost_amount"], currency="USD"),
            tokens_used=api_data["tokens_used"],
            success=api_data["success"],
            error_type=api_data["error_type"]
        )
        
        # 楠岃瘉鎸囨爣琚褰?
        assert len(collector.api_call_metrics) == 1
        
        metric = collector.api_call_metrics[0]
        assert metric.endpoint == api_data["endpoint"]
        assert metric.model == api_data["model"]
        assert metric.latency_ms == api_data["latency_ms"]
        assert metric.cost.amount == api_data["cost_amount"]
        assert metric.tokens_used == api_data["tokens_used"]
        assert metric.success == api_data["success"]
        assert metric.error_type == api_data["error_type"]
        
        # 楠岃瘉绱缁熻鏇存柊
        assert collector.total_api_calls == 1
        assert collector.total_latency_ms == api_data["latency_ms"]
        assert collector.total_cost == api_data["cost_amount"]
    
    @given(processing_data())
    @settings(max_examples=20, deadline=None)
    def test_processing_metrics_recording(self, proc_data):
        """
        Property 8.2: 澶勭悊鏃堕棿鍜岃緭鍏ュぇ灏忚褰?
        
        For any processing operation, the metrics collector should record 
        processing time, input size, and all input counts
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.2
        """
        collector = MetricsCollector()
        
        # 璁板綍澶勭悊鎸囨爣
        collector.record_processing(
            project_id=proc_data["project_id"],
            processing_stage=proc_data["processing_stage"],
            processing_time_ms=proc_data["processing_time_ms"],
            input_size_bytes=proc_data["input_size_bytes"],
            text_length=proc_data["text_length"],
            images_count=proc_data["images_count"],
            videos_count=proc_data["videos_count"],
            audio_count=proc_data["audio_count"],
            success=proc_data["success"]
        )
        
        # 楠岃瘉鎸囨爣琚褰?
        assert len(collector.processing_metrics) == 1
        
        metric = collector.processing_metrics[0]
        assert metric.project_id == proc_data["project_id"]
        assert metric.processing_stage == proc_data["processing_stage"]
        assert metric.processing_time_ms == proc_data["processing_time_ms"]
        assert metric.input_size_bytes == proc_data["input_size_bytes"]
        assert metric.text_length == proc_data["text_length"]
        assert metric.images_count == proc_data["images_count"]
        assert metric.videos_count == proc_data["videos_count"]
        assert metric.audio_count == proc_data["audio_count"]
        assert metric.success == proc_data["success"]
        
        # 楠岃瘉鎴愬姛/澶辫触璁℃暟
        if proc_data["success"]:
            assert collector.successful_processing == 1
            assert collector.failed_processing == 0
        else:
            assert collector.successful_processing == 0
            assert collector.failed_processing == 1
    
    @given(confidence_data())
    @settings(max_examples=20, deadline=None)
    def test_confidence_metrics_recording(self, conf_data):
        """
        Property 8.3: 缃俊搴﹀垎甯冪粺璁?
        
        For any confidence evaluation, the metrics collector should record 
        overall confidence, level, component scores, and recommendation
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.3
        """
        collector = MetricsCollector()
        
        # 璁板綍缃俊搴︽寚鏍?
        collector.record_confidence(
            project_id=conf_data["project_id"],
            overall_confidence=conf_data["overall_confidence"],
            confidence_level=conf_data["confidence_level"],
            component_scores=conf_data["component_scores"],
            recommendation=conf_data["recommendation"]
        )
        
        # 楠岃瘉鎸囨爣琚褰?
        assert len(collector.confidence_metrics) == 1
        
        metric = collector.confidence_metrics[0]
        assert metric.project_id == conf_data["project_id"]
        assert metric.overall_confidence == conf_data["overall_confidence"]
        assert metric.confidence_level == conf_data["confidence_level"]
        assert metric.component_scores == conf_data["component_scores"]
        assert metric.recommendation == conf_data["recommendation"]
        
        # 楠岃瘉缃俊搴﹀垎甯冪粺璁?
        distribution = collector.get_confidence_distribution()
        assert conf_data["confidence_level"].value in distribution
        assert distribution[conf_data["confidence_level"].value] == 1
    
    @given(error_data())
    @settings(max_examples=20, deadline=None)
    def test_error_metrics_recording(self, err_data):
        """
        Property 8.4: 閿欒绫诲瀷鍜岄鐜囩粺璁?
        
        For any error occurrence, the metrics collector should record 
        error type, message, recovery strategy, and success
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.4
        """
        collector = MetricsCollector()
        
        # 璁板綍閿欒鎸囨爣
        collector.record_error(
            project_id=err_data["project_id"],
            error_type=err_data["error_type"],
            error_message=err_data["error_message"],
            recovery_strategy=err_data["recovery_strategy"],
            recovery_success=err_data["recovery_success"]
        )
        
        # 楠岃瘉鎸囨爣琚褰?
        assert len(collector.error_metrics) == 1
        
        metric = collector.error_metrics[0]
        assert metric.project_id == err_data["project_id"]
        assert metric.error_type == err_data["error_type"]
        assert metric.error_message == err_data["error_message"]
        assert metric.recovery_strategy == err_data["recovery_strategy"]
        assert metric.recovery_success == err_data["recovery_success"]
        
        # 楠岃瘉閿欒绫诲瀷缁熻
        distribution = collector.get_error_distribution()
        assert err_data["error_type"] in distribution
        assert distribution[err_data["error_type"]] == 1
    
    @given(
        st.lists(api_call_data(), min_size=1, max_size=20),
        st.lists(processing_data(), min_size=1, max_size=20)
    )
    @settings(max_examples=10, deadline=None)
    def test_metrics_snapshot_completeness(self, api_calls, processings):
        """
        Property 8.5: 鎸囨爣蹇収瀹屾暣鎬?
        
        For any set of recorded metrics, the snapshot should contain 
        complete aggregated statistics
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.1, 8.2, 8.3, 8.4, 8.5
        """
        collector = MetricsCollector()
        
        # 璁板綍澶氫釜 API 璋冪敤
        for api_data in api_calls:
            collector.record_api_call(
                endpoint=api_data["endpoint"],
                model=api_data["model"],
                latency_ms=api_data["latency_ms"],
                cost=Money(amount=api_data["cost_amount"], currency="USD"),
                tokens_used=api_data["tokens_used"],
                success=api_data["success"],
                error_type=api_data["error_type"]
            )
        
        # 璁板綍澶氫釜澶勭悊鎿嶄綔
        for proc_data in processings:
            collector.record_processing(
                project_id=proc_data["project_id"],
                processing_stage=proc_data["processing_stage"],
                processing_time_ms=proc_data["processing_time_ms"],
                input_size_bytes=proc_data["input_size_bytes"],
                text_length=proc_data["text_length"],
                images_count=proc_data["images_count"],
                videos_count=proc_data["videos_count"],
                audio_count=proc_data["audio_count"],
                success=proc_data["success"]
            )
        
        # 鑾峰彇蹇収
        snapshot = collector.get_snapshot()
        
        # 楠岃瘉蹇収鍖呭惈鎵€鏈夊繀闇€瀛楁
        assert snapshot.total_api_calls == len(api_calls)
        assert snapshot.total_processing_requests == len(processings)
        assert snapshot.average_latency_ms >= 0
        assert snapshot.total_cost >= 0
        assert isinstance(snapshot.confidence_distribution, dict)
        assert isinstance(snapshot.error_type_distribution, dict)
        assert 0.0 <= snapshot.success_rate <= 1.0
        
        # 楠岃瘉鎴愬姛鐜囪绠楁纭?
        successful = sum(1 for p in processings if p["success"])
        expected_rate = successful / len(processings) if processings else 0.0
        assert abs(snapshot.success_rate - expected_rate) < 0.01
    
    @given(st.lists(api_call_data(), min_size=2, max_size=10))
    @settings(max_examples=10, deadline=None)
    def test_average_latency_calculation(self, api_calls):
        """
        Property: 骞冲潎寤惰繜璁＄畻姝ｇ‘鎬?
        
        For any set of API calls, the average latency should be 
        correctly calculated
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.1
        """
        collector = MetricsCollector()
        
        total_latency = 0
        for api_data in api_calls:
            collector.record_api_call(
                endpoint=api_data["endpoint"],
                model=api_data["model"],
                latency_ms=api_data["latency_ms"],
                cost=Money(amount=api_data["cost_amount"], currency="USD"),
                tokens_used=api_data["tokens_used"],
                success=api_data["success"],
                error_type=api_data["error_type"]
            )
            total_latency += api_data["latency_ms"]
        
        expected_avg = total_latency / len(api_calls)
        actual_avg = collector.get_average_latency()
        
        # 楠岃瘉骞冲潎寤惰繜璁＄畻姝ｇ‘锛堝厑璁告诞鐐硅宸級
        assert abs(actual_avg - expected_avg) < 0.01
    
    @given(st.lists(api_call_data(), min_size=1, max_size=10))
    @settings(max_examples=10, deadline=None)
    def test_total_cost_accumulation(self, api_calls):
        """
        Property: 鎬绘垚鏈疮璁℃纭€?
        
        For any set of API calls, the total cost should be 
        correctly accumulated
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.1
        """
        collector = MetricsCollector()
        
        expected_total = 0.0
        for api_data in api_calls:
            collector.record_api_call(
                endpoint=api_data["endpoint"],
                model=api_data["model"],
                latency_ms=api_data["latency_ms"],
                cost=Money(amount=api_data["cost_amount"], currency="USD"),
                tokens_used=api_data["tokens_used"],
                success=api_data["success"],
                error_type=api_data["error_type"]
            )
            expected_total += api_data["cost_amount"]
        
        actual_total = collector.get_total_cost()
        
        # 楠岃瘉鎬绘垚鏈疮璁℃纭紙鍏佽娴偣璇樊锛?
        assert abs(actual_total - expected_total) < 0.0001
    
    @given(
        st.lists(confidence_data(), min_size=5, max_size=20)
    )
    @settings(max_examples=10, deadline=None)
    def test_confidence_distribution_accuracy(self, confidence_list):
        """
        Property: 缃俊搴﹀垎甯冪粺璁″噯纭€?
        
        For any set of confidence evaluations, the distribution 
        should accurately reflect the confidence levels
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.3
        """
        collector = MetricsCollector()
        
        # 缁熻棰勬湡鍒嗗竷
        expected_distribution = {"high": 0, "medium": 0, "low": 0}
        
        for conf_data in confidence_list:
            collector.record_confidence(
                project_id=conf_data["project_id"],
                overall_confidence=conf_data["overall_confidence"],
                confidence_level=conf_data["confidence_level"],
                component_scores=conf_data["component_scores"],
                recommendation=conf_data["recommendation"]
            )
            expected_distribution[conf_data["confidence_level"].value] += 1
        
        actual_distribution = collector.get_confidence_distribution()
        
        # 楠岃瘉鍒嗗竷缁熻鍑嗙‘
        for level, count in expected_distribution.items():
            if count > 0:
                assert actual_distribution.get(level, 0) == count
    
    @given(
        st.lists(error_data(), min_size=5, max_size=20)
    )
    @settings(max_examples=10, deadline=None)
    def test_error_distribution_accuracy(self, error_list):
        """
        Property: 閿欒鍒嗗竷缁熻鍑嗙‘鎬?
        
        For any set of errors, the distribution should accurately 
        reflect the error types and frequencies
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.4
        """
        collector = MetricsCollector()
        
        # 缁熻棰勬湡鍒嗗竷
        from collections import Counter
        expected_distribution = Counter()
        
        for err_data in error_list:
            collector.record_error(
                project_id=err_data["project_id"],
                error_type=err_data["error_type"],
                error_message=err_data["error_message"],
                recovery_strategy=err_data["recovery_strategy"],
                recovery_success=err_data["recovery_success"]
            )
            expected_distribution[err_data["error_type"]] += 1
        
        actual_distribution = collector.get_error_distribution()
        
        # 楠岃瘉鍒嗗竷缁熻鍑嗙‘
        for error_type, count in expected_distribution.items():
            assert actual_distribution.get(error_type, 0) == count
    
    def test_metrics_export_completeness(self):
        """
        Property: 鎸囨爣瀵煎嚭瀹屾暣鎬?
        
        For any metrics collector state, the export should contain 
        all metric types and snapshot data
        
        Feature: requirement-parser-agent, Property 8: Comprehensive Monitoring and Logging
        Validates: Requirements 8.5
        """
        collector = MetricsCollector()
        
        # 璁板綍鍚勭被鎸囨爣
        collector.record_api_call(
            endpoint="https://api.test.com",
            model="test-model",
            latency_ms=1000,
            cost=Money(amount=0.01, currency="USD"),
            tokens_used=100,
            success=True
        )
        
        collector.record_processing(
            project_id="test-project",
            processing_stage="full",
            processing_time_ms=2000,
            input_size_bytes=1000,
            text_length=100,
            images_count=1,
            videos_count=0,
            audio_count=0,
            success=True
        )
        
        collector.record_confidence(
            project_id="test-project",
            overall_confidence=0.8,
            confidence_level=ConfidenceLevel.HIGH,
            component_scores={"test": 0.8},
            recommendation="proceed"
        )
        
        collector.record_error(
            project_id="test-project",
            error_type="TestError",
            error_message="Test error message",
            recovery_strategy="retry",
            recovery_success=True
        )
        
        # 瀵煎嚭鎸囨爣
        exported = collector.export_metrics()
        
        # 楠岃瘉瀵煎嚭鍖呭惈鎵€鏈夊繀闇€閮ㄥ垎
        assert "snapshot" in exported
        assert "api_calls" in exported
        assert "processing" in exported
        assert "confidence" in exported
        assert "errors" in exported
        
        # 楠岃瘉姣忎釜閮ㄥ垎閮芥湁鏁版嵁
        assert len(exported["api_calls"]) == 1
        assert len(exported["processing"]) == 1
        assert len(exported["confidence"]) == 1
        assert len(exported["errors"]) == 1
        
        # 楠岃瘉蹇収鏁版嵁瀹屾暣
        snapshot = exported["snapshot"]
        assert "total_api_calls" in snapshot
        assert "total_processing_requests" in snapshot
        assert "average_latency_ms" in snapshot
        assert "total_cost" in snapshot
        assert "success_rate" in snapshot
