"""
{AgentName} 配置管理
"""

from pydantic_settings import BaseSettings
from typing import Optional


class {AgentName}Config(BaseSettings):
    """
    {AgentName} 配置
    
    从环境变量或 .env 文件读取配置
    """
    
    # Agent 名称
    agent_name: str = "{AgentName}"
    
    # Event Bus 配置
    event_bus_url: str = "redis://localhost:6379"
    
    # Blackboard 配置
    blackboard_url: str = "http://localhost:8000"
    
    # 业务配置示例
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # API 配置（如果需要调用外部服务）
    api_key: Optional[str] = None
    api_endpoint: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_prefix = "AGENT_"  # 环境变量前缀，例如 AGENT_MAX_RETRIES


# 创建全局配置实例
config = {AgentName}Config()
