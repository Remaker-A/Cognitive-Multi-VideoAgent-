"""
审批管理器

管理用户审批流程。
"""

import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

from ..blackboard.blackboard import SharedBlackboard
from ..event_bus.event import Event, EventType


logger = logging.getLogger(__name__)


# 默认审批检查点
DEFAULT_APPROVAL_CHECKPOINTS = [
    EventType.SCENE_WRITTEN,
    EventType.SHOT_PLANNED,
    EventType.PREVIEW_VIDEO_READY,
    EventType.FINAL_VIDEO_READY
]


class ApprovalManager:
    """
    审批管理器
    
    Features:
    - 检查审批检查点
    - 创建审批请求
    - 处理用户决策
    - 项目暂停/恢复
    """
    
    def __init__(self, blackboard: SharedBlackboard, event_bus=None):
        """
        初始化审批管理器
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例（可选）
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.paused_projects = set()
    
    def check_approval_required(self, event: Event) -> bool:
        """
        检查事件是否需要用户审批
        
        Args:
            event: 事件对象
            
        Returns:
            bool: 是否需要审批
        """
        try:
            project = self.blackboard.get_project(event.project_id)
            
            # 检查是否启用自动模式
            global_spec = project.get('global_spec', {})
            user_options = global_spec.get('user_options', {})
            
            if user_options.get('auto_mode', False):
                logger.debug(f"Project {event.project_id} in auto mode, skip approval")
                return False
            
            # 获取审批检查点配置
            checkpoints = user_options.get(
                'approval_checkpoints',
                [cp.value for cp in DEFAULT_APPROVAL_CHECKPOINTS]
            )
            
            # 检查事件类型是否在检查点中
            is_required = event.type.value in checkpoints
            
            if is_required:
                logger.info(f"Approval required for event {event.type.value}")
            
            return is_required
            
        except Exception as e:
            logger.error(f"Failed to check approval requirement: {e}")
            return False
    
    async def request_approval(self, event: Event) -> Dict[str, Any]:
        """
        创建审批请求
        
        Args:
            event: 触发审批的事件
            
        Returns:
            Dict: 审批请求对象
        """
        import uuid
        
        approval_request = {
            "approval_id": f"APPR-{uuid.uuid4().hex[:8]}",
            "project_id": event.project_id,
            "stage": event.type.value,
            "status": "PENDING",
            "content": self._extract_approval_content(event),
            "options": ["approve", "revise", "reject"],
            "created_at": datetime.utcnow().isoformat(),
            "timeout_minutes": 60,
            "user_decision": None
        }
        
        # 写入 Blackboard
        # TODO: 实现 create_approval_request 方法
        # self.blackboard.create_approval_request(approval_request)
        
        # 发布审批请求事件
        if self.event_bus:
            await self.event_bus.publish(Event(
                project_id=event.project_id,
                type=EventType.USER_APPROVAL_REQUIRED,
                actor="ApprovalManager",
                payload=approval_request
            ))
        
        # 暂停项目
        self.pause_project(event.project_id)
        
        logger.info(
            f"Created approval request {approval_request['approval_id']} "
            f"for project {event.project_id}"
        )
        
        return approval_request
    
    def _extract_approval_content(self, event: Event) -> Dict[str, Any]:
        """
        从事件中提取审批内容
        
        Args:
            event: 事件对象
            
        Returns:
            Dict: 审批内容
        """
        content = {
            "type": event.type.value,
            "data": event.payload,
            "metadata": event.metadata
        }
        
        # 根据事件类型提取特定内容
        if event.type == EventType.SCENE_WRITTEN:
            content["preview_type"] = "script"
            content["script"] = event.payload.get("script")
        
        elif event.type == EventType.SHOT_PLANNED:
            content["preview_type"] = "shots"
            content["shots"] = event.payload.get("shots")
        
        elif event.type == EventType.PREVIEW_VIDEO_READY:
            content["preview_type"] = "preview_video"
            content["preview_url"] = event.payload.get("artifact_url")
        
        elif event.type == EventType.FINAL_VIDEO_READY:
            content["preview_type"] = "final_video"
            content["preview_url"] = event.payload.get("artifact_url")
        
        return content
    
    async def handle_decision(self, decision_data: Dict[str, Any]) -> None:
        """
        处理用户决策
        
        Args:
            decision_data: 决策数据
        """
        approval_id = decision_data.get("approval_id")
        project_id = decision_data.get("project_id")
        decision = decision_data.get("decision")
        
        logger.info(f"Handling approval decision: {decision} for {approval_id}")
        
        if decision == "approve":
            # 恢复项目执行
            self.resume_project(project_id)
            
            # 发布批准事件
            if self.event_bus:
                await self.event_bus.publish(Event(
                    project_id=project_id,
                    type=EventType.USER_APPROVED,
                    actor="ApprovalManager",
                    payload={"approval_id": approval_id}
                ))
        
        elif decision == "revise":
            # 获取修改意见
            revision_notes = decision_data.get("revision_notes", "")
            
            # 发布修改请求事件
            if self.event_bus:
                await self.event_bus.publish(Event(
                    project_id=project_id,
                    type=EventType.USER_REVISION_REQUESTED,
                    actor="ApprovalManager",
                    payload={
                        "approval_id": approval_id,
                        "revision_notes": revision_notes
                    }
                ))
        
        elif decision == "reject":
            # 发布拒绝事件
            if self.event_bus:
                await self.event_bus.publish(Event(
                    project_id=project_id,
                    type=EventType.USER_REJECTED,
                    actor="ApprovalManager",
                    payload={"approval_id": approval_id}
                ))
    
    def pause_project(self, project_id: str) -> None:
        """
        暂停项目执行
        
        Args:
            project_id: 项目 ID
        """
        self.paused_projects.add(project_id)
        logger.info(f"Paused project {project_id}")
    
    def resume_project(self, project_id: str) -> None:
        """
        恢复项目执行
        
        Args:
            project_id: 项目 ID
        """
        self.paused_projects.discard(project_id)
        logger.info(f"Resumed project {project_id}")
    
    def is_paused(self, project_id: str) -> bool:
        """
        检查项目是否暂停
        
        Args:
            project_id: 项目 ID
            
        Returns:
            bool: 是否暂停
        """
        return project_id in self.paused_projects
