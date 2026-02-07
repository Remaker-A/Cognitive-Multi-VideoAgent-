"""
置信度评估器 (ConfidenceEvaluator)

负责评估GlobalSpec生成结果的置信度，决定是否需要人工介入。
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .models import (
    GlobalSpec,
    SynthesizedAnalysis,
    UserInputData,
    ConfidenceReport,
    ClarificationRequest,
    ConfidenceLevel,
    TextAnalysis,
    VisualStyle,
    MotionStyle,
    AudioMood
)
from .config import RequirementParserConfig

logger = logging.getLogger(__name__)


class ConfidenceEvaluator:
    """
    置信度评估器
    
    评估生成结果的可信度，决定是否需要人工介入。
    
    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    def __init__(self, config: Optional[RequirementParserConfig] = None):
        """
        初始化置信度评估器
        
        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        from .config import config as default_config
        self.config = config or default_config
        
        # 置信度阈值
        self.confidence_threshold = self.config.confidence_threshold
        
        # 各组件的权重
        self.component_weights = {
            "text_clarity": 0.25,
            "style_consistency": 0.20,
            "completeness": 0.30,
            "user_input_quality": 0.25
        }
        
        # 低置信度阈值（触发澄清请求）
        self.low_confidence_threshold = 0.4
    
    async def evaluate_confidence(
        self,
        global_spec: GlobalSpec,
        analysis: SynthesizedAnalysis,
        user_input: Optional[UserInputData] = None
    ) -> ConfidenceReport:
        """
        评估整体置信度
        
        Args:
            global_spec: 生成的GlobalSpec
            analysis: 综合分析结果
            user_input: 用户输入数据
            
        Returns:
            置信度报告
            
        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        """
        logger.info("Starting confidence evaluation")
        
        # 计算各组件的置信度
        component_scores = {}
        
        # 1. 文本清晰度评估
        text_clarity_score = self._evaluate_text_clarity(user_input, analysis)
        component_scores["text_clarity"] = text_clarity_score
        
        # 2. 风格一致性评估
        style_consistency_score = self._evaluate_style_consistency(global_spec, analysis)
        component_scores["style_consistency"] = style_consistency_score
        
        # 3. 信息完整性评估
        completeness_score = self._evaluate_completeness(global_spec, analysis)
        component_scores["completeness"] = completeness_score
        
        # 4. 用户输入质量评估
        input_quality_score = self._evaluate_user_input_quality(user_input)
        component_scores["user_input_quality"] = input_quality_score
        
        # 计算加权总体置信度 (Requirement 4.1)
        overall_confidence = self._calculate_weighted_confidence(component_scores)
        
        # 识别低置信度区域
        low_confidence_areas = self._identify_low_confidence_areas(component_scores)
        
        # 生成澄清请求 (Requirement 4.4)
        clarification_requests = self._generate_clarification_requests(
            global_spec,
            analysis,
            user_input,
            component_scores,
            low_confidence_areas
        )
        
        # 确定推荐行动 (Requirement 4.2)
        recommendation = self._determine_recommendation(
            overall_confidence,
            clarification_requests
        )
        
        # 创建置信度报告
        report = ConfidenceReport(
            overall_confidence=overall_confidence,
            component_scores=component_scores,
            low_confidence_areas=low_confidence_areas,
            clarification_requests=clarification_requests,
            recommendation=recommendation
        )
        
        logger.info(
            f"Confidence evaluation completed: {overall_confidence:.2f} ({report.confidence_level.value})",
            extra={
                "overall_confidence": overall_confidence,
                "confidence_level": report.confidence_level.value,
                "recommendation": recommendation,
                "component_scores": component_scores
            }
        )
        
        return report
    
    def _evaluate_text_clarity(
        self,
        user_input: Optional[UserInputData],
        analysis: SynthesizedAnalysis
    ) -> float:
        """
        评估文本描述的清晰度
        
        Args:
            user_input: 用户输入
            analysis: 分析结果
            
        Returns:
            清晰度得分 (0-1)
        """
        if not user_input or not user_input.text_description:
            return 0.3  # 没有文本输入，给予较低分数
        
        text = user_input.text_description.strip()
        score = 0.5  # 基础分数
        
        # 文本长度评估
        word_count = len(text.split())
        if word_count >= 10:
            score += 0.2
        elif word_count >= 5:
            score += 0.1
        
        # 检查是否包含关键信息
        if analysis and analysis.text_analysis:
            text_analysis = analysis.text_analysis
            
            # 有明确主题
            if text_analysis.main_theme and len(text_analysis.main_theme) > 0:
                score += 0.1
            
            # 有角色信息
            if text_analysis.characters and len(text_analysis.characters) > 0:
                score += 0.1
            
            # 有场景信息
            if text_analysis.scenes and len(text_analysis.scenes) > 0:
                score += 0.1
        
        return min(1.0, score)
    
    def _evaluate_style_consistency(
        self,
        global_spec: GlobalSpec,
        analysis: SynthesizedAnalysis
    ) -> float:
        """
        评估风格一致性
        
        Args:
            global_spec: GlobalSpec
            analysis: 分析结果
            
        Returns:
            一致性得分 (0-1)
        """
        score = 0.5  # 基础分数
        
        # 检查风格配置的完整性
        if global_spec.style:
            # 有色调定义
            if global_spec.style.tone and len(global_spec.style.tone) > 0:
                score += 0.15
            
            # 有调色板
            if global_spec.style.palette and len(global_spec.style.palette) > 0:
                score += 0.15
            
            # 调色板颜色数量合理
            if global_spec.style.palette and 2 <= len(global_spec.style.palette) <= 10:
                score += 0.1
        
        # 检查分析结果的一致性
        if analysis:
            consistency_count = 0
            total_checks = 0
            
            # 视觉风格与音频情绪的一致性
            if analysis.visual_style and analysis.audio_mood:
                total_checks += 1
                # 简单的一致性检查：能量级别匹配
                if hasattr(analysis.audio_mood, 'energy'):
                    consistency_count += 0.5
            
            # 运动风格与音频节奏的一致性
            if analysis.motion_style and analysis.audio_mood:
                total_checks += 1
                if hasattr(analysis.motion_style, 'pace') and hasattr(analysis.audio_mood, 'tempo'):
                    consistency_count += 0.5
            
            if total_checks > 0:
                score += 0.1 * (consistency_count / total_checks)
        
        return min(1.0, score)
    
    def _evaluate_completeness(
        self,
        global_spec: GlobalSpec,
        analysis: SynthesizedAnalysis
    ) -> float:
        """
        评估信息完整性
        
        Args:
            global_spec: GlobalSpec
            analysis: 分析结果
            
        Returns:
            完整性得分 (0-1)
        """
        score = 0.0
        total_fields = 10  # 总共需要检查的字段数
        complete_fields = 0
        
        # 检查GlobalSpec的必需字段
        if global_spec.title and len(global_spec.title) > 0:
            complete_fields += 1
        
        if global_spec.duration and global_spec.duration > 0:
            complete_fields += 1
        
        if global_spec.aspect_ratio and global_spec.aspect_ratio in ["9:16", "16:9", "1:1", "4:3"]:
            complete_fields += 1
        
        if global_spec.quality_tier and global_spec.quality_tier in ["high", "balanced", "fast"]:
            complete_fields += 1
        
        if global_spec.resolution and "x" in global_spec.resolution:
            complete_fields += 1
        
        if global_spec.fps and global_spec.fps in [24, 30, 60]:
            complete_fields += 1
        
        if global_spec.style and global_spec.style.tone and len(global_spec.style.tone) > 0:
            complete_fields += 1
        
        if global_spec.style and global_spec.style.palette and len(global_spec.style.palette) > 0:
            complete_fields += 1
        
        if global_spec.characters is not None:  # 可以为空列表
            complete_fields += 1
        
        if global_spec.mood and len(global_spec.mood) > 0:
            complete_fields += 1
        
        # 计算完整性得分
        score = complete_fields / total_fields
        
        return score
    
    def _evaluate_user_input_quality(
        self,
        user_input: Optional[UserInputData]
    ) -> float:
        """
        评估用户输入质量
        
        Args:
            user_input: 用户输入
            
        Returns:
            质量得分 (0-1)
        """
        if not user_input:
            return 0.3  # 没有用户输入，给予较低分数
        
        score = 0.3  # 基础分数
        
        # 有文本描述
        if user_input.text_description and len(user_input.text_description.strip()) > 0:
            score += 0.3
            
            # 文本描述足够详细
            word_count = len(user_input.text_description.split())
            if word_count >= 20:
                score += 0.1
        
        # 有参考图片
        if user_input.reference_images and len(user_input.reference_images) > 0:
            score += 0.1
        
        # 有参考视频
        if user_input.reference_videos and len(user_input.reference_videos) > 0:
            score += 0.1
        
        # 有参考音频
        if user_input.reference_audio and len(user_input.reference_audio) > 0:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_weighted_confidence(
        self,
        component_scores: Dict[str, float]
    ) -> float:
        """
        计算加权置信度
        
        Args:
            component_scores: 各组件得分
            
        Returns:
            加权置信度 (0-1)
        """
        total_weight = 0.0
        weighted_sum = 0.0
        
        for component, score in component_scores.items():
            weight = self.component_weights.get(component, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        return weighted_sum / total_weight
    
    def _identify_low_confidence_areas(
        self,
        component_scores: Dict[str, float]
    ) -> List[str]:
        """
        识别低置信度区域
        
        Args:
            component_scores: 各组件得分
            
        Returns:
            低置信度区域列表
        """
        low_areas = []
        
        for component, score in component_scores.items():
            if score < self.low_confidence_threshold:
                low_areas.append(component)
        
        return low_areas
    
    def _generate_clarification_requests(
        self,
        global_spec: GlobalSpec,
        analysis: SynthesizedAnalysis,
        user_input: Optional[UserInputData],
        component_scores: Dict[str, float],
        low_confidence_areas: List[str]
    ) -> List[ClarificationRequest]:
        """
        生成澄清请求
        
        Args:
            global_spec: GlobalSpec
            analysis: 分析结果
            user_input: 用户输入
            component_scores: 组件得分
            low_confidence_areas: 低置信度区域
            
        Returns:
            澄清请求列表
            
        Validates: Requirement 4.4
        """
        requests = []
        
        # 文本清晰度低
        if "text_clarity" in low_confidence_areas:
            if not user_input or not user_input.text_description or len(user_input.text_description.strip()) < 10:
                requests.append(ClarificationRequest(
                    field_name="text_description",
                    current_value=user_input.text_description if user_input else "",
                    reason="文本描述过于简短或缺失，无法充分理解需求",
                    suggestions=[
                        "请提供更详细的场景描述",
                        "说明视频的主要内容和目标",
                        "描述期望的视觉风格和情绪"
                    ],
                    priority="high"
                ))
        
        # 风格一致性低
        if "style_consistency" in low_confidence_areas:
            if not global_spec.style or not global_spec.style.palette or len(global_spec.style.palette) == 0:
                requests.append(ClarificationRequest(
                    field_name="style",
                    current_value=global_spec.style.to_dict() if global_spec.style else {},
                    reason="无法确定明确的视觉风格",
                    suggestions=[
                        "提供参考图片以明确视觉风格",
                        "描述期望的色调和氛围",
                        "指定艺术风格（如：写实、卡通、复古等）"
                    ],
                    priority="medium"
                ))
        
        # 完整性低
        if "completeness" in low_confidence_areas:
            # 检查缺失的关键字段
            if not global_spec.characters or len(global_spec.characters) == 0:
                requests.append(ClarificationRequest(
                    field_name="characters",
                    current_value=global_spec.characters,
                    reason="未能识别出角色信息",
                    suggestions=[
                        "明确说明视频中的角色",
                        "描述角色的外观和特征",
                        "说明角色之间的关系"
                    ],
                    priority="medium"
                ))
            
            if not global_spec.mood or len(global_spec.mood) == 0:
                requests.append(ClarificationRequest(
                    field_name="mood",
                    current_value=global_spec.mood,
                    reason="未能确定视频的整体情绪",
                    suggestions=[
                        "描述期望的情绪氛围（如：欢快、温馨、紧张等）",
                        "提供参考音乐以明确情绪基调"
                    ],
                    priority="low"
                ))
        
        # 用户输入质量低
        if "user_input_quality" in low_confidence_areas:
            if not user_input or (
                not user_input.text_description and
                not user_input.reference_images and
                not user_input.reference_videos and
                not user_input.reference_audio
            ):
                requests.append(ClarificationRequest(
                    field_name="user_input",
                    current_value=None,
                    reason="用户输入信息不足",
                    suggestions=[
                        "提供文本描述说明需求",
                        "上传参考图片、视频或音频",
                        "说明具体的使用场景和目标"
                    ],
                    priority="high"
                ))
        
        return requests
    
    def _determine_recommendation(
        self,
        overall_confidence: float,
        clarification_requests: List[ClarificationRequest]
    ) -> str:
        """
        确定推荐行动
        
        Args:
            overall_confidence: 总体置信度
            clarification_requests: 澄清请求列表
            
        Returns:
            推荐行动: "proceed", "clarify", "human_review"
            
        Validates: Requirement 4.2
        """
        # 置信度高于阈值，直接继续
        if overall_confidence >= self.confidence_threshold:
            return "proceed"
        
        # 置信度极低，需要人工审核
        if overall_confidence < 0.3:
            return "human_review"
        
        # 有高优先级的澄清请求，需要澄清
        high_priority_requests = [
            req for req in clarification_requests
            if req.priority == "high"
        ]
        if high_priority_requests:
            return "clarify"
        
        # 置信度中等偏低，建议澄清
        if overall_confidence < self.confidence_threshold:
            return "clarify"
        
        return "proceed"
    
    def mark_uncertain_fields(
        self,
        global_spec: GlobalSpec,
        confidence_report: ConfidenceReport
    ) -> Dict[str, Any]:
        """
        标记不确定的字段
        
        Args:
            global_spec: GlobalSpec
            confidence_report: 置信度报告
            
        Returns:
            包含不确定性标记的字典
            
        Validates: Requirement 4.5
        """
        uncertain_fields = {}
        
        # 基于低置信度区域标记字段
        for area in confidence_report.low_confidence_areas:
            if area == "text_clarity":
                uncertain_fields["title"] = {
                    "value": global_spec.title,
                    "confidence": confidence_report.component_scores.get("text_clarity", 0.0),
                    "reason": "文本描述不够清晰"
                }
            
            elif area == "style_consistency":
                uncertain_fields["style"] = {
                    "value": global_spec.style.to_dict() if global_spec.style else {},
                    "confidence": confidence_report.component_scores.get("style_consistency", 0.0),
                    "reason": "风格信息不一致或不完整"
                }
            
            elif area == "completeness":
                if not global_spec.characters or len(global_spec.characters) == 0:
                    uncertain_fields["characters"] = {
                        "value": global_spec.characters,
                        "confidence": confidence_report.component_scores.get("completeness", 0.0),
                        "reason": "角色信息缺失"
                    }
                
                if not global_spec.mood or len(global_spec.mood) == 0:
                    uncertain_fields["mood"] = {
                        "value": global_spec.mood,
                        "confidence": confidence_report.component_scores.get("completeness", 0.0),
                        "reason": "情绪信息缺失"
                    }
        
        # 基于澄清请求标记字段
        for request in confidence_report.clarification_requests:
            if request.field_name not in uncertain_fields:
                uncertain_fields[request.field_name] = {
                    "value": request.current_value,
                    "confidence": 0.0,  # 需要澄清的字段置信度为0
                    "reason": request.reason,
                    "suggestions": request.suggestions
                }
        
        return uncertain_fields
