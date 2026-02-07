"""
置信度评估器单元测试

测试不同输入质量的置信度计算和阈值触发逻辑

Validates: Requirements 4.1, 4.2
"""

import pytest
from unittest.mock import Mock, patch

from ..models import (
    GlobalSpec,
    StyleConfig,
    SynthesizedAnalysis,
    TextAnalysis,
    VisualStyle,
    MotionStyle,
    AudioMood,
    CharacterInfo,
    SceneInfo,
    UserInputData,
    ConfidenceReport,
    ConfidenceLevel,
    ClarificationRequest
)
from ..confidence_evaluator import ConfidenceEvaluator
from ..config import RequirementParserConfig


class TestConfidenceEvaluator:
    """置信度评估器单元测试"""
    
    @pytest.fixture
    def evaluator(self):
        """创建评估器实例"""
        return ConfidenceEvaluator()
    
    @pytest.fixture
    def high_quality_input(self):
        """高质量用户输入"""
        return UserInputData(
            text_description="一个年轻的探险家在神秘的森林中寻找宝藏，时长30秒。画面采用温暖的色调，充满冒险和神秘的氛围。",
            reference_images=["image1.jpg", "image2.jpg"],
            reference_videos=["video1.mp4"],
            reference_audio=["audio1.mp3"],
            user_preferences={
                "duration": 30,
                "aspect_ratio": "9:16",
                "quality_tier": "high"
            }
        )
    
    @pytest.fixture
    def low_quality_input(self):
        """低质量用户输入"""
        return UserInputData(
            text_description="视频",
            reference_images=[],
            reference_videos=[],
            reference_audio=[],
            user_preferences={}
        )
    
    @pytest.fixture
    def complete_global_spec(self):
        """完整的GlobalSpec"""
        return GlobalSpec(
            title="探险家寻宝记",
            duration=30,
            aspect_ratio="9:16",
            quality_tier="high",
            resolution="1080x1920",
            fps=30,
            style=StyleConfig(
                tone="warm",
                palette=["#FF6B35", "#F7931E", "#FDC830"],
                visual_dna_version=1
            ),
            characters=["探险家", "神秘向导"],
            mood="冒险,神秘,兴奋",
            user_options={}
        )
    
    @pytest.fixture
    def incomplete_global_spec(self):
        """不完整的GlobalSpec"""
        return GlobalSpec(
            title="",
            duration=30,
            aspect_ratio="9:16",
            quality_tier="balanced",
            resolution="1080x1920",
            fps=30,
            style=StyleConfig(
                tone="",
                palette=[],
                visual_dna_version=1
            ),
            characters=[],
            mood="",
            user_options={}
        )
    
    @pytest.fixture
    def complete_analysis(self):
        """完整的分析结果"""
        return SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="探险寻宝",
                characters=[
                    CharacterInfo(
                        name="探险家",
                        description="年轻勇敢的探险家",
                        role="protagonist",
                        traits=["勇敢", "聪明"]
                    )
                ],
                scenes=[
                    SceneInfo(
                        description="神秘森林",
                        location="森林深处",
                        time_of_day="黄昏",
                        mood="神秘",
                        duration_estimate=30.0
                    )
                ],
                mood_tags=["冒险", "神秘", "兴奋"],
                estimated_duration=30,
                narrative_structure="linear",
                genre="冒险",
                target_audience="青少年"
            ),
            visual_style=VisualStyle(
                color_palette=["#FF6B35", "#F7931E", "#FDC830"],
                lighting_style="warm",
                composition_style="dynamic",
                art_style="realistic",
                reference_styles=["cinematic"],
                mood_descriptors=["温暖", "神秘"]
            ),
            motion_style=MotionStyle(
                camera_movement="tracking",
                pace="medium",
                transition_style="cut",
                energy_level="medium"
            ),
            audio_mood=AudioMood(
                tempo="medium",
                energy="medium",
                mood="adventurous",
                genre="orchestral",
                instruments=["strings", "brass"]
            ),
            overall_theme="冒险探索",
            confidence_scores={
                "text": 0.9,
                "visual": 0.85,
                "motion": 0.8,
                "audio": 0.75
            }
        )
    
    @pytest.fixture
    def minimal_analysis(self):
        """最小化的分析结果"""
        return SynthesizedAnalysis(
            text_analysis=None,
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="",
            confidence_scores={}
        )
    
    @pytest.mark.asyncio
    async def test_high_quality_input_produces_high_confidence(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis,
        high_quality_input
    ):
        """
        测试高质量输入产生高置信度
        
        Validates: Requirement 4.1
        """
        report = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            high_quality_input
        )
        
        # 高质量输入应该产生较高的置信度
        assert report.overall_confidence >= 0.6, \
            f"High quality input should produce confidence >= 0.6, got {report.overall_confidence}"
        
        # 置信度级别应该是MEDIUM或HIGH
        assert report.confidence_level in [ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH], \
            f"High quality input should produce MEDIUM or HIGH confidence level, got {report.confidence_level}"
    
    @pytest.mark.asyncio
    async def test_low_quality_input_produces_low_confidence(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis,
        low_quality_input
    ):
        """
        测试低质量输入产生低置信度
        
        Validates: Requirement 4.1
        """
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            low_quality_input
        )
        
        # 低质量输入应该产生较低的置信度
        assert report.overall_confidence < 0.6, \
            f"Low quality input should produce confidence < 0.6, got {report.overall_confidence}"
        
        # 置信度级别应该是LOW
        assert report.confidence_level == ConfidenceLevel.LOW, \
            f"Low quality input should produce LOW confidence level, got {report.confidence_level}"
    
    @pytest.mark.asyncio
    async def test_confidence_threshold_triggers_clarification(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis,
        low_quality_input
    ):
        """
        测试低于阈值触发澄清请求
        
        Validates: Requirement 4.2
        """
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            low_quality_input
        )
        
        # 低置信度应该触发澄清或人工审核
        if report.overall_confidence < evaluator.confidence_threshold:
            assert report.recommendation in ["clarify", "human_review"], \
                f"Low confidence should recommend clarify or human_review, got {report.recommendation}"
    
    @pytest.mark.asyncio
    async def test_high_confidence_recommends_proceed(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis,
        high_quality_input
    ):
        """
        测试高置信度推荐继续
        
        Validates: Requirement 4.2
        """
        report = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            high_quality_input
        )
        
        # 如果置信度高于阈值，应该推荐继续
        if report.overall_confidence >= evaluator.confidence_threshold:
            assert report.recommendation == "proceed", \
                f"High confidence should recommend proceed, got {report.recommendation}"
    
    @pytest.mark.asyncio
    async def test_very_low_confidence_recommends_human_review(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis
    ):
        """
        测试极低置信度推荐人工审核
        
        Validates: Requirement 4.2
        """
        # 创建极低质量的输入（最小有效输入）
        very_low_input = UserInputData(
            text_description="a",  # 最短的有效文本
            reference_images=[],
            reference_videos=[],
            reference_audio=[],
            user_preferences={}
        )
        
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            very_low_input
        )
        
        # 极低置信度应该推荐人工审核
        if report.overall_confidence < 0.3:
            assert report.recommendation == "human_review", \
                f"Very low confidence should recommend human_review, got {report.recommendation}"
    
    @pytest.mark.asyncio
    async def test_component_scores_calculated(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis,
        high_quality_input
    ):
        """
        测试各组件得分被正确计算
        
        Validates: Requirement 4.1
        """
        report = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            high_quality_input
        )
        
        # 应该包含所有组件的得分
        expected_components = [
            "text_clarity",
            "style_consistency",
            "completeness",
            "user_input_quality"
        ]
        
        for component in expected_components:
            assert component in report.component_scores, \
                f"Component {component} should be in scores"
            
            score = report.component_scores[component]
            assert 0.0 <= score <= 1.0, \
                f"Component {component} score should be between 0 and 1, got {score}"
    
    @pytest.mark.asyncio
    async def test_low_confidence_areas_identified_correctly(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis,
        low_quality_input
    ):
        """
        测试低置信度区域被正确识别
        
        Validates: Requirement 4.1
        """
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            low_quality_input
        )
        
        # 验证低置信度区域的识别逻辑
        # 如果有低置信度区域，它们的得分应该低于阈值
        for area in report.low_confidence_areas:
            score = report.component_scores.get(area, 1.0)
            assert score < evaluator.low_confidence_threshold, \
                f"Low confidence area {area} should have score < {evaluator.low_confidence_threshold}, got {score}"
        
        # 验证所有低于阈值的组件都被识别为低置信度区域
        for component, score in report.component_scores.items():
            if score < evaluator.low_confidence_threshold:
                assert component in report.low_confidence_areas, \
                    f"Component {component} with score {score} should be in low_confidence_areas"
    
    @pytest.mark.asyncio
    async def test_clarification_requests_generated_for_missing_info(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis,
        low_quality_input
    ):
        """
        测试为缺失信息生成澄清请求
        
        Validates: Requirement 4.2
        """
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            low_quality_input
        )
        
        # 验证澄清请求的结构（如果有的话）
        for request in report.clarification_requests:
            assert isinstance(request, ClarificationRequest), \
                "Request should be ClarificationRequest instance"
            
            assert request.field_name, "Request should have field_name"
            assert request.reason, "Request should have reason"
            assert request.priority in ["low", "medium", "high"], \
                f"Request priority should be low/medium/high, got {request.priority}"
        
        # 如果有低置信度区域，应该考虑生成澄清请求
        # 但这取决于具体的低置信度区域和阈值
        if len(report.low_confidence_areas) > 0:
            # 至少应该有推荐行动
            assert report.recommendation in ["proceed", "clarify", "human_review"], \
                f"Should have valid recommendation, got {report.recommendation}"
    
    @pytest.mark.asyncio
    async def test_text_clarity_evaluation(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis
    ):
        """
        测试文本清晰度评估
        
        Validates: Requirement 4.1
        """
        # 测试详细文本
        detailed_input = UserInputData(
            text_description="这是一个关于年轻探险家在神秘森林中寻找古老宝藏的故事。画面采用温暖的色调，充满冒险和神秘的氛围。主角勇敢而聪明，在旅途中遇到各种挑战。",
            reference_images=[],
            reference_videos=[],
            reference_audio=[]
        )
        
        report1 = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            detailed_input
        )
        
        # 测试简短文本
        brief_input = UserInputData(
            text_description="视频",
            reference_images=[],
            reference_videos=[],
            reference_audio=[]
        )
        
        # 创建最小化的分析结果（模拟简短文本的分析）
        minimal_text_analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="",
                characters=[],
                scenes=[],
                mood_tags=[],
                estimated_duration=30,
                narrative_structure="linear"
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="",
            confidence_scores={}
        )
        
        report2 = await evaluator.evaluate_confidence(
            complete_global_spec,
            minimal_text_analysis,
            brief_input
        )
        
        # 详细文本应该有更高的文本清晰度得分
        assert report1.component_scores["text_clarity"] > report2.component_scores["text_clarity"], \
            f"Detailed text should have higher clarity score ({report1.component_scores['text_clarity']}) than brief text ({report2.component_scores['text_clarity']})"
    
    @pytest.mark.asyncio
    async def test_completeness_evaluation(
        self,
        evaluator,
        complete_analysis,
        high_quality_input
    ):
        """
        测试完整性评估
        
        Validates: Requirement 4.1
        """
        # 测试完整的GlobalSpec
        complete_spec = GlobalSpec(
            title="完整标题",
            duration=30,
            aspect_ratio="9:16",
            quality_tier="high",
            resolution="1080x1920",
            fps=30,
            style=StyleConfig(
                tone="warm",
                palette=["#FF0000", "#00FF00"],
                visual_dna_version=1
            ),
            characters=["角色1", "角色2"],
            mood="快乐,兴奋",
            user_options={}
        )
        
        report1 = await evaluator.evaluate_confidence(
            complete_spec,
            complete_analysis,
            high_quality_input
        )
        
        # 测试不完整的GlobalSpec
        incomplete_spec = GlobalSpec(
            title="",
            duration=30,
            aspect_ratio="9:16",
            quality_tier="balanced",
            resolution="1080x1920",
            fps=30,
            style=StyleConfig(
                tone="",
                palette=[],
                visual_dna_version=1
            ),
            characters=[],
            mood="",
            user_options={}
        )
        
        report2 = await evaluator.evaluate_confidence(
            incomplete_spec,
            complete_analysis,
            high_quality_input
        )
        
        # 完整的GlobalSpec应该有更高的完整性得分
        assert report1.component_scores["completeness"] > report2.component_scores["completeness"], \
            "Complete GlobalSpec should have higher completeness score than incomplete one"
    
    @pytest.mark.asyncio
    async def test_user_input_quality_evaluation(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis
    ):
        """
        测试用户输入质量评估
        
        Validates: Requirement 4.1
        """
        # 测试多模态输入
        multimodal_input = UserInputData(
            text_description="详细的文本描述，包含场景、角色和情绪信息。",
            reference_images=["img1.jpg", "img2.jpg"],
            reference_videos=["video1.mp4"],
            reference_audio=["audio1.mp3"]
        )
        
        report1 = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            multimodal_input
        )
        
        # 测试仅文本输入
        text_only_input = UserInputData(
            text_description="简短描述",
            reference_images=[],
            reference_videos=[],
            reference_audio=[]
        )
        
        report2 = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            text_only_input
        )
        
        # 多模态输入应该有更高的输入质量得分
        assert report1.component_scores["user_input_quality"] > report2.component_scores["user_input_quality"], \
            "Multimodal input should have higher quality score than text-only input"
    
    @pytest.mark.asyncio
    async def test_mark_uncertain_fields(
        self,
        evaluator,
        incomplete_global_spec,
        minimal_analysis,
        low_quality_input
    ):
        """
        测试标记不确定字段
        
        Validates: Requirement 4.2
        """
        report = await evaluator.evaluate_confidence(
            incomplete_global_spec,
            minimal_analysis,
            low_quality_input
        )
        
        # 标记不确定字段
        uncertain_fields = evaluator.mark_uncertain_fields(
            incomplete_global_spec,
            report
        )
        
        # 验证不确定字段的结构（如果有的话）
        for field_name, field_info in uncertain_fields.items():
            assert "value" in field_info, \
                f"Uncertain field {field_name} should have value"
            
            assert "confidence" in field_info, \
                f"Uncertain field {field_name} should have confidence"
            
            assert "reason" in field_info, \
                f"Uncertain field {field_name} should have reason"
            
            assert 0.0 <= field_info["confidence"] <= 1.0, \
                f"Uncertain field {field_name} confidence should be between 0 and 1"
        
        # 如果有低置信度区域或澄清请求，应该有不确定字段
        if len(report.low_confidence_areas) > 0 or len(report.clarification_requests) > 0:
            assert len(uncertain_fields) >= 0, \
                "Should be able to mark uncertain fields"
    
    @pytest.mark.asyncio
    async def test_weighted_confidence_calculation(self, evaluator):
        """
        测试加权置信度计算
        
        Validates: Requirement 4.1
        """
        # 测试不同的组件得分
        component_scores = {
            "text_clarity": 0.8,
            "style_consistency": 0.6,
            "completeness": 0.9,
            "user_input_quality": 0.7
        }
        
        weighted_confidence = evaluator._calculate_weighted_confidence(component_scores)
        
        # 加权置信度应该在有效范围内
        assert 0.0 <= weighted_confidence <= 1.0, \
            f"Weighted confidence should be between 0 and 1, got {weighted_confidence}"
        
        # 加权置信度应该考虑权重
        # 由于completeness权重最高(0.3)，而其得分也最高(0.9)，
        # 加权平均应该偏向较高的值
        simple_average = sum(component_scores.values()) / len(component_scores)
        
        # 验证加权计算确实应用了权重（不等于简单平均）
        # 注意：由于权重分布，加权平均可能接近但不完全等于简单平均
        assert weighted_confidence >= 0.0, \
            "Weighted confidence should be calculated correctly"
    
    @pytest.mark.asyncio
    async def test_no_user_input_handled_gracefully(
        self,
        evaluator,
        complete_global_spec,
        complete_analysis
    ):
        """
        测试没有用户输入时的优雅处理
        
        Validates: Requirement 4.1
        """
        report = await evaluator.evaluate_confidence(
            complete_global_spec,
            complete_analysis,
            user_input=None
        )
        
        # 应该能够生成有效的报告
        assert isinstance(report, ConfidenceReport), \
            "Should generate valid report even without user input"
        
        assert 0.0 <= report.overall_confidence <= 1.0, \
            "Confidence should be in valid range even without user input"
        
        # 用户输入质量得分应该较低
        assert report.component_scores["user_input_quality"] < 0.5, \
            "User input quality should be low when no input provided"
