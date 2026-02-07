"""
RequirementParser Agent 性能指标收集器

负责收集和统计各类性能指标，包括：
- API 调用延迟和成本
- 处理时间和输入大小
- 置信度分布统计
- 错误类型和频率统计

Requirements: 8.1, 8.2, 8.3, 8.4
"""

import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, Counter
from enum import Enum

from .models import Money, ConfidenceLevel


class MetricType(Enum):
    """指标类型枚举"""
    API_CALL = "api_call"
    PROCESSING = "processing"
    CONFIDENCE = "confidence"
    ERROR = "error"
    INPUT_SIZE = "input_size"


@dataclass
class APICallMetric:
    """API 调用指标
    
    Requirements: 8.1
    """
    timestamp: str
    endpoint: str
    model: str
    latency_ms: int
    cost: Money
    tokens_used: int
    success: bool
    error_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "endpoint": self.endpoint,
            "model": self.model,
            "latency_ms": self.latency_ms,
            "cost": self.cost.to_dict(),
            "tokens_used": self.tokens_used,
            "success": self.success,
            "error_type": self.error_type
        }


@dataclass
class ProcessingMetric:
    """处理时间指标
    
    Requirements: 8.2
    """
    timestamp: str
    project_id: str
    processing_stage: str  # "full", "fallback", "template"
    processing_time_ms: int
    input_size_bytes: int
    text_length: int
    images_count: int
    videos_count: int
    audio_count: int
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "project_id": self.project_id,
            "processing_stage": self.processing_stage,
            "processing_time_ms": self.processing_time_ms,
            "input_size_bytes": self.input_size_bytes,
            "text_length": self.text_length,
            "images_count": self.images_count,
            "videos_count": self.videos_count,
            "audio_count": self.audio_count,
            "success": self.success
        }


@dataclass
class ConfidenceMetric:
    """置信度指标
    
    Requirements: 8.3
    """
    timestamp: str
    project_id: str
    overall_confidence: float
    confidence_level: ConfidenceLevel
    component_scores: Dict[str, float]
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "project_id": self.project_id,
            "overall_confidence": self.overall_confidence,
            "confidence_level": self.confidence_level.value,
            "component_scores": self.component_scores,
            "recommendation": self.recommendation
        }


@dataclass
class ErrorMetric:
    """错误指标
    
    Requirements: 8.4
    """
    timestamp: str
    project_id: str
    error_type: str
    error_message: str
    recovery_strategy: Optional[str] = None
    recovery_success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "project_id": self.project_id,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "recovery_strategy": self.recovery_strategy,
            "recovery_success": self.recovery_success
        }


@dataclass
class MetricsSnapshot:
    """指标快照"""
    timestamp: str
    total_api_calls: int
    total_processing_requests: int
    total_errors: int
    average_latency_ms: float
    total_cost: float
    confidence_distribution: Dict[str, int]
    error_type_distribution: Dict[str, int]
    success_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timestamp": self.timestamp,
            "total_api_calls": self.total_api_calls,
            "total_processing_requests": self.total_processing_requests,
            "total_errors": self.total_errors,
            "average_latency_ms": self.average_latency_ms,
            "total_cost": self.total_cost,
            "confidence_distribution": self.confidence_distribution,
            "error_type_distribution": self.error_type_distribution,
            "success_rate": self.success_rate
        }


