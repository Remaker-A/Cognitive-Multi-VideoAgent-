"""
PromptEngineer Agent

负责 Prompt 编织、模板管理和 DNA token 注入。
"""

import logging
import random
from typing import Dict, Any, List

from src.infrastructure.event_bus import Event, EventType
from .template_library import TemplateLibrary
from .prompt_composer import PromptComposer
from .dna_injector import DNAInjector
from .negative_manager import NegativeManager


logger = logging.getLogger(__name__)


class PromptEngineer:
    """
    PromptEngineer Agent
    
    负责生成高质量的 prompts，包括：
    - 模板选择和管理
    - Prompt 组合
    - DNA token 注入
    - Negative prompt 生成
    """
    
    def __init__(self, blackboard, event_bus, templates_dir=None):
        """
        初始化 PromptEngineer
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
            templates_dir: 模板目录路径（可选）
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        # 初始化组件
        self.template_library = TemplateLibrary(templates_dir)
        self.prompt_composer = PromptComposer(self.template_library)
        self.dna_injector = DNAInjector(blackboard)
        self.negative_manager = NegativeManager()
        
        logger.info("PromptEngineer initialized")
    
    async def handle_event(self, event: Event) -> None:
        """
        处理事件
        
        Args:
            event: 事件对象
        """
        try:
            if event.type == EventType.KEYFRAME_REQUESTED:
                await self.generate_prompt(event)
            elif event.type == EventType.DNA_BANK_UPDATED:
                await self.update_character_tokens(event)
            else:
                logger.debug(f"Ignoring event type: {event.type}")
                
        except Exception as e:
            logger.error(f"Error handling event: {e}", exc_info=True)
    
    async def generate_prompt(self, event: Event) -> None:
        """
        生成 prompt
        
        Args:
            event: KEYFRAME_REQUESTED 事件
        """
        shot_id = event.payload.get("shot_id")
        project_id = event.project_id
        
        logger.info(f"Generating prompt for shot {shot_id}")
        
        try:
            # 获取 shot 信息
            shot = self.blackboard.get_shot(project_id, shot_id)
            
            if not shot:
                logger.error(f"Shot {shot_id} not found")
                return
            
            # 获取全局规格
            project = self.blackboard.get_project(project_id)
            global_spec = project.get("global_spec", {})
            
            # 生成 prompt 配置
            prompt_config = self.create_prompt_config(
                shot=shot,
                project_id=project_id,
                global_spec=global_spec,
                quality_tier=global_spec.get("quality_tier", "STANDARD")
            )
            
            # 保存到 Blackboard
            self.blackboard.update_shot(project_id, shot_id, {
                "prompt_config": prompt_config
            })
            
            # 发布事件
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.PROMPT_GENERATED,
                actor="PromptEngineer",
                payload={
                    "shot_id": shot_id,
                    "prompt_config": prompt_config
                },
                causation_id=event.event_id
            ))
            
            logger.info(f"Prompt generated for shot {shot_id}")
            
        except Exception as e:
            logger.error(f"Failed to generate prompt: {e}", exc_info=True)
    
    def create_prompt_config(
        self,
        shot: Dict[str, Any],
        project_id: str,
        global_spec: Dict[str, Any],
        quality_tier: str = "STANDARD"
    ) -> Dict[str, Any]:
        """
        创建 prompt 配置
        
        Args:
            shot: Shot 数据
            project_id: 项目 ID
            global_spec: 全局规格
            quality_tier: 质量档位
            
        Returns:
            Dict: Prompt 配置
        """
        # 1. 获取 DNA tokens
        dna_tokens = []
        characters = shot.get("characters", [])
        
        if characters:
            dna_tokens = self.dna_injector.get_all_character_tokens(
                project_id,
                characters
            )
        
        # 2. 选择模板
        template = self.template_library.select_template(
            shot.get("type", ""),
            shot.get("mood_tags", [])
        )
        
        # 3. 组合 positive prompt
        positive_prompt = self.prompt_composer.compose_prompt(
            shot_spec=shot,
            dna_tokens=dna_tokens,
            global_style=global_spec.get("style", {}),
            quality_tier=quality_tier
        )
        
        # 4. 生成 negative prompt
        negative_prompt = self.negative_manager.build_negative_prompt(
            template=template,
            shot_spec=shot,
            quality_tier=quality_tier
        )
        
        # 5. 获取默认参数
        default_params = template.default_params if template else {}
        
        # 6. 生成种子
        seed = self.generate_seed()
        
        prompt_config = {
            "positive": positive_prompt,
            "negative": negative_prompt,
            "seed": seed,
            "cfg_scale": default_params.get("cfg_scale", 7.5),
            "steps": default_params.get("steps", 30),
            "sampler": default_params.get("sampler", "DPM++ 2M Karras"),
            "template_id": template.template_id if template else None,
            "dna_tokens_count": len(dna_tokens),
            "quality_tier": quality_tier
        }
        
        return prompt_config
    
    async def update_character_tokens(self, event: Event) -> None:
        """
        更新角色 tokens（当 DNA Bank 更新时）
        
        Args:
            event: DNA_BANK_UPDATED 事件
        """
        character_name = event.payload.get("character_name")
        logger.info(f"DNA Bank updated for character: {character_name}")
        
        # 这里可以添加逻辑来重新生成受影响的 prompts
        # 目前只记录日志
    
    def generate_seed(self) -> int:
        """
        生成随机种子
        
        Returns:
            int: 随机种子
        """
        return random.randint(0, 2**32 - 1)
    
    async def start(self) -> None:
        """启动 Agent"""
        logger.info("PromptEngineer Agent started")
    
    async def stop(self) -> None:
        """停止 Agent"""
        logger.info("PromptEngineer Agent stopped")
