"""
Prompt 组合器

负责组合最终的 Prompt。
"""

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class PromptComposer:
    """
    Prompt 组合器
    
    负责将模板、变量、DNA tokens 等组合成最终 prompt。
    """
    
    def __init__(self, template_library):
        """
        初始化组合器
        
        Args:
            template_library: 模板库实例
        """
        self.template_library = template_library
    
    def compose_prompt(
        self,
        shot_spec: Dict[str, Any],
        dna_tokens: List[str],
        global_style: Dict[str, Any],
        quality_tier: str
    ) -> str:
        """
        组合最终 prompt
        
        Args:
            shot_spec: Shot 规格
            dna_tokens: DNA tokens 列表
            global_style: 全局风格
            quality_tier: 质量档位
            
        Returns:
            str: 组合后的 prompt
        """
        # 1. 选择模板
        template = self.template_library.select_template(
            shot_spec.get("type", ""),
            shot_spec.get("mood_tags", [])
        )
        
        if not template:
            logger.warning("No template found, using basic prompt")
            return self._create_basic_prompt(shot_spec)
        
        # 2. 填充变量
        prompt = self.fill_variables(template.base_prompt, shot_spec)
        
        # 3. 注入 DNA tokens
        if dna_tokens:
            prompt = f"{', '.join(dna_tokens)}, {prompt}"
        
        # 4. 添加质量修饰符
        quality_mod = template.quality_modifiers.get(quality_tier, "")
        if quality_mod:
            prompt = f"{prompt}{quality_mod}"
        
        # 5. 应用风格权重（如果有）
        if global_style and global_style.get("palette"):
            prompt = self.apply_style_weights(prompt, global_style["palette"])
        
        logger.debug(f"Composed prompt: {prompt[:100]}...")
        
        return prompt
    
    def fill_variables(self, template: str, shot_spec: Dict[str, Any]) -> str:
        """
        填充模板变量
        
        Args:
            template: 模板字符串
            shot_spec: Shot 规格
            
        Returns:
            str: 填充后的字符串
        """
        variables = {
            # 角色相关
            "character": self._get_first_character(shot_spec),
            "character_signature": shot_spec.get("character_signature", ""),
            "character_face": shot_spec.get("character_face", ""),
            "character_hair": shot_spec.get("character_hair", ""),
            "character_clothing": shot_spec.get("character_clothing", ""),
            "character_full": shot_spec.get("character_full", ""),
            
            # 动作相关
            "action": shot_spec.get("description", ""),
            "action_primary": shot_spec.get("action_primary", ""),
            "action_secondary": shot_spec.get("action_secondary", ""),
            "expression": shot_spec.get("expression", "neutral expression"),
            
            # 环境相关
            "environment": shot_spec.get("environment", ""),
            "location_type": shot_spec.get("location_type", ""),
            "space_layout": shot_spec.get("space_layout", ""),
            "key_objects": shot_spec.get("key_objects", ""),
            "background_elements": shot_spec.get("background_elements", ""),
            
            # 时间和天气
            "time_of_day": shot_spec.get("time_of_day", ""),
            "weather": shot_spec.get("weather", ""),
            
            # 光线和色彩
            "lighting": shot_spec.get("lighting", ""),
            "color_palette": shot_spec.get("color_palette", ""),
            
            # 情绪和风格
            "mood": ", ".join(shot_spec.get("mood_tags", [])),
            "atmosphere": shot_spec.get("atmosphere", ""),
            "style": shot_spec.get("style", "cinematic"),
            
            # 镜头相关
            "shot_type": shot_spec.get("shot_type", "medium shot"),
            "camera_movement": shot_spec.get("camera_movement", "static camera")
        }
        
        # 使用 format 填充
        try:
            filled = template.format(**variables)
        except KeyError as e:
            logger.warning(f"Missing variable in template: {e}")
            # 移除未填充的变量
            filled = template
            for key, value in variables.items():
                filled = filled.replace(f"{{{key}}}", value)
        
        # 清理多余的逗号和空格
        filled = self._clean_prompt(filled)
        
        return filled
    
    def _get_first_character(self, shot_spec: Dict[str, Any]) -> str:
        """获取第一个角色名称"""
        characters = shot_spec.get("characters", [])
        return characters[0] if characters else ""
    
    def _clean_prompt(self, prompt: str) -> str:
        """
        清理 prompt
        
        - 移除多余的逗号
        - 移除多余的空格
        - 移除空的占位符
        """
        # 移除空占位符
        prompt = prompt.replace("{}", "")
        
        # 移除多余的逗号
        while ",," in prompt:
            prompt = prompt.replace(",,", ",")
        
        # 移除开头和结尾的逗号
        prompt = prompt.strip(", ")
        
        # 移除多余的空格
        prompt = " ".join(prompt.split())
        
        return prompt
    
    def apply_style_weights(self, prompt: str, palette: Dict[str, Any]) -> str:
        """
        应用风格权重
        
        使用 (keyword:weight) 语法
        
        Args:
            prompt: 原始 prompt
            palette: 调色板信息
            
        Returns:
            str: 添加权重后的 prompt
        """
        weighted_prompt = prompt
        
        # 添加主色调权重
        if "dominant_colors" in palette:
            for color in palette["dominant_colors"]:
                weighted_prompt += f", ({color}:1.2)"
        
        return weighted_prompt
    
    def _create_basic_prompt(self, shot_spec: Dict[str, Any]) -> str:
        """
        创建基础 prompt（当没有模板时）
        
        Args:
            shot_spec: Shot 规格
            
        Returns:
            str: 基础 prompt
        """
        parts = []
        
        # 角色
        if shot_spec.get("characters"):
            parts.append(shot_spec["characters"][0])
        
        # 动作
        if shot_spec.get("description"):
            parts.append(shot_spec["description"])
        
        # 环境
        if shot_spec.get("environment"):
            parts.append(shot_spec["environment"])
        
        # 情绪
        if shot_spec.get("mood_tags"):
            parts.append(", ".join(shot_spec["mood_tags"]))
        
        # 风格
        if shot_spec.get("style"):
            parts.append(shot_spec["style"])
        
        return ", ".join(parts)
