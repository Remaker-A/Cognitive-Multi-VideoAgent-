"""
多模态分析器模块

负责协调不同模态的分析，整合分析结果
"""

import json
import logging
from typing import List, Dict, Any, Optional

from .deepseek_client import DeepSeekClient
from .models import (
    ProcessedText,
    ProcessedImage,
    ProcessedVideo,
    ProcessedAudio,
    TextAnalysis,
    VisualStyle,
    MotionStyle,
    AudioMood,
    SynthesizedAnalysis,
    CharacterInfo,
    SceneInfo
)
from .logger import setup_logger

logger = setup_logger(__name__)


class MultimodalAnalyzer:
    """
    多模态分析器
    
    职责：
    - 分析文本意图和关键信息
    - 分析视觉风格和色彩偏好
    - 分析运镜风格和节奏偏好
    - 分析音频情绪和风格
    - 综合所有分析结果
    """
    
    def __init__(self, deepseek_client: DeepSeekClient):
        """
        初始化多模态分析器
        
        Args:
            deepseek_client: DeepSeek API 客户端
        """
        self.deepseek_client = deepseek_client
        logger.info("MultimodalAnalyzer initialized")
    
    async def analyze_text_intent(self, text: ProcessedText) -> TextAnalysis:
        """
        分析文本意图和关键信息
        
        Args:
            text: 处理后的文本数据
        
        Returns:
            TextAnalysis: 文本分析结果
        """
        logger.info("Analyzing text intent", extra={"text_length": len(text.cleaned)})
        
        try:
            # 构建分析提示词
            system_prompt = """你是一个专业的视频需求分析助手。
请分析用户的文本描述，提取以下信息：
1. 主题（main_theme）：视频的核心主题
2. 角色（characters）：出现的角色及其描述
3. 场景（scenes）：场景描述和位置
4. 情绪标签（mood_tags）：整体情绪氛围
5. 预估时长（estimated_duration）：视频时长（秒）
6. 叙事结构（narrative_structure）：线性/非线性/循环等
7. 类型（genre）：视频类型
8. 目标受众（target_audience）：目标观众群体

以JSON格式返回结果。"""
            
            user_prompt = f"""请分析以下文本描述：

{text.cleaned}

关键短语：{', '.join(text.key_phrases)}
情感：{text.sentiment}"""
            
            # 调用 DeepSeek API
            response = await self.deepseek_client.analyze_multimodal(
                text=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # 解析响应
            analysis_result = self._parse_text_analysis(response.analysis_text, text)
            
            logger.info(
                "Text analysis completed",
                extra={
                    "main_theme": analysis_result.main_theme,
                    "characters_count": len(analysis_result.characters),
                    "scenes_count": len(analysis_result.scenes)
                }
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Failed to analyze text intent: {e}")
            # 返回基础分析结果
            return self._create_fallback_text_analysis(text)
    
    def _parse_text_analysis(self, analysis_text: str, original_text: ProcessedText) -> TextAnalysis:
        """
        解析文本分析结果
        
        Args:
            analysis_text: API 返回的分析文本
            original_text: 原始处理后的文本
        
        Returns:
            TextAnalysis: 解析后的文本分析结果
        """
        try:
            # 尝试从响应中提取 JSON
            # 查找 JSON 代码块
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "{" in analysis_text and "}" in analysis_text:
                # 尝试提取 JSON 对象
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                json_str = analysis_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_str)
            
            # 解析角色信息
            characters = []
            for char_data in data.get("characters", []):
                if isinstance(char_data, dict):
                    characters.append(CharacterInfo(
                        name=char_data.get("name", ""),
                        description=char_data.get("description", ""),
                        role=char_data.get("role", "supporting"),
                        traits=char_data.get("traits", [])
                    ))
                elif isinstance(char_data, str):
                    characters.append(CharacterInfo(
                        name=char_data,
                        description="",
                        role="supporting",
                        traits=[]
                    ))
            
            # 解析场景信息
            scenes = []
            for scene_data in data.get("scenes", []):
                if isinstance(scene_data, dict):
                    scenes.append(SceneInfo(
                        description=scene_data.get("description", ""),
                        location=scene_data.get("location", ""),
                        time_of_day=scene_data.get("time_of_day"),
                        mood=scene_data.get("mood", ""),
                        duration_estimate=scene_data.get("duration_estimate")
                    ))
                elif isinstance(scene_data, str):
                    scenes.append(SceneInfo(
                        description=scene_data,
                        location="",
                        mood=""
                    ))
            
            return TextAnalysis(
                main_theme=data.get("main_theme", original_text.cleaned[:50]),
                characters=characters,
                scenes=scenes,
                mood_tags=data.get("mood_tags", []),
                estimated_duration=data.get("estimated_duration", 30),
                narrative_structure=data.get("narrative_structure", "linear"),
                genre=data.get("genre"),
                target_audience=data.get("target_audience")
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse text analysis JSON: {e}")
            return self._create_fallback_text_analysis(original_text)
    
    def _create_fallback_text_analysis(self, text: ProcessedText) -> TextAnalysis:
        """
        创建降级的文本分析结果
        
        Args:
            text: 处理后的文本
        
        Returns:
            TextAnalysis: 基础分析结果
        """
        return TextAnalysis(
            main_theme=text.cleaned[:50] if text.cleaned else "未知主题",
            characters=[],
            scenes=[],
            mood_tags=[text.sentiment] if text.sentiment else [],
            estimated_duration=30,
            narrative_structure="linear"
        )
    
    async def analyze_visual_style(self, images: List[ProcessedImage]) -> VisualStyle:
        """
        分析视觉风格和色彩偏好
        
        Args:
            images: 处理后的图片数据列表
        
        Returns:
            VisualStyle: 视觉风格分析结果
        """
        logger.info(f"Analyzing visual style from {len(images)} images")
        
        if not images:
            logger.info("No images provided, returning default visual style")
            return VisualStyle()
        
        try:
            # 构建分析提示词
            system_prompt = """你是一个专业的视觉风格分析师。
请分析参考图片，提取以下信息：
1. 色彩调色板（color_palette）：主要颜色列表
2. 光照风格（lighting_style）：自然光/人工光/戏剧性/柔和等
3. 构图风格（composition_style）：平衡/对称/动态/极简等
4. 艺术风格（art_style）：写实/卡通/抽象/复古等
5. 参考风格（reference_styles）：类似的艺术风格或流派
6. 情绪描述（mood_descriptors）：视觉传达的情绪

以JSON格式返回结果。"""
            
            # 构建图片描述
            image_descriptions = []
            for i, img in enumerate(images[:5]):  # 最多分析5张图片
                image_descriptions.append(f"图片{i+1}: {img.url}")
            
            user_prompt = f"""请分析以下参考图片的视觉风格：

{chr(10).join(image_descriptions)}

请提取整体的视觉风格特征。"""
            
            # 调用 DeepSeek API
            response = await self.deepseek_client.analyze_multimodal(
                text=user_prompt,
                images=[img.url for img in images[:5]],
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # 解析响应
            visual_style = self._parse_visual_style(response.analysis_text)
            
            logger.info(
                "Visual style analysis completed",
                extra={
                    "lighting_style": visual_style.lighting_style,
                    "art_style": visual_style.art_style,
                    "color_count": len(visual_style.color_palette)
                }
            )
            
            return visual_style
            
        except Exception as e:
            logger.error(f"Failed to analyze visual style: {e}")
            return VisualStyle()
    
    def _parse_visual_style(self, analysis_text: str) -> VisualStyle:
        """
        解析视觉风格分析结果
        
        Args:
            analysis_text: API 返回的分析文本
        
        Returns:
            VisualStyle: 解析后的视觉风格
        """
        try:
            # 提取 JSON
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "{" in analysis_text and "}" in analysis_text:
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                json_str = analysis_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_str)
            
            return VisualStyle(
                color_palette=data.get("color_palette", []),
                lighting_style=data.get("lighting_style", "natural"),
                composition_style=data.get("composition_style", "balanced"),
                art_style=data.get("art_style", "realistic"),
                reference_styles=data.get("reference_styles", []),
                mood_descriptors=data.get("mood_descriptors", [])
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse visual style JSON: {e}")
            return VisualStyle()
    
    async def analyze_motion_style(self, videos: List[ProcessedVideo]) -> MotionStyle:
        """
        分析运镜风格和节奏偏好
        
        Args:
            videos: 处理后的视频数据列表
        
        Returns:
            MotionStyle: 运动风格分析结果
        """
        logger.info(f"Analyzing motion style from {len(videos)} videos")
        
        if not videos:
            logger.info("No videos provided, returning default motion style")
            return MotionStyle()
        
        try:
            # 构建分析提示词
            system_prompt = """你是一个专业的视频运镜分析师。
请分析参考视频，提取以下信息：
1. 镜头运动（camera_movement）：静态/推拉/摇移/跟随/航拍等
2. 节奏（pace）：慢速/中速/快速
3. 转场风格（transition_style）：切/淡入淡出/擦除/特效等
4. 能量级别（energy_level）：低/中/高

以JSON格式返回结果。"""
            
            # 构建视频描述
            video_descriptions = []
            for i, vid in enumerate(videos[:3]):  # 最多分析3个视频
                video_descriptions.append(
                    f"视频{i+1}: {vid.url} (时长: {vid.duration}秒, {vid.fps}fps)"
                )
            
            user_prompt = f"""请分析以下参考视频的运镜风格：

{chr(10).join(video_descriptions)}

请提取整体的运镜和节奏特征。"""
            
            # 调用 DeepSeek API
            response = await self.deepseek_client.analyze_multimodal(
                text=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # 解析响应
            motion_style = self._parse_motion_style(response.analysis_text)
            
            logger.info(
                "Motion style analysis completed",
                extra={
                    "camera_movement": motion_style.camera_movement,
                    "pace": motion_style.pace,
                    "energy_level": motion_style.energy_level
                }
            )
            
            return motion_style
            
        except Exception as e:
            logger.error(f"Failed to analyze motion style: {e}")
            return MotionStyle()
    
    def _parse_motion_style(self, analysis_text: str) -> MotionStyle:
        """
        解析运动风格分析结果
        
        Args:
            analysis_text: API 返回的分析文本
        
        Returns:
            MotionStyle: 解析后的运动风格
        """
        try:
            # 提取 JSON
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "{" in analysis_text and "}" in analysis_text:
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                json_str = analysis_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_str)
            
            return MotionStyle(
                camera_movement=data.get("camera_movement", "static"),
                pace=data.get("pace", "medium"),
                transition_style=data.get("transition_style", "cut"),
                energy_level=data.get("energy_level", "medium")
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse motion style JSON: {e}")
            return MotionStyle()
    
    async def analyze_audio_mood(self, audio: List[ProcessedAudio]) -> AudioMood:
        """
        分析音频情绪和风格
        
        Args:
            audio: 处理后的音频数据列表
        
        Returns:
            AudioMood: 音频情绪分析结果
        """
        logger.info(f"Analyzing audio mood from {len(audio)} audio files")
        
        if not audio:
            logger.info("No audio provided, returning default audio mood")
            return AudioMood()
        
        try:
            # 构建分析提示词
            system_prompt = """你是一个专业的音乐情绪分析师。
请分析参考音频，提取以下信息：
1. 节奏（tempo）：慢速/中速/快速
2. 能量（energy）：低/中/高
3. 情绪（mood）：欢快/悲伤/平静/激动/神秘等
4. 类型（genre）：流行/古典/电子/摇滚等
5. 乐器（instruments）：主要乐器列表

以JSON格式返回结果。"""
            
            # 构建音频描述
            audio_descriptions = []
            for i, aud in enumerate(audio[:3]):  # 最多分析3个音频
                audio_descriptions.append(
                    f"音频{i+1}: {aud.url} (时长: {aud.duration}秒, {aud.sample_rate}Hz)"
                )
            
            user_prompt = f"""请分析以下参考音频的情绪和风格：

{chr(10).join(audio_descriptions)}

请提取整体的音乐特征和情绪。"""
            
            # 调用 DeepSeek API
            response = await self.deepseek_client.analyze_multimodal(
                text=user_prompt,
                system_prompt=system_prompt,
                temperature=0.7
            )
            
            # 解析响应
            audio_mood = self._parse_audio_mood(response.analysis_text)
            
            logger.info(
                "Audio mood analysis completed",
                extra={
                    "tempo": audio_mood.tempo,
                    "mood": audio_mood.mood,
                    "genre": audio_mood.genre
                }
            )
            
            return audio_mood
            
        except Exception as e:
            logger.error(f"Failed to analyze audio mood: {e}")
            return AudioMood()
    
    def _parse_audio_mood(self, analysis_text: str) -> AudioMood:
        """
        解析音频情绪分析结果
        
        Args:
            analysis_text: API 返回的分析文本
        
        Returns:
            AudioMood: 解析后的音频情绪
        """
        try:
            # 提取 JSON
            if "```json" in analysis_text:
                json_start = analysis_text.find("```json") + 7
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "```" in analysis_text:
                json_start = analysis_text.find("```") + 3
                json_end = analysis_text.find("```", json_start)
                json_str = analysis_text[json_start:json_end].strip()
            elif "{" in analysis_text and "}" in analysis_text:
                json_start = analysis_text.find("{")
                json_end = analysis_text.rfind("}") + 1
                json_str = analysis_text[json_start:json_end]
            else:
                raise ValueError("No JSON found in response")
            
            data = json.loads(json_str)
            
            return AudioMood(
                tempo=data.get("tempo", "medium"),
                energy=data.get("energy", "medium"),
                mood=data.get("mood", "neutral"),
                genre=data.get("genre"),
                instruments=data.get("instruments", [])
            )
            
        except Exception as e:
            logger.warning(f"Failed to parse audio mood JSON: {e}")
            return AudioMood()

    
    async def synthesize_analysis(
        self,
        text_analysis: Optional[TextAnalysis],
        visual_style: Optional[VisualStyle],
        motion_style: Optional[MotionStyle],
        audio_mood: Optional[AudioMood]
    ) -> SynthesizedAnalysis:
        """
        综合所有分析结果
        
        Args:
            text_analysis: 文本分析结果
            visual_style: 视觉风格分析结果
            motion_style: 运动风格分析结果
            audio_mood: 音频情绪分析结果
        
        Returns:
            SynthesizedAnalysis: 综合分析结果
        """
        logger.info("Synthesizing multimodal analysis results")
        
        # 计算各组件的置信度分数
        confidence_scores = {}
        
        if text_analysis:
            # 基于文本分析的完整性计算置信度
            text_confidence = self._calculate_text_confidence(text_analysis)
            confidence_scores["text"] = text_confidence
        
        if visual_style:
            # 基于视觉风格的完整性计算置信度
            visual_confidence = self._calculate_visual_confidence(visual_style)
            confidence_scores["visual"] = visual_confidence
        
        if motion_style:
            # 基于运动风格的完整性计算置信度
            motion_confidence = self._calculate_motion_confidence(motion_style)
            confidence_scores["motion"] = motion_confidence
        
        if audio_mood:
            # 基于音频情绪的完整性计算置信度
            audio_confidence = self._calculate_audio_confidence(audio_mood)
            confidence_scores["audio"] = audio_confidence
        
        # 确定整体主题
        overall_theme = self._determine_overall_theme(
            text_analysis, visual_style, motion_style, audio_mood
        )
        
        # 创建综合分析结果
        synthesized = SynthesizedAnalysis(
            text_analysis=text_analysis,
            visual_style=visual_style,
            motion_style=motion_style,
            audio_mood=audio_mood,
            overall_theme=overall_theme,
            confidence_scores=confidence_scores,
            processing_metadata={
                "has_text": text_analysis is not None,
                "has_visual": visual_style is not None,
                "has_motion": motion_style is not None,
                "has_audio": audio_mood is not None,
                "modality_count": sum([
                    text_analysis is not None,
                    visual_style is not None,
                    motion_style is not None,
                    audio_mood is not None
                ])
            }
        )
        
        logger.info(
            "Analysis synthesis completed",
            extra={
                "overall_theme": overall_theme,
                "confidence_scores": confidence_scores,
                "modality_count": synthesized.processing_metadata["modality_count"]
            }
        )
        
        return synthesized
    
    def _calculate_text_confidence(self, text_analysis: TextAnalysis) -> float:
        """
        计算文本分析的置信度
        
        Args:
            text_analysis: 文本分析结果
        
        Returns:
            float: 置信度分数 (0-1)
        """
        score = 0.0
        
        # 主题存在且有意义
        if text_analysis.main_theme and len(text_analysis.main_theme) > 5:
            score += 0.3
        
        # 有角色信息
        if text_analysis.characters:
            score += 0.2
        
        # 有场景信息
        if text_analysis.scenes:
            score += 0.2
        
        # 有情绪标签
        if text_analysis.mood_tags:
            score += 0.15
        
        # 有合理的时长估算
        if 5 <= text_analysis.estimated_duration <= 600:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_visual_confidence(self, visual_style: VisualStyle) -> float:
        """
        计算视觉风格的置信度
        
        Args:
            visual_style: 视觉风格分析结果
        
        Returns:
            float: 置信度分数 (0-1)
        """
        score = 0.0
        
        # 有色彩调色板
        if visual_style.color_palette:
            score += 0.3
        
        # 有光照风格
        if visual_style.lighting_style != "natural":
            score += 0.2
        
        # 有艺术风格
        if visual_style.art_style != "realistic":
            score += 0.2
        
        # 有参考风格
        if visual_style.reference_styles:
            score += 0.15
        
        # 有情绪描述
        if visual_style.mood_descriptors:
            score += 0.15
        
        return min(score, 1.0)
    
    def _calculate_motion_confidence(self, motion_style: MotionStyle) -> float:
        """
        计算运动风格的置信度
        
        Args:
            motion_style: 运动风格分析结果
        
        Returns:
            float: 置信度分数 (0-1)
        """
        score = 0.0
        
        # 有镜头运动信息
        if motion_style.camera_movement != "static":
            score += 0.3
        
        # 有节奏信息
        if motion_style.pace != "medium":
            score += 0.25
        
        # 有转场风格
        if motion_style.transition_style != "cut":
            score += 0.25
        
        # 有能量级别
        if motion_style.energy_level != "medium":
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_audio_confidence(self, audio_mood: AudioMood) -> float:
        """
        计算音频情绪的置信度
        
        Args:
            audio_mood: 音频情绪分析结果
        
        Returns:
            float: 置信度分数 (0-1)
        """
        score = 0.0
        
        # 有节奏信息
        if audio_mood.tempo != "medium":
            score += 0.25
        
        # 有能量信息
        if audio_mood.energy != "medium":
            score += 0.25
        
        # 有情绪信息
        if audio_mood.mood != "neutral":
            score += 0.25
        
        # 有类型信息
        if audio_mood.genre:
            score += 0.15
        
        # 有乐器信息
        if audio_mood.instruments:
            score += 0.1
        
        return min(score, 1.0)
    
    def _determine_overall_theme(
        self,
        text_analysis: Optional[TextAnalysis],
        visual_style: Optional[VisualStyle],
        motion_style: Optional[MotionStyle],
        audio_mood: Optional[AudioMood]
    ) -> str:
        """
        确定整体主题
        
        综合各模态的分析结果，确定视频的整体主题
        
        Args:
            text_analysis: 文本分析结果
            visual_style: 视觉风格分析结果
            motion_style: 运动风格分析结果
            audio_mood: 音频情绪分析结果
        
        Returns:
            str: 整体主题描述
        """
        theme_parts = []
        
        # 从文本分析提取主题
        if text_analysis and text_analysis.main_theme:
            theme_parts.append(text_analysis.main_theme)
        
        # 从视觉风格提取风格描述
        if visual_style:
            if visual_style.art_style and visual_style.art_style != "realistic":
                theme_parts.append(f"{visual_style.art_style}风格")
            if visual_style.mood_descriptors:
                theme_parts.append(visual_style.mood_descriptors[0])
        
        # 从运动风格提取节奏描述
        if motion_style and motion_style.pace != "medium":
            pace_desc = {
                "slow": "慢节奏",
                "fast": "快节奏"
            }.get(motion_style.pace, "")
            if pace_desc:
                theme_parts.append(pace_desc)
        
        # 从音频情绪提取情绪描述
        if audio_mood and audio_mood.mood != "neutral":
            theme_parts.append(f"{audio_mood.mood}氛围")
        
        # 组合主题
        if theme_parts:
            return "、".join(theme_parts[:3])  # 最多取3个部分
        else:
            return "视频创作"
    
    async def analyze_all(
        self,
        text: Optional[ProcessedText],
        images: List[ProcessedImage],
        videos: List[ProcessedVideo],
        audio: List[ProcessedAudio]
    ) -> SynthesizedAnalysis:
        """
        分析所有模态的输入数据
        
        这是一个便捷方法，依次调用各个分析方法并综合结果
        
        Args:
            text: 处理后的文本数据
            images: 处理后的图片数据列表
            videos: 处理后的视频数据列表
            audio: 处理后的音频数据列表
        
        Returns:
            SynthesizedAnalysis: 综合分析结果
        """
        logger.info(
            "Starting comprehensive multimodal analysis",
            extra={
                "has_text": text is not None,
                "images_count": len(images),
                "videos_count": len(videos),
                "audio_count": len(audio)
            }
        )
        
        # 分析文本
        text_analysis = None
        if text:
            text_analysis = await self.analyze_text_intent(text)
        
        # 分析视觉风格
        visual_style = None
        if images:
            visual_style = await self.analyze_visual_style(images)
        
        # 分析运动风格
        motion_style = None
        if videos:
            motion_style = await self.analyze_motion_style(videos)
        
        # 分析音频情绪
        audio_mood = None
        if audio:
            audio_mood = await self.analyze_audio_mood(audio)
        
        # 综合分析结果
        synthesized = await self.synthesize_analysis(
            text_analysis=text_analysis,
            visual_style=visual_style,
            motion_style=motion_style,
            audio_mood=audio_mood
        )
        
        logger.info("Comprehensive multimodal analysis completed")
        
        return synthesized
