"""
错误恢复工具模块

提供错误分类、恢复策略选择等辅助功能
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

from .exceptions import (
    RequirementParserError,
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError,
    MaxRetriesExceededError,
    InputValidationError,
    InsufficientInputError,
    FileProcessingError,
    AnalysisError,
    ConfidenceError
)

logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """错误类别枚举"""
    INPUT_VALIDATION = "input_validation"  # 输入验证错误
    API_CALL = "api_call"  # API 调用错误
    RESOURCE_CONSTRAINT = "resource_constraint"  # 资源不足错误
    BUSINESS_LOGIC = "business_logic"  # 业务逻辑错误
    SYSTEM = "system"  # 系统错误
    UNKNOWN = "unknown"  # 未知错误


class RecoveryStrategy(Enum):
    """恢复策略枚举"""
    RETRY = "retry"  # 重试
    FALLBACK = "fallback"  # 降级
    ESCALATE = "escalate"  # 升级到人工
    FAIL_FAST = "fail_fast"  # 快速失败


class ErrorClassifier:
    """
    错误分类器
    
    根据错误类型确定错误类别和推荐的恢复策略
    """
    
    # 错误类型到类别的映射
    ERROR_TYPE_MAPPING: Dict[type, ErrorCategory] = {
        InputValidationError: ErrorCategory.INPUT_VALIDATION,
        InsufficientInputError: ErrorCategory.INPUT_VALIDATION,
        FileProcessingError: ErrorCategory.INPUT_VALIDATION,
        
        DeepSeekAPIError: ErrorCategory.API_CALL,
        APITimeoutError: ErrorCategory.API_CALL,
        APIRateLimitError: ErrorCategory.API_CALL,
        NetworkError: ErrorCategory.API_CALL,
        MaxRetriesExceededError: ErrorCategory.API_CALL,
        
        MemoryError: ErrorCategory.RESOURCE_CONSTRAINT,
        
        AnalysisError: ErrorCategory.BUSINESS_LOGIC,
        ConfidenceError: ErrorCategory.BUSINESS_LOGIC,
    }
    
    # 错误类别到恢复策略的映射
    CATEGORY_STRATEGY_MAPPING: Dict[ErrorCategory, RecoveryStrategy] = {
        ErrorCategory.INPUT_VALIDATION: RecoveryStrategy.FAIL_FAST,
        ErrorCategory.API_CALL: RecoveryStrategy.RETRY,
        ErrorCategory.RESOURCE_CONSTRAINT: RecoveryStrategy.FALLBACK,
        ErrorCategory.BUSINESS_LOGIC: RecoveryStrategy.ESCALATE,
        ErrorCategory.SYSTEM: RecoveryStrategy.ESCALATE,
        ErrorCategory.UNKNOWN: RecoveryStrategy.ESCALATE,
    }
    
    @classmethod
    def classify_error(cls, error: Exception) -> ErrorCategory:
        """
        分类错误
        
        Args:
            error: 异常对象
        
        Returns:
            ErrorCategory: 错误类别
        """
        error_type = type(error)
        
        # 精确匹配
        if error_type in cls.ERROR_TYPE_MAPPING:
            return cls.ERROR_TYPE_MAPPING[error_type]
        
        # 检查继承关系
        for mapped_type, category in cls.ERROR_TYPE_MAPPING.items():
            if isinstance(error, mapped_type):
                return category
        
        # 未知错误
        logger.warning(f"Unknown error type: {error_type.__name__}")
        return ErrorCategory.UNKNOWN
    
    @classmethod
    def recommend_strategy(cls, error: Exception) -> RecoveryStrategy:
        """
        推荐恢复策略
        
        Args:
            error: 异常对象
        
        Returns:
            RecoveryStrategy: 推荐的恢复策略
        """
        category = cls.classify_error(error)
        strategy = cls.CATEGORY_STRATEGY_MAPPING.get(category, RecoveryStrategy.ESCALATE)
        
        logger.debug(
            f"Error recovery recommendation",
            extra={
                "error_type": type(error).__name__,
                "category": category.value,
                "strategy": strategy.value
            }
        )
        
        return strategy
    
    @classmethod
    def is_retryable(cls, error: Exception) -> bool:
        """
        判断错误是否可重试
        
        Args:
            error: 异常对象
        
        Returns:
            bool: 是否可重试
        """
        # API 调用错误通常可重试
        if isinstance(error, (APITimeoutError, APIRateLimitError, NetworkError)):
            return True
        
        # 已经达到最大重试次数的错误不再重试
        if isinstance(error, MaxRetriesExceededError):
            return False
        
        # 输入验证错误不可重试
        if isinstance(error, (InputValidationError, InsufficientInputError)):
            return False
        
        # 其他错误根据类别判断
        category = cls.classify_error(error)
        return category == ErrorCategory.API_CALL


class ErrorRecoveryHelper:
    """
    错误恢复辅助类
    
    提供错误分析、恢复建议等功能
    """
    
    @staticmethod
    def analyze_error_context(
        error: Exception,
        user_input: Optional[Any] = None,
        processing_stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        分析错误上下文
        
        Args:
            error: 异常对象
            user_input: 用户输入（可选）
            processing_stage: 处理阶段（可选）
        
        Returns:
            Dict[str, Any]: 错误上下文信息
        """
        context = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_category": ErrorClassifier.classify_error(error).value,
            "is_retryable": ErrorClassifier.is_retryable(error),
            "recommended_strategy": ErrorClassifier.recommend_strategy(error).value
        }
        
        # 添加处理阶段信息
        if processing_stage:
            context["processing_stage"] = processing_stage
        
        # 添加用户输入摘要
        if user_input:
            context["user_input_summary"] = ErrorRecoveryHelper._summarize_user_input(user_input)
        
        # 添加特定错误的额外信息
        if isinstance(error, DeepSeekAPIError):
            context["api_error"] = {
                "status_code": getattr(error, "status_code", None),
                "response_data": getattr(error, "response_data", None)
            }
        
        if isinstance(error, MaxRetriesExceededError):
            context["retry_count"] = getattr(error, "retry_count", 0)
        
        if isinstance(error, InsufficientInputError):
            context["missing_fields"] = getattr(error, "missing_fields", [])
        
        return context
    
    @staticmethod
    def _summarize_user_input(user_input: Any) -> Dict[str, Any]:
        """
        生成用户输入摘要
        
        Args:
            user_input: 用户输入对象
        
        Returns:
            Dict[str, Any]: 输入摘要
        """
        summary = {}
        
        if hasattr(user_input, "text_description"):
            summary["has_text"] = bool(user_input.text_description)
            summary["text_length"] = len(user_input.text_description) if user_input.text_description else 0
        
        if hasattr(user_input, "reference_images"):
            summary["images_count"] = len(user_input.reference_images)
        
        if hasattr(user_input, "reference_videos"):
            summary["videos_count"] = len(user_input.reference_videos)
        
        if hasattr(user_input, "reference_audio"):
            summary["audio_count"] = len(user_input.reference_audio)
        
        return summary
    
    @staticmethod
    def generate_recovery_suggestions(
        error: Exception,
        context: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        生成恢复建议
        
        Args:
            error: 异常对象
            context: 错误上下文（可选）
        
        Returns:
            List[str]: 恢复建议列表
        """
        suggestions = []
        
        # 基于错误类型的建议
        if isinstance(error, InputValidationError):
            suggestions.extend([
                "检查输入数据的格式和完整性",
                "确保文本描述不为空",
                "验证文件 URL 的有效性"
            ])
        
        elif isinstance(error, APITimeoutError):
            suggestions.extend([
                "检查网络连接",
                "增加超时时间配置",
                "稍后重试"
            ])
        
        elif isinstance(error, APIRateLimitError):
            suggestions.extend([
                "等待一段时间后重试",
                "检查 API 配额使用情况",
                "考虑升级 API 计划"
            ])
        
        elif isinstance(error, NetworkError):
            suggestions.extend([
                "检查网络连接",
                "验证 API 端点配置",
                "检查防火墙设置"
            ])
        
        elif isinstance(error, InsufficientInputError):
            suggestions.extend([
                "提供更详细的文本描述",
                "上传参考图片或视频",
                "补充缺失的必需信息"
            ])
            
            # 添加具体缺失字段的建议
            if hasattr(error, "missing_fields") and error.missing_fields:
                suggestions.append(f"缺失字段: {', '.join(error.missing_fields)}")
        
        elif isinstance(error, MaxRetriesExceededError):
            suggestions.extend([
                "检查 API 服务状态",
                "验证 API 密钥是否有效",
                "考虑使用降级处理策略"
            ])
        
        elif isinstance(error, MemoryError):
            suggestions.extend([
                "减少输入文件的大小",
                "分批处理大文件",
                "增加系统内存"
            ])
        
        else:
            suggestions.extend([
                "查看详细错误日志",
                "联系技术支持",
                "考虑人工处理"
            ])
        
        return suggestions
    
    @staticmethod
    def should_escalate_immediately(error: Exception) -> bool:
        """
        判断是否应该立即升级到人工介入
        
        某些严重错误应该跳过重试和降级，直接升级
        
        Args:
            error: 异常对象
        
        Returns:
            bool: 是否应该立即升级
        """
        # 系统级错误应该立即升级
        if isinstance(error, (SystemError, RuntimeError)):
            return True
        
        # 配置错误应该立即升级
        from .exceptions import ConfigurationError
        if isinstance(error, ConfigurationError):
            return True
        
        # 其他情况不立即升级
        return False
    
    @staticmethod
    def estimate_recovery_probability(
        error: Exception,
        retry_count: int = 0
    ) -> float:
        """
        估算恢复成功的概率
        
        Args:
            error: 异常对象
            retry_count: 已重试次数
        
        Returns:
            float: 恢复成功概率 (0-1)
        """
        # 基础概率
        base_probability = 0.5
        
        # 根据错误类型调整
        if isinstance(error, APITimeoutError):
            base_probability = 0.7  # 超时错误重试成功率较高
        elif isinstance(error, APIRateLimitError):
            base_probability = 0.9  # 限流错误等待后成功率很高
        elif isinstance(error, NetworkError):
            base_probability = 0.6  # 网络错误重试成功率中等
        elif isinstance(error, InputValidationError):
            base_probability = 0.0  # 输入验证错误无法通过重试恢复
        elif isinstance(error, MaxRetriesExceededError):
            base_probability = 0.1  # 已经多次重试失败，成功率很低
        
        # 根据重试次数衰减
        decay_factor = 0.8 ** retry_count
        
        return base_probability * decay_factor


def create_error_report(
    error: Exception,
    user_input: Optional[Any] = None,
    processing_stage: Optional[str] = None,
    retry_count: int = 0
) -> Dict[str, Any]:
    """
    创建完整的错误报告
    
    Args:
        error: 异常对象
        user_input: 用户输入（可选）
        processing_stage: 处理阶段（可选）
        retry_count: 已重试次数
    
    Returns:
        Dict[str, Any]: 错误报告
    """
    helper = ErrorRecoveryHelper()
    
    # 分析错误上下文
    context = helper.analyze_error_context(error, user_input, processing_stage)
    
    # 生成恢复建议
    suggestions = helper.generate_recovery_suggestions(error, context)
    
    # 估算恢复概率
    recovery_probability = helper.estimate_recovery_probability(error, retry_count)
    
    # 判断是否应该立即升级
    should_escalate = helper.should_escalate_immediately(error)
    
    # 构建报告
    report = {
        "error_context": context,
        "recovery_suggestions": suggestions,
        "recovery_probability": recovery_probability,
        "should_escalate_immediately": should_escalate,
        "retry_count": retry_count,
        "timestamp": logging.Formatter().formatTime(logging.LogRecord(
            name="", level=0, pathname="", lineno=0,
            msg="", args=(), exc_info=None
        ))
    }
    
    return report