class MetricsCollector:
    """
    性能指标收集器
    
    负责收集、存储和统计各类性能指标
    
    Requirements: 8.1, 8.2, 8.3, 8.4
    """
    
    def __init__(self):
        """初始化指标收集器"""
        # 存储各类指标
        self.api_call_metrics: List[APICallMetric] = []
        self.processing_metrics: List[ProcessingMetric] = []
        self.confidence_metrics: List[ConfidenceMetric] = []
        self.error_metrics: List[ErrorMetric] = []
        
        # 统计计数器
        self.error_counter: Counter = Counter()
        self.confidence_level_counter: Counter = Counter()
        
        # 累计统计
        self.total_cost: float = 0.0
        self.total_latency_ms: int = 0
        self.total_api_calls: int = 0
        self.successful_processing: int = 0
        self.failed_processing: int = 0
    
    def record_api_call(
        self,
        endpoint: str,
        model: str,
        latency_ms: int,
        cost: Money,
        tokens_used: int,
        success: bool,
        error_type: Optional[str] = None
    ) -> None:
        """
        记录 API 调用指标
        
        Args:
            endpoint: API 端点
            model: 使用的模型
            latency_ms: 延迟（毫秒）
            cost: 成本
            tokens_used: 使用的 token 数
            success: 是否成功
            error_type: 错误类型（如果失败）
        
        Requirements: 8.1
        """
        metric = APICallMetric(
            timestamp=datetime.now().isoformat(),
            endpoint=endpoint,
            model=model,
            latency_ms=latency_ms,
            cost=cost,
            tokens_used=tokens_used,
            success=success,
            error_type=error_type
        )
        
        self.api_call_metrics.append(metric)
        
        # 更新累计统计
        self.total_api_calls += 1
        self.total_latency_ms += latency_ms
        self.total_cost += cost.amount
        
        if not success and error_type:
            self.error_counter[error_type] += 1
    
    def record_processing(
        self,
        project_id: str,
        processing_stage: str,
        processing_time_ms: int,
        input_size_bytes: int,
        text_length: int,
        images_count: int,
        videos_count: int,
        audio_count: int,
        success: bool
    ) -> None:
        """
        记录处理时间和输入大小指标
        
        Args:
            project_id: 项目 ID
            processing_stage: 处理阶段
            processing_time_ms: 处理时间（毫秒）
            input_size_bytes: 输入大小（字节）
            text_length: 文本长度
            images_count: 图片数量
            videos_count: 视频数量
            audio_count: 音频数量
            success: 是否成功
        
        Requirements: 8.2
        """
        metric = ProcessingMetric(
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            processing_stage=processing_stage,
            processing_time_ms=processing_time_ms,
            input_size_bytes=input_size_bytes,
            text_length=text_length,
            images_count=images_count,
            videos_count=videos_count,
            audio_count=audio_count,
            success=success
        )
        
        self.processing_metrics.append(metric)
        
        # 更新成功/失败计数
        if success:
            self.successful_processing += 1
        else:
            self.failed_processing += 1
    
    def record_confidence(
        self,
        project_id: str,
        overall_confidence: float,
        confidence_level: ConfidenceLevel,
        component_scores: Dict[str, float],
        recommendation: str
    ) -> None:
        """
        记录置信度指标
        
        Args:
            project_id: 项目 ID
            overall_confidence: 总体置信度
            confidence_level: 置信度级别
            component_scores: 各组件置信度分数
            recommendation: 推荐行动
        
        Requirements: 8.3
        """
        metric = ConfidenceMetric(
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            overall_confidence=overall_confidence,
            confidence_level=confidence_level,
            component_scores=component_scores,
            recommendation=recommendation
        )
        
        self.confidence_metrics.append(metric)
        
        # 更新置信度分布统计
        self.confidence_level_counter[confidence_level.value] += 1
    
    def record_error(
        self,
        project_id: str,
        error_type: str,
        error_message: str,
        recovery_strategy: Optional[str] = None,
        recovery_success: bool = False
    ) -> None:
        """
        记录错误指标
        
        Args:
            project_id: 项目 ID
            error_type: 错误类型
            error_message: 错误消息
            recovery_strategy: 恢复策略
            recovery_success: 恢复是否成功
        
        Requirements: 8.4
        """
        metric = ErrorMetric(
            timestamp=datetime.now().isoformat(),
            project_id=project_id,
            error_type=error_type,
            error_message=error_message,
            recovery_strategy=recovery_strategy,
            recovery_success=recovery_success
        )
        
        self.error_metrics.append(metric)
        
        # 更新错误类型统计
        self.error_counter[error_type] += 1
    
    def get_snapshot(self) -> MetricsSnapshot:
        """
        获取当前指标快照
        
        Returns:
            MetricsSnapshot: 指标快照
        """
        total_requests = self.successful_processing + self.failed_processing
        success_rate = (
            self.successful_processing / total_requests
            if total_requests > 0
            else 0.0
        )
        
        average_latency = (
            self.total_latency_ms / self.total_api_calls
            if self.total_api_calls > 0
            else 0.0
        )
        
        return MetricsSnapshot(
            timestamp=datetime.now().isoformat(),
            total_api_calls=self.total_api_calls,
            total_processing_requests=total_requests,
            total_errors=len(self.error_metrics),
            average_latency_ms=average_latency,
            total_cost=self.total_cost,
            confidence_distribution=dict(self.confidence_level_counter),
            error_type_distribution=dict(self.error_counter),
            success_rate=success_rate
        )
    
    def get_confidence_distribution(self) -> Dict[str, int]:
        """
        获取置信度分布统计
        
        Returns:
            Dict[str, int]: 置信度级别分布
        
        Requirements: 8.3
        """
        return dict(self.confidence_level_counter)
    
    def get_error_distribution(self) -> Dict[str, int]:
        """
        获取错误类型分布统计
        
        Returns:
            Dict[str, int]: 错误类型分布
        
        Requirements: 8.4
        """
        return dict(self.error_counter)
    
    def get_average_latency(self) -> float:
        """
        获取平均 API 调用延迟
        
        Returns:
            float: 平均延迟（毫秒）
        
        Requirements: 8.1
        """
        if self.total_api_calls == 0:
            return 0.0
        return self.total_latency_ms / self.total_api_calls
    
    def get_total_cost(self) -> float:
        """
        获取总成本
        
        Returns:
            float: 总成本
        
        Requirements: 8.1
        """
        return self.total_cost
    
    def get_success_rate(self) -> float:
        """
        获取处理成功率
        
        Returns:
            float: 成功率（0-1）
        
        Requirements: 8.2
        """
        total = self.successful_processing + self.failed_processing
        if total == 0:
            return 0.0
        return self.successful_processing / total
    
    def get_recent_metrics(
        self,
        metric_type: MetricType,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取最近的指标记录
        
        Args:
            metric_type: 指标类型
            limit: 返回数量限制
        
        Returns:
            List[Dict[str, Any]]: 指标记录列表
        """
        if metric_type == MetricType.API_CALL:
            metrics = self.api_call_metrics[-limit:]
            return [m.to_dict() for m in metrics]
        elif metric_type == MetricType.PROCESSING:
            metrics = self.processing_metrics[-limit:]
            return [m.to_dict() for m in metrics]
        elif metric_type == MetricType.CONFIDENCE:
            metrics = self.confidence_metrics[-limit:]
            return [m.to_dict() for m in metrics]
        elif metric_type == MetricType.ERROR:
            metrics = self.error_metrics[-limit:]
            return [m.to_dict() for m in metrics]
        else:
            return []
    
    def reset(self) -> None:
        """重置所有指标"""
        self.api_call_metrics.clear()
        self.processing_metrics.clear()
        self.confidence_metrics.clear()
        self.error_metrics.clear()
        self.error_counter.clear()
        self.confidence_level_counter.clear()
        self.total_cost = 0.0
        self.total_latency_ms = 0
        self.total_api_calls = 0
        self.successful_processing = 0
        self.failed_processing = 0
    
    def export_metrics(self) -> Dict[str, Any]:
        """
        导出所有指标数据
        
        Returns:
            Dict[str, Any]: 所有指标数据
        """
        return {
            "snapshot": self.get_snapshot().to_dict(),
            "api_calls": [m.to_dict() for m in self.api_call_metrics],
            "processing": [m.to_dict() for m in self.processing_metrics],
            "confidence": [m.to_dict() for m in self.confidence_metrics],
            "errors": [m.to_dict() for m in self.error_metrics]
        }


# 创建全局指标收集器实例
global_metrics_collector = MetricsCollector()
