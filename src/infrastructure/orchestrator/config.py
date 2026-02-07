"""
Orchestrator 配置管理
"""

import os
from dataclasses import dataclass


@dataclass
class OrchestratorConfig:
    """Orchestrator 配置"""
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # 任务队列配置
    task_queue_key: str = "orchestrator:task_queue"
    max_concurrent_tasks: int = 10
    
    # 调度配置
    scheduler_interval_seconds: int = 1
    task_timeout_seconds: int = 300
    
    # 预算配置
    budget_check_enabled: bool = True
    budget_warning_threshold: float = 0.9  # 90%
    
    # 审批配置
    approval_enabled: bool = True
    approval_timeout_minutes: int = 60
    
    @classmethod
    def from_env(cls) -> "OrchestratorConfig":
        """从环境变量加载配置"""
        return cls(
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            task_queue_key=os.getenv("TASK_QUEUE_KEY", "orchestrator:task_queue"),
            max_concurrent_tasks=int(os.getenv("MAX_CONCURRENT_TASKS", "10")),
            scheduler_interval_seconds=int(os.getenv("SCHEDULER_INTERVAL", "1")),
            task_timeout_seconds=int(os.getenv("TASK_TIMEOUT", "300")),
            budget_check_enabled=os.getenv("BUDGET_CHECK_ENABLED", "true").lower() == "true",
            budget_warning_threshold=float(os.getenv("BUDGET_WARNING_THRESHOLD", "0.9")),
            approval_enabled=os.getenv("APPROVAL_ENABLED", "true").lower() == "true",
            approval_timeout_minutes=int(os.getenv("APPROVAL_TIMEOUT", "60")),
        )
