"""
ShotDirector Agent

负责 shot 级别规划和镜头设计。
"""

import logging
from typing import Dict, Any

from src.infrastructure.event_bus import Event, EventType
from .shot_planner import ShotPlanner
from .keyframe_requester import KeyframeRequester


logger = logging.getLogger(__name__)


class ShotDirector:
    """
    ShotDirector Agent
    
    负责：
    - Shot 级别规划
    - 镜头语言设计
    - Keyframe 请求生成
    - Preview Video 请求生成
    - Shot 审批
    """
    
    def __init__(self, blackboard, event_bus):
        """
        初始化 ShotDirector
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化组件
        self.shot_planner = ShotPlanner()
        self.keyframe_requester = KeyframeRequester()
        
        logger.info("ShotDirector initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.SCENE_WRITTEN:
                await self.plan_shots(event)
            elif event.type == EventType.DNA_BANK_UPDATED:
                await self.update_shot_plans(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def plan_shots(self, event: Event) -> None:
        """
        规划所有 shots
        
        Args:
            event: SCENE_WRITTEN 事件
        """
        project_id = event.project_id
        
        logger.info(f"Planning shots for project {project_id}")
        
        try:
            # 获取项目数据
            project = self.blackboard.get_project(project_id)
            
            if not project:
                logger.error(f"Project {project_id} not found")
                return
            
            shots = project.get("shots", [])
            dna_bank = project.get("dna_bank", {})
            
            if not shots:
                logger.warning(f"No shots found in project {project_id}")
                return
            
            # 规划每个 shot
            for shot in shots:
                await self._plan_and_request_single_shot(
                    project_id,
                    shot,
                    dna_bank
                )
            
            # 发布完成事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.SHOT_PLANNED,
                actor="ShotDirector",
                payload={
                    "shots_count": len(shots)
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Planned {len(shots)} shots")
            
        except Exception as e:
            logger.error(f"Failed to plan shots: {e}", exc_info=True)
    
    async def _plan_and_request_single_shot(
        self,
        project_id: str,
        shot: Dict[str, Any],
        dna_bank: Dict[str, Any]
    ) -> None:
        """规划单个 shot 并发送请求"""
        shot_id = shot.get("shot_id")
        
        # 1. 规划 shot
        shot_plan = self.shot_planner.plan_shot(shot, dna_bank)
        
        # 2. 保存 shot plan 到 Blackboard
        self.blackboard.update_shot(project_id, shot_id, {
            "shot_plan": shot_plan
        })
        
        # 3. 创建 keyframe 请求
        keyframe_requests = self.keyframe_requester.create_keyframe_requests(
            shot,
            shot_plan
        )
        
        # 4. 发布 keyframe 请求事件
        for kf_request in keyframe_requests:
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.KEYFRAME_REQUESTED,
                actor="ShotDirector",
                payload={
                    "shot_id": shot_id,
                    "keyframe_request": kf_request
                }
            ))
        
        logger.debug(f"Requested {len(keyframe_requests)} keyframes for shot {shot_id}")
    
    async def request_preview_video(
        self,
        project_id: str,
        shot_id: str
    ) -> None:
        """
        请求 preview video
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
        """
        logger.info(f"Requesting preview video for shot {shot_id}")
        
        try:
            # 获取 shot 数据
            shot = self.blackboard.get_shot(project_id, shot_id)
            shot_plan = shot.get("shot_plan", {})
            
            # 创建 preview 请求
            preview_request = self.keyframe_requester.create_preview_video_request(
                shot,
                shot_plan
            )
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.PREVIEW_VIDEO_REQUESTED,
                actor="ShotDirector",
                payload={
                    "shot_id": shot_id,
                    "preview_request": preview_request
                }
            ))
            
            logger.info(f"Preview video requested for shot {shot_id}")
            
        except Exception as e:
            logger.error(f"Failed to request preview video: {e}", exc_info=True)
    
    async def approve_shot(
        self,
        project_id: str,
        shot_id: str,
        approval_notes: str = ""
    ) -> None:
        """
        审批 shot
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            approval_notes: 审批备注
        """
        logger.info(f"Approving shot {shot_id}")
        
        try:
            # 更新 Blackboard
            self.blackboard.update_shot(project_id, shot_id, {
                "approved": True,
                "approval_notes": approval_notes
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.SHOT_APPROVED,
                actor="ShotDirector",
                payload={
                    "shot_id": shot_id,
                    "approval_notes": approval_notes
                }
            ))
            
            logger.info(f"Shot {shot_id} approved")
            
        except Exception as e:
            logger.error(f"Failed to approve shot: {e}", exc_info=True)
    
    async def update_shot_plans(self, event: Event) -> None:
        """
        更新 shot plans（当 DNA Bank 更新时）
        
        Args:
            event: DNA_BANK_UPDATED 事件
        """
        character_name = event.payload.get("character_name")
        logger.info(f"DNA Bank updated for {character_name}, updating affected shots")
        
        # TODO: 找到包含该角色的 shots 并重新规划
        # 这里是占位符
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ShotDirector Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ShotDirector Agent stopped")
