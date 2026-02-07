"""
RequirementParser Agent - 需求解析器

LivingAgentPipeline 系统的入口层 Agent，负责解析用户多模态输入并生成 GlobalSpec。
"""

from .config import RequirementParserConfig
from .deepseek_client import DeepSeekClient
from .input_manager import InputManager
from .preprocessor import Preprocessor
from .event_manager import EventManager

# Agent 类将在后续任务中实现
# from .agent import RequirementParserAgent

__all__ = [
    "RequirementParserConfig",
    "DeepSeekClient",
    "InputManager",
    "Preprocessor",
    "EventManager"
]