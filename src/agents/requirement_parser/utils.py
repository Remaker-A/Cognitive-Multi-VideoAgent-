"""
RequirementParser Agent 工具函数
"""

import uuid
import hashlib
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "req") -> str:
    """
    生成唯一ID
    
    Args:
        prefix: ID前缀
        
    Returns:
        唯一ID字符串
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_project_id() -> str:
    """生成项目ID"""
    timestamp = datetime.now().strftime("%Y%m%d")
    unique_part = uuid.uuid4().hex[:8]
    return f"PROJ-{timestamp}-{unique_part}"


def calculate_hash(content: str) -> str:
    """
    计算内容的哈希值
    
    Args:
        content: 要计算哈希的内容
        
    Returns:
        SHA256哈希值
    """
    return hashlib.sha256(content.encode()).hexdigest()


def clean_text(text: str) -> str:
    """
    清理文本内容
    
    Args:
        text: 原始文本
        
    Returns:
        清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    
    # 移除首尾空白
    text = text.strip()
    
    return text


def extract_key_phrases(text: str, max_phrases: int = 10) -> List[str]:
    """
    提取文本中的关键短语
    
    Args:
        text: 输入文本
        max_phrases: 最大短语数量
        
    Returns:
        关键短语列表
    """
    # 简单实现：提取长度大于3的词
    words = text.split()
    phrases = [word for word in words if len(word) > 3]
    return phrases[:max_phrases]


def detect_language(text: str) -> str:
    """
    检测文本语言
    
    Args:
        text: 输入文本
        
    Returns:
        语言代码 (zh, en, etc.)
    """
    # 简单实现：检测中文字符
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    if len(chinese_chars) > len(text) * 0.3:
        return "zh"
    return "en"


def estimate_duration_from_text(text: str, default: int = 30) -> int:
    """
    从文本估算视频时长
    
    Args:
        text: 输入文本
        default: 默认时长（秒）
        
    Returns:
        估算的时长（秒）
    """
    # 检查文本中是否明确提到时长
    duration_patterns = [
        r'(\d+)\s*秒',
        r'(\d+)\s*seconds?',
        r'(\d+)\s*分钟',
        r'(\d+)\s*minutes?',
    ]
    
    for pattern in duration_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if '分钟' in pattern or 'minute' in pattern:
                return value * 60
            return value
    
    # 基于文本长度估算
    word_count = len(text.split())
    if word_count < 20:
        return 15
    elif word_count < 50:
        return 30
    elif word_count < 100:
        return 60
    else:
        return 90


def determine_aspect_ratio(
    user_preference: Optional[str] = None,
    visual_hints: Optional[Dict[str, Any]] = None
) -> str:
    """
    确定视频宽高比
    
    Args:
        user_preference: 用户偏好
        visual_hints: 视觉提示信息
        
    Returns:
        宽高比字符串
    """
    if user_preference:
        return user_preference
    
    # 基于视觉提示判断
    if visual_hints:
        if visual_hints.get("vertical_oriented"):
            return "9:16"
        elif visual_hints.get("horizontal_oriented"):
            return "16:9"
    
    # 默认竖屏（适合移动设备）
    return "9:16"


def calculate_resolution(aspect_ratio: str, quality_tier: str = "balanced") -> str:
    """
    根据宽高比和质量档位计算分辨率
    
    Args:
        aspect_ratio: 宽高比
        quality_tier: 质量档位
        
    Returns:
        分辨率字符串
    """
    resolution_map = {
        "9:16": {
            "high": "1080x1920",
            "balanced": "1080x1920",
            "fast": "720x1280"
        },
        "16:9": {
            "high": "1920x1080",
            "balanced": "1920x1080",
            "fast": "1280x720"
        },
        "1:1": {
            "high": "1080x1080",
            "balanced": "1080x1080",
            "fast": "720x720"
        }
    }
    
    return resolution_map.get(aspect_ratio, {}).get(quality_tier, "1080x1920")


def validate_file_format(filename: str, allowed_formats: List[str]) -> bool:
    """
    验证文件格式
    
    Args:
        filename: 文件名
        allowed_formats: 允许的格式列表
        
    Returns:
        是否有效
    """
    if not filename:
        return False
    
    extension = filename.lower().split('.')[-1]
    return extension in [fmt.lower() for fmt in allowed_formats]


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化的文件大小字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def merge_dictionaries(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    合并多个字典
    
    Args:
        *dicts: 要合并的字典
        
    Returns:
        合并后的字典
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    安全获取字典值
    
    Args:
        data: 字典
        key: 键
        default: 默认值
        
    Returns:
        值或默认值
    """
    try:
        return data.get(key, default)
    except (AttributeError, TypeError):
        return default


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def log_processing_step(step_name: str, data: Dict[str, Any]) -> None:
    """
    记录处理步骤
    
    Args:
        step_name: 步骤名称
        data: 相关数据
    """
    logger.info(
        f"Processing step: {step_name}",
        extra={
            "step": step_name,
            "data": data
        }
    )


def measure_confidence(scores: Dict[str, float], weights: Optional[Dict[str, float]] = None) -> float:
    """
    计算加权置信度
    
    Args:
        scores: 各项得分
        weights: 权重（可选）
        
    Returns:
        加权置信度
    """
    if not scores:
        return 0.0
    
    if weights is None:
        # 默认均等权重
        return sum(scores.values()) / len(scores)
    
    # 加权平均
    total_weight = sum(weights.get(k, 1.0) for k in scores.keys())
    weighted_sum = sum(score * weights.get(key, 1.0) for key, score in scores.items())
    
    return weighted_sum / total_weight if total_weight > 0 else 0.0