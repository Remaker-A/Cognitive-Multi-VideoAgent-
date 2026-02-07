"""
GlobalSpec生成器模块

负责基于分析结果生成标准化的GlobalSpec
"""

import logging
from typing import Dict, Any, Optional, List

from .models import (
    GlobalSpec,
    StyleConfig,
    SynthesizedAnalysis,
    TextAnalysis,
    VisualStyle,
    MotionStyle,
    AudioMood,
    UserInputData
)
from .utils import (
    estimate_duration_from_text,
    determine_aspect_ratio,
    calculate_resolution
)
from .logger import setup_logger

logger = setup_logger(__name__)


class GlobalSpecGenerator:
    """
    GlobalSpec生成器
    
    职责：
    - 基于分析结果生成标准化的GlobalSpec
    - 提取项目标题
    - 估算视频时长
    - 确定宽高比和分辨率
    - 提取角色列表
    - 综合风格配置
    - 设置合理的默认值
    """
    
    def __init__(self, default_config: Optional[Dict[str, Any]] = None):
        """
        初始化GlobalSpec生成器
        
        Args:
            default_config: 默认配置字典
        """
        self.default_config = default_config or self._get_default_config()
        logger.info("GlobalSpecGenerator initialized", extra={"default_config": self.default_config})
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        获取默认配置
        
        Returns:
            Dict[str, Any]: 默认配置字典
        """
        return {
            "quality_tier": "balanced",
            "fps": 30,
            "aspect_ratio": "9:16",
            "duration": 30,
            "tone": "natural",
            "palette": ["#FFFFFF", "#000000"],
            "visual_dna_version": 1
        }
    
    async def generate_spec(
        self,
        analysis: SynthesizedAnalysis,
        user_input: Optional[UserInputData] = None
    ) -> GlobalSpec:
        """
        生成GlobalSpec
        
        Args:
            analysis: 综合分析结果
            user_input: 用户输入数据（可选）
        
        Returns:
            GlobalSpec: 生成的全局规格
        """
        logger.info("Generating GlobalSpec from analysis")
        
        # 提取标题
        title = self._extract_title(analysis.text_analysis, analysis.overall_theme)
        
        # 估算时长
        duration = self._estimate_duration(analysis.text_analysis, user_input)
        
        # 确定宽高比
        aspect_ratio = self._determine_aspect_ratio(
            user_input.user_preferences if user_input else {},
            analysis.visual_style
        )
        
        # 计算分辨率
        quality_tier = self._get_quality_tier(user_input)
        resolution = calculate_resolution(aspect_ratio, quality_tier)
        
        # 获取FPS
        fps = self._get_fps(user_input)
        
        # 综合风格配置
        style = self._synthesize_style(
            analysis.visual_style,
            analysis.motion_style,
            analysis.audio_mood
        )
        
        # 提取角色列表
        characters = self._extract_characters(analysis.text_analysis)
        
        # 提取情绪
        mood = self._extract_mood(analysis)
        
        # 获取用户选项
        user_options = user_input.user_preferences if user_input else {}
        
        # 创建GlobalSpec
        global_spec = GlobalSpec(
            title=title,
            duration=duration,
            aspect_ratio=aspect_ratio,
            quality_tier=quality_tier,
            resolution=resolution,
            fps=fps,
            style=style,
            characters=characters,
            mood=mood,
            user_options=user_options
        )
        
        logger.info(
            "GlobalSpec generated successfully",
            extra={
                "title": title,
                "duration": duration,
                "aspect_ratio": aspect_ratio,
                "characters_count": len(characters)
            }
        )
        
        return global_spec
    
    def _extract_title(
        self,
        text_analysis: Optional[TextAnalysis],
        overall_theme: str
    ) -> str:
        """
        提取项目标题
        
        Args:
            text_analysis: 文本分析结果
            overall_theme: 整体主题
        
        Returns:
            str: 项目标题
        """
        # 优先使用文本分析的主题
        if text_analysis and text_analysis.main_theme:
            title = text_analysis.main_theme
            # 限制标题长度
            if len(title) > 50:
                title = title[:47] + "..."
            return title
        
        # 使用整体主题
        if overall_theme:
            return overall_theme
        
        # 使用默认标题
        return "视频项目"
    
    def _estimate_duration(
        self,
        text_analysis: Optional[TextAnalysis],
        user_input: Optional[UserInputData]
    ) -> int:
        """
        估算视频时长
        
        Args:
            text_analysis: 文本分析结果
            user_input: 用户输入数据
        
        Returns:
            int: 估算的时长（秒）
        """
        # 优先使用用户偏好
        if user_input and "duration" in user_input.user_preferences:
            duration = user_input.user_preferences["duration"]
            if isinstance(duration, (int, float)) and 5 <= duration <= 600:
                return int(duration)
        
        # 使用文本分析的估算
        if text_analysis and text_analysis.estimated_duration:
            duration = text_analysis.estimated_duration
            # 确保在合理范围内
            if 5 <= duration <= 600:
                return duration
        
        # 从用户输入文本估算
        if user_input and user_input.text_description:
            duration = estimate_duration_from_text(user_input.text_description)
            return duration
        
        # 使用默认值
        return self.default_config["duration"]
    
    def _determine_aspect_ratio(
        self,
        user_prefs: Dict[str, Any],
        visual_style: Optional[VisualStyle]
    ) -> str:
        """
        确定宽高比
        
        Args:
            user_prefs: 用户偏好
            visual_style: 视觉风格分析结果
        
        Returns:
            str: 宽高比字符串
        """
        # 优先使用用户偏好（仅当有效时）
        if "aspect_ratio" in user_prefs:
            aspect_ratio = user_prefs["aspect_ratio"]
            if aspect_ratio in ["9:16", "16:9", "1:1", "4:3"]:
                return aspect_ratio
        
        # 基于视觉风格判断
        visual_hints = {}
        if visual_style:
            # 这里可以根据视觉风格的特征判断
            # 例如：如果构图风格是"vertical"，则使用竖屏
            if visual_style.composition_style and "vertical" in visual_style.composition_style.lower():
                visual_hints["vertical_oriented"] = True
            elif visual_style.composition_style and "horizontal" in visual_style.composition_style.lower():
                visual_hints["horizontal_oriented"] = True
        
        # 不传递无效的用户偏好给determine_aspect_ratio
        valid_user_pref = None
        if "aspect_ratio" in user_prefs and user_prefs["aspect_ratio"] in ["9:16", "16:9", "1:1", "4:3"]:
            valid_user_pref = user_prefs["aspect_ratio"]
        
        return determine_aspect_ratio(
            user_preference=valid_user_pref,
            visual_hints=visual_hints
        )
    
    def _get_quality_tier(self, user_input: Optional[UserInputData]) -> str:
        """
        获取质量档位
        
        Args:
            user_input: 用户输入数据
        
        Returns:
            str: 质量档位
        """
        if user_input and "quality_tier" in user_input.user_preferences:
            quality_tier = user_input.user_preferences["quality_tier"]
            if quality_tier in ["high", "balanced", "fast"]:
                return quality_tier
        
        return self.default_config["quality_tier"]
    
    def _get_fps(self, user_input: Optional[UserInputData]) -> int:
        """
        获取帧率
        
        Args:
            user_input: 用户输入数据
        
        Returns:
            int: 帧率
        """
        if user_input and "fps" in user_input.user_preferences:
            fps = user_input.user_preferences["fps"]
            if isinstance(fps, int) and fps in [24, 30, 60]:
                return fps
        
        return self.default_config["fps"]
    
    def _extract_characters(self, text_analysis: Optional[TextAnalysis]) -> List[str]:
        """
        提取角色列表
        
        Args:
            text_analysis: 文本分析结果
        
        Returns:
            List[str]: 角色名称列表
        """
        if not text_analysis or not text_analysis.characters:
            return []
        
        # 提取角色名称
        character_names = [char.name for char in text_analysis.characters if char.name]
        
        logger.debug(f"Extracted {len(character_names)} characters", extra={"characters": character_names})
        
        return character_names
    
    def _synthesize_style(
        self,
        visual_style: Optional[VisualStyle],
        motion_style: Optional[MotionStyle],
        audio_mood: Optional[AudioMood]
    ) -> StyleConfig:
        """
        综合风格配置
        
        Args:
            visual_style: 视觉风格分析结果
            motion_style: 运动风格分析结果
            audio_mood: 音频情绪分析结果
        
        Returns:
            StyleConfig: 风格配置
        """
        # 确定色调（tone）
        tone = self._determine_tone(visual_style, motion_style, audio_mood)
        
        # 确定调色板（palette）
        palette = self._determine_palette(visual_style)
        
        # 视觉DNA版本
        visual_dna_version = self.default_config["visual_dna_version"]
        
        style_config = StyleConfig(
            tone=tone,
            palette=palette,
            visual_dna_version=visual_dna_version
        )
        
        logger.debug(
            "Style configuration synthesized",
            extra={
                "tone": tone,
                "palette_size": len(palette)
            }
        )
        
        return style_config
    
    def _determine_tone(
        self,
        visual_style: Optional[VisualStyle],
        motion_style: Optional[MotionStyle],
        audio_mood: Optional[AudioMood]
    ) -> str:
        """
        确定色调
        
        综合视觉、运动和音频的信息确定整体色调
        
        Args:
            visual_style: 视觉风格分析结果
            motion_style: 运动风格分析结果
            audio_mood: 音频情绪分析结果
        
        Returns:
            str: 色调描述
        """
        # 优先使用视觉风格的光照风格
        if visual_style and visual_style.lighting_style:
            return visual_style.lighting_style
        
        # 基于音频情绪推断
        if audio_mood:
            mood_to_tone = {
                "happy": "bright",
                "sad": "dark",
                "calm": "soft",
                "energetic": "vibrant",
                "mysterious": "moody"
            }
            if audio_mood.mood in mood_to_tone:
                return mood_to_tone[audio_mood.mood]
        
        # 基于运动风格推断
        if motion_style:
            if motion_style.energy_level == "high":
                return "dynamic"
            elif motion_style.energy_level == "low":
                return "calm"
        
        # 使用默认值
        return self.default_config["tone"]
    
    def _determine_palette(self, visual_style: Optional[VisualStyle]) -> List[str]:
        """
        确定调色板
        
        Args:
            visual_style: 视觉风格分析结果
        
        Returns:
            List[str]: 颜色列表（十六进制格式）
        """
        # 使用视觉风格的调色板
        if visual_style and visual_style.color_palette:
            # 确保颜色格式正确
            palette = []
            for color in visual_style.color_palette:
                # 如果不是十六进制格式，尝试转换或使用默认值
                if color.startswith("#"):
                    palette.append(color)
                else:
                    # 简单的颜色名称到十六进制的映射
                    color_map = {
                        "red": "#FF0000",
                        "green": "#00FF00",
                        "blue": "#0000FF",
                        "yellow": "#FFFF00",
                        "purple": "#800080",
                        "orange": "#FFA500",
                        "pink": "#FFC0CB",
                        "brown": "#A52A2A",
                        "gray": "#808080",
                        "black": "#000000",
                        "white": "#FFFFFF"
                    }
                    palette.append(color_map.get(color.lower(), "#808080"))
            
            if palette:
                return palette[:10]  # 最多10个颜色
        
        # 使用默认调色板
        return self.default_config["palette"]
    
    def _extract_mood(self, analysis: SynthesizedAnalysis) -> str:
        """
        提取整体情绪
        
        Args:
            analysis: 综合分析结果
        
        Returns:
            str: 情绪标签字符串（逗号分隔）
        """
        mood_tags = []
        
        # 从文本分析提取情绪标签
        if analysis.text_analysis and analysis.text_analysis.mood_tags:
            mood_tags.extend(analysis.text_analysis.mood_tags)
        
        # 从视觉风格提取情绪描述
        if analysis.visual_style and analysis.visual_style.mood_descriptors:
            mood_tags.extend(analysis.visual_style.mood_descriptors)
        
        # 从音频情绪提取
        if analysis.audio_mood and analysis.audio_mood.mood:
            mood_tags.append(analysis.audio_mood.mood)
        
        # 去重并限制数量
        unique_moods = list(dict.fromkeys(mood_tags))[:5]
        
        # 组合成字符串
        mood_string = ",".join(unique_moods) if unique_moods else "neutral"
        
        logger.debug(f"Extracted mood: {mood_string}")
        
        return mood_string
