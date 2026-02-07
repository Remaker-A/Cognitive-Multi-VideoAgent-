"""
{AgentName} - 简要说明

职责:
- 职责1
- 职责2
- 职责3

订阅事件:
- EVENT_TYPE_1
- EVENT_TYPE_2

发布事件:
- RESULT_EVENT_TYPE_1
- ERROR_EVENT_TYPE (失败时)
"""

import logging
from typing import List, Dict, Any, Optional
from src.infrastructure.event_bus import EventSubscriber, Event, EventType
from src.contracts import create_event, Money

logger = logging.getLogger(__name__)


class {AgentName}(EventSubscriber):
    """
    {AgentName} 详细说明
    
    这个 Agent 的主要职责是...
    """
    
    def __init__(self, name: str = "{AgentName}"):
        """
        初始化 Agent
        
        Args:
            name: Agent 名称
        """
        super().__init__(name)
        
        # 订阅相关事件
        self.subscribe_to([
            EventType.YOUR_EVENT_TYPE,
            # 添加更多事件类型
        ])
        
        logger.info(f"{self.name} initialized and subscribed to events")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理订阅的事件
        
        Args:
            event: 接收到的事件
        """
        logger.info(
            f"{self.name} received event",
            extra={
                "event_id": event.event_id,
                "event_type": event.event_type,
                "project_id": event.project_id
            }
        )
        
        try:
            # 事件路由
            if event.event_type == EventType.YOUR_EVENT_TYPE:
                await self._handle_your_event(event)
            # 添加更多事件处理
            
        except Exception as e:
            logger.error(
                f"Error handling event {event.event_id}",
                exc_info=True,
                extra={
                    "event_type": event.event_type,
                    "project_id": event.project_id
                }
            )
            # 发布错误事件
            await self._publish_error_event(event, e)
    
    async def _handle_your_event(self, event: Event) -> None:
        """
        处理特定事件的业务逻辑
        
        Args:
            event: 触发事件
        """
        project_id = event.project_id
        
        # 1. 从 Blackboard 读取数据
        logger.debug(f"Reading data from Blackboard for project {project_id}")
        data = await self._read_from_blackboard(project_id, event.payload)
        
        # 2. 执行业务逻辑
        logger.info(f"Processing data for project {project_id}")
        result = await self._process_data(data)
        
        # 3. 写回 Blackboard
        logger.debug(f"Writing results to Blackboard for project {project_id}")
        await self._write_to_blackboard(project_id, result)
        
        # 4. 发布完成事件
        await self._publish_completion_event(event, result)
        
        logger.info(f"Successfully processed event {event.event_id}")
    
    async def _read_from_blackboard(
        self,
        project_id: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        从 Blackboard 读取必要的数据
        
        Args:
            project_id: 项目 ID
            payload: Event payload
            
        Returns:
            读取的数据
        """
        # TODO: 实现 Blackboard RPC 调用
        # from src.contracts import create_blackboard_request
        # request = create_blackboard_request(
        #     request_id=generate_id(),
        #     method="get_project",
        #     params={"project_id": project_id}
        # )
        # response = await blackboard_client.call(request.dict())
        
        # 临时返回示例数据
        return {
            "project_id": project_id,
            "data": payload
        }
    
    async def _write_to_blackboard(
        self,
        project_id: str,
        data: Dict[str, Any]
    ) -> None:
        """
        写入数据到 Blackboard
        
        Args:
            project_id: 项目 ID
            data: 要写入的数据
        """
        # TODO: 实现 Blackboard RPC 调用
        # from src.contracts import create_blackboard_request
        # request = create_blackboard_request(
        #     request_id=generate_id(),
        #     method="update_project",
        #     params={"project_id": project_id, "data": data}
        # )
        # response = await blackboard_client.call(request.dict())
        
        logger.debug(f"Would write to Blackboard: {data}")
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行核心业务逻辑
        
        Args:
            data: 输入数据
            
        Returns:
            处理结果
        """
        # TODO: 实现实际的业务逻辑
        # 这里是 Agent 的核心功能
        
        result = {
            "status": "success",
            "data": data,
            "processed": True
        }
        
        return result
    
    async def _publish_completion_event(
        self,
        trigger_event: Event,
        result: Dict[str, Any]
    ) -> None:
        """
        发布完成事件
        
        Args:
            trigger_event: 触发此操作的事件
            result: 处理结果
        """
        # TODO: 替换为实际的事件类型
        completion_event = create_event(
            event_id=self._generate_event_id(),
            project_id=trigger_event.project_id,
            event_type=EventType.TASK_COMPLETED,  # 替换为实际的事件类型
            actor=self.name,
            payload=result,
            causation_id=trigger_event.event_id,
            cost=Money(amount=0.0, currency="USD"),  # 记录实际成本
            latency_ms=0,  # 记录实际延迟
            metadata={
                "agent": self.name,
                "trigger_event_type": trigger_event.event_type
            }
        )
        
        # TODO: 发布到 Event Bus
        # await self.event_bus.publish(completion_event)
        
        logger.info(
            f"Published completion event {completion_event.event_id}",
            extra={
                "event_type": completion_event.event_type,
                "project_id": completion_event.project_id
            }
        )
    
    async def _publish_error_event(
        self,
        trigger_event: Event,
        error: Exception
    ) -> None:
        """
        发布错误事件
        
        Args:
            trigger_event: 触发此操作的事件
            error: 发生的错误
        """
        error_event = create_event(
            event_id=self._generate_event_id(),
            project_id=trigger_event.project_id,
            event_type=EventType.ERROR_OCCURRED,
            actor=self.name,
            payload={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "trigger_event_id": trigger_event.event_id
            },
            causation_id=trigger_event.event_id,
            metadata={
                "agent": self.name,
                "severity": "error"
            }
        )
        
        # TODO: 发布到 Event Bus
        # await self.event_bus.publish(error_event)
        
        logger.error(
            f"Published error event {error_event.event_id}",
            extra={
                "error_type": type(error).__name__,
                "project_id": error_event.project_id
            }
        )
    
    def _generate_event_id(self) -> str:
        """生成唯一的事件 ID"""
        import uuid
        return f"evt_{uuid.uuid4().hex[:12]}"
