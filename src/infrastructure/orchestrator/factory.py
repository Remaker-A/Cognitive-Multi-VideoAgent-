"""
Orchestrator 工厂类

提供便捷的 Orchestrator 实例创建方法。
"""

from typing import Optional

from ..blackboard.blackboard import SharedBlackboard
from ..event_bus.event_bus import EventBus
from .orchestrator import Orchestrator
from .config import OrchestratorConfig


class OrchestratorFactory:
    """Orchestrator 工厂"""
    
    @staticmethod
    async def create(
        blackboard: SharedBlackboard,
        event_bus: EventBus,
        config: Optional[OrchestratorConfig] = None
    ) -> Orchestrator:
        """
        创建 Orchestrator 实例
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            config: 配置对象，如果为 None 则从环境变量加载
            
        Returns:
            Orchestrator: Orchestrator 实例
        """
        if config is None:
            config = OrchestratorConfig.from_env()
        
        orchestrator = Orchestrator(blackboard, event_bus, config)
        
        return orchestrator
    
    @staticmethod
    async def create_and_start(
        blackboard: SharedBlackboard,
        event_bus: EventBus,
        config: Optional[OrchestratorConfig] = None
    ) -> Orchestrator:
        """
        创建并启动 Orchestrator
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            config: 配置对象
            
        Returns:
            Orchestrator: 已启动的 Orchestrator 实例
        """
        orchestrator = await OrchestratorFactory.create(blackboard, event_bus, config)
        await orchestrator.start()
        return orchestrator
