"""
ScriptWriter Agent

负责剧本编写、shot 分解和情绪标注。
"""

import logging
from typing import Dict, Any

from src.infrastructure.event_bus import Event, EventType
from .llm_client import LLMClient
from .script_generator import ScriptGenerator
from .shot_decomposer import ShotDecomposer
from .emotion_tagger import EmotionTagger


logger = logging.getLogger(__name__)


class ScriptWriter:
    """
    ScriptWriter Agent
    
    负责：
    - 剧本生成（使用 LLM）
    - Shot 分解
    - 情绪标注
    - 用户修改处理
    - 自动重写（最多 3 次）
    """
    
    def __init__(self, blackboard, event_bus, llm_provider="openai"):
        """
        初始化 ScriptWriter
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            llm_provider: LLM 提供商 ("openai" 或 "claude")
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化组件
        self.llm_client = LLMClient(provider=llm_provider)
        self.script_generator = ScriptGenerator(self.llm_client)
        self.shot_decomposer = ShotDecomposer()
        self.emotion_tagger = EmotionTagger()
        
        logger.info(f"ScriptWriter initialized with {llm_provider}")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.PROJECT_CREATED:
                await self.write_script(event)
            elif event.type == EventType.REWRITE_SCENE:
                await self.rewrite_scene(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def write_script(self, event: Event) -> None:
        """
        编写剧本
        
        Args:
            event: PROJECT_CREATED 事件
        """
        project_id = event.project_id
        
        logger.info(f"Writing script for project {project_id}")
        
        try:
            # 获取 global_spec
            project = self.blackboard.get_project(project_id)
            
            if not project:
                logger.error(f"Project {project_id} not found")
                return
            
            global_spec = project.get("global_spec", {})
            
            # 生成剧本
            script = await self.script_generator.generate_script(global_spec)
            
            # 处理 shots：分解 + 标注情绪
            all_shots = []
            
            for scene in script.get("scenes", []):
                # 如果场景已有 shots，直接使用
                if "shots" in scene and scene["shots"]:
                    shots = scene["shots"]
                else:
                    # 否则分解场景
                    shots = self.shot_decomposer.break_into_shots(
                        scene,
                        target_duration=scene.get("duration_estimate", 10)
                    )
                    scene["shots"] = shots
                
                # 为每个 shot 标注情绪
                for shot in shots:
                    if "mood_tags" not in shot or not shot["mood_tags"]:
                        shot["mood_tags"] = self.emotion_tagger.tag_emotions(
                            shot.get("description", "")
                        )
                    
                    # 添加情绪强度
                    shot["mood_intensity"] = self.emotion_tagger.tag_mood_intensity(
                        shot.get("description", "")
                    )
                
                all_shots.extend(shots)
            
            # 保存到 Blackboard
            self.blackboard.update_project(project_id, {
                "script": script,
                "shots": all_shots
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.SCENE_WRITTEN,
                actor="ScriptWriter",
                payload={
                    "script": script,
                    "shots_count": len(all_shots),
                    "scenes_count": len(script.get("scenes", []))
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Script written: {len(script.get('scenes', []))} scenes, {len(all_shots)} shots")
            
        except Exception as e:
            logger.error(f"Failed to write script: {e}", exc_info=True)
    
    async def rewrite_scene(self, event: Event) -> None:
        """
        重写场景
        
        Args:
            event: REWRITE_SCENE 事件
        """
        project_id = event.project_id
        scene_id = event.payload.get("scene_id")
        reason = event.payload.get("reason", "Quality improvement")
        
        logger.info(f"Rewriting scene {scene_id}, reason: {reason}")
        
        try:
            # 获取当前剧本
            project = self.blackboard.get_project(project_id)
            script = project.get("script", {})
            
            # 找到需要重写的场景
            scene_index = None
            for i, scene in enumerate(script.get("scenes", [])):
                if scene.get("scene_id") == scene_id:
                    scene_index = i
                    break
            
            if scene_index is None:
                logger.error(f"Scene {scene_id} not found")
                return
            
            # 重写场景（简化版：重新生成整个剧本）
            # TODO: 实现单场景重写
            global_spec = project.get("global_spec", {})
            new_script = await self.script_generator.generate_script(global_spec)
            
            # 更新 Blackboard
            self.blackboard.update_project(project_id, {
                "script": new_script
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.SCENE_WRITTEN,
                actor="ScriptWriter",
                payload={
                    "script": new_script,
                    "is_rewrite": True,
                    "rewrite_reason": reason
                },
                causation_id=event.event_id
            ))
            
        except Exception as e:
            logger.error(f"Failed to rewrite scene: {e}", exc_info=True)
    
    async def handle_user_revision(self, revision_request: Dict[str, Any]) -> None:
        """
        处理用户修改请求
        
        Args:
            revision_request: 修改请求
                - project_id: 项目 ID
                - revision_notes: 用户修改意见
        """
        project_id = revision_request.get("project_id")
        revision_notes = revision_request.get("revision_notes", "")
        
        logger.info(f"Handling user revision for project {project_id}")
        
        try:
            # 获取原始剧本
            project = self.blackboard.get_project(project_id)
            original_script = project.get("script", {})
            
            if not original_script:
                logger.error("No original script found")
                return
            
            # 使用 LLM 修改
            revised_script = await self.script_generator.revise_script(
                original_script,
                revision_notes
            )
            
            # 重新标注情绪
            all_shots = []
            for scene in revised_script.get("scenes", []):
                for shot in scene.get("shots", []):
                    shot["mood_tags"] = self.emotion_tagger.tag_emotions(
                        shot.get("description", "")
                    )
                    all_shots.append(shot)
            
            # 保存到 Blackboard
            self.blackboard.update_project(project_id, {
                "script": revised_script,
                "shots": all_shots,
                "revision_history": project.get("revision_history", []) + [{
                    "notes": revision_notes,
                    "timestamp": "now"  # TODO: 使用实际时间戳
                }]
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.SCENE_WRITTEN,
                actor="ScriptWriter",
                payload={
                    "script": revised_script,
                    "is_revision": True,
                    "revision_notes": revision_notes
                }
            ))
            
            logger.info(f"Script revised based on user feedback")
            
        except Exception as e:
            logger.error(f"Failed to handle user revision: {e}", exc_info=True)
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("ScriptWriter Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("ScriptWriter Agent stopped")
