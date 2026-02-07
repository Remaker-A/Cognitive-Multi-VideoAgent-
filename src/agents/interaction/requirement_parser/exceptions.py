"""
RequirementParser Agent 异常定义
"""


class RequirementParserError(Exception):
    """RequirementParser Agent 基础异常"""
    pass


class ConfigurationError(RequirementParserError):
    """配置错误"""
    pass


class InputValidationError(RequirementParserError):
    """输入验证错误"""
    pass


class DeepSeekAPIError(RequirementParserError):
    """DeepSeek API 调用错误"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class APITimeoutError(DeepSeekAPIError):
    """API 超时错误"""
    pass


class APIRateLimitError(DeepSeekAPIError):
    """API 限流错误"""
    pass


class InsufficientBalanceError(DeepSeekAPIError):
    """API 余额不足错误"""
    pass


class NetworkError(RequirementParserError):
    """网络错误"""
    pass


class FileProcessingError(RequirementParserError):
    """文件处理错误"""
    pass


class AnalysisError(RequirementParserError):
    """分析处理错误"""
    pass


class ConfidenceError(RequirementParserError):
    """置信度评估错误"""
    pass


class MaxRetriesExceededError(RequirementParserError):
    """最大重试次数超出错误"""
    def __init__(self, message: str, retry_count: int):
        super().__init__(message)
        self.retry_count = retry_count


class InsufficientInputError(RequirementParserError):
    """输入信息不足错误"""
    def __init__(self, message: str, missing_fields: list = None):
        super().__init__(message)
        self.missing_fields = missing_fields or []


class HumanInterventionRequired(RequirementParserError):
    """需要人工介入错误"""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}