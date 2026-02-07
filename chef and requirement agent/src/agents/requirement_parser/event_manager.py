"""
RequirementParser Agent 事件管理器

负责事件发布和Blackboard数据写入
"""

import uuid
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .models import (
    Event,
    EventType,
    Money,
    GlobalSpec,
    BlackboardWriteRequest,
    ConfidenceReport
)
from .logger import default_logger


class EventManager:
    """
    事件管理器
    
    职责:
    - 发布 PROJECT_CREATED 事件
    - 发布 ERROR_OCCURRED 事件
    - 管理事件元数据
    - 写入数据到 Blackboard
    """
    
    def __init__(
        self,
        agent_name: str = "RequirementParserAgent",
        logger: Optional[logging.Logger] = None
    ):
        """
        初始化事件管理器
        
        Args:
            agent_name: Agent 名称
            logger: 日志记录器（可选）
        """
        self.agent_name = agent_name
        self.logger = logger or default_logger
        self._published_events: list[Event] = []
    
    def generate_event_id(self) -> str:
        """
        生成唯一的事件 ID
        
        Returns:
            事件 ID，格式为 evt_{12位十六进制}
        """
        return f"evt_{uuid.uuid4().hex[:12]}"
    
    def generate_project_id(self) -> str:
        """
        生成唯一的项目 ID
        
        Returns:
            项目 ID，格式为 proj_{12位十六进制}
        """
        return f"proj_{uuid.uuid4().hex[:12]}"
    
    async def publish_project_created(
        self,
        project_id: str,
        global_spec: GlobalSpec,
        confidence_report: ConfidenceReport,
        causation_id: Optional[str] = None,
        cost: Optional[Money] = None,
        latency_ms: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        发布 PROJECT_CREATED 事件
        
        Args:
            project_id: 项目 ID
            global_spec: 生成的 GlobalSpec
            confidence_report: 置信度报告
            causation_id: 因果关系 ID（触发此事件的事件 ID）
            cost: 处理成本
            latency_ms: 处理延迟（毫秒）
            metadata: 额外的元数据
            
        Returns:
            发布的事件对象
        """
        event_id = self.generate_event_id()
        
        # 构建事件 payload
        payload = {
            "global_spec": global_spec.to_dict(),
            "confidence_report": {
                "overall_confidence": confidence_report.overall_confidence,
                "confidence_level": confidence_report.confidence_level.value,
                "component_scores": confidence_report.component_scores,
                "low_confidence_areas": confidence_report.low_confidence_areas,
                "recommendation": confidence_report.recommendation
            }
        }
        
        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.PROJECT_CREATED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms,
            metadata=metadata or {}
        )
        
        # 记录事件
        self._published_events.append(event)
        
        # 记录日志
        self.logger.info(
            f"Published PROJECT_CREATED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "confidence": confidence_report.overall_confidence,
                "cost": cost.amount if cost else None,
                "latency_ms": latency_ms
            }
        )
        
        return event
    
    async def publish_error_occurred(
        self,
        project_id: str,
        error: Exception,
        error_context: Optional[Dict[str, Any]] = None,
        causation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        发布 ERROR_OCCURRED 事件
        
        Args:
            project_id: 项目 ID
            error: 发生的错误
            error_context: 错误上下文信息
            causation_id: 因果关系 ID
            metadata: 额外的元数据
            
        Returns:
            发布的事件对象
        """
        event_id = self.generate_event_id()
        
        # 构建事件 payload
        payload = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_context": error_context or {},
            "timestamp": datetime.now().isoformat()
        }
        
        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.ERROR_OCCURRED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            metadata=metadata or {}
        )
        
        # 记录事件
        self._published_events.append(event)
        
        # 记录日志
        self.logger.error(
            f"Published ERROR_OCCURRED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "error_type": type(error).__name__,
                "error_message": str(error)
            }
        )
        
        return event
    
    async def publish_human_clarification_required(
        self,
        project_id: str,
        confidence_report: ConfidenceReport,
        causation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        发布 HUMAN_CLARIFICATION_REQUIRED 事件
        
        Args:
            project_id: 项目 ID
            confidence_report: 置信度报告
            causation_id: 因果关系 ID
            metadata: 额外的元数据
            
        Returns:
            发布的事件对象
        """
        event_id = self.generate_event_id()
        
        # 构建事件 payload
        payload = {
            "confidence_report": {
                "overall_confidence": confidence_report.overall_confidence,
                "confidence_level": confidence_report.confidence_level.value,
                "low_confidence_areas": confidence_report.low_confidence_areas,
                "clarification_requests": [
                    {
                        "field_name": req.field_name,
                        "current_value": req.current_value,
                        "reason": req.reason,
                        "suggestions": req.suggestions,
                        "priority": req.priority
                    }
                    for req in confidence_report.clarification_requests
                ],
                "recommendation": confidence_report.recommendation
            }
        }
        
        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=EventType.HUMAN_CLARIFICATION_REQUIRED,
            actor=self.agent_name,
            payload=payload,
            causation_id=causation_id,
            metadata=metadata or {}
        )
        
        # 记录事件
        self._published_events.append(event)
        
        # 记录日志
        self.logger.warning(
            f"Published HUMAN_CLARIFICATION_REQUIRED event",
            extra={
                "event_id": event_id,
                "project_id": project_id,
                "confidence": confidence_report.overall_confidence,
                "clarification_count": len(confidence_report.clarification_requests)
            }
        )
        
        return event
    
    async def write_to_blackboard(
        self,
        project_id: str,
        path: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> BlackboardWriteRequest:
        """
        写入数据到 Blackboard
        
        Args:
            project_id: 项目 ID
            path: 数据路径（例如 "global_spec"）
            data: 要写入的数据
            metadata: 额外的元数据
            
        Returns:
            Blackboard 写入请求对象
        """
        # 创建写入请求
        write_request = BlackboardWriteRequest(
            project_id=project_id,
            path=path,
            data=data,
            metadata=metadata or {}
        )
        
        # 记录日志
        self.logger.debug(
            f"Writing to Blackboard",
            extra={
                "project_id": project_id,
                "path": path,
                "data_keys": list(data.keys())
            }
        )
        
        # TODO: 实际的 Blackboard RPC 调用
        # 当前仅返回请求对象，实际实现需要调用 Blackboard 服务
        
        return write_request
    
    async def write_global_spec_to_blackboard(
        self,
        project_id: str,
        global_spec: GlobalSpec
    ) -> BlackboardWriteRequest:
        """
        将 GlobalSpec 写入 Blackboard
        
        Args:
            project_id: 项目 ID
            global_spec: GlobalSpec 对象
            
        Returns:
            Blackboard 写入请求对象
        """
        return await self.write_to_blackboard(
            project_id=project_id,
            path="global_spec",
            data=global_spec.to_dict(),
            metadata={
                "written_by": self.agent_name,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def get_published_events(self) -> list[Event]:
        """
        获取已发布的事件列表
        
        Returns:
            事件列表
        """
        return self._published_events.copy()
    
    def clear_published_events(self) -> None:
        """清空已发布的事件列表"""
        self._published_events.clear()
    
    def get_event_count(self) -> int:
        """
        获取已发布的事件数量
        
        Returns:
            事件数量
        """
        return len(self._published_events)
