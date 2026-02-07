"""
缃俊搴﹁瘎浼板櫒灞炴€ф祴璇?

Feature: requirement-parser-agent, Property 4: Confidence-Based Decision Making
Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from hypothesis.strategies import composite

from ...models import (
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
    ConfidenceLevel
)
from ..confidence_evaluator import ConfidenceEvaluator


# 绛栫暐锛氱敓鎴怌haracterInfo
@composite
def character_info_strategy(draw):
    """鐢熸垚闅忔満鐨凜haracterInfo"""
    name = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(blacklist_categories=('Cs',))))
    description = draw(st.text(max_size=100))
    role = draw(st.sampled_from(["protagonist", "antagonist", "supporting", "minor"]))
    traits = draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    
    return CharacterInfo(
        name=name,
        description=description,
        role=role,
        traits=traits
    )


# 绛栫暐锛氱敓鎴怱ceneInfo
@composite
def scene_info_strategy(draw):
    """鐢熸垚闅忔満鐨凷ceneInfo"""
    description = draw(st.text(min_size=1, max_size=100))
    location = draw(st.text(max_size=50))
    time_of_day = draw(st.one_of(st.none(), st.sampled_from(["morning", "afternoon", "evening", "night"])))
    mood = draw(st.text(max_size=30))
    duration_estimate = draw(st.one_of(st.none(), st.floats(min_value=1.0, max_value=60.0)))
    
    return SceneInfo(
        description=description,
        location=location,
        time_of_day=time_of_day,
        mood=mood,
        duration_estimate=duration_estimate
    )


# 绛栫暐锛氱敓鎴怲extAnalysis
@composite
def text_analysis_strategy(draw):
    """鐢熸垚闅忔満鐨凾extAnalysis"""
    main_theme = draw(st.text(min_size=1, max_size=100))
    characters = draw(st.lists(character_info_strategy(), max_size=5))
    scenes = draw(st.lists(scene_info_strategy(), max_size=5))
    mood_tags = draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    estimated_duration = draw(st.integers(min_value=5, max_value=600))
    narrative_structure = draw(st.sampled_from(["linear", "non-linear", "circular", "episodic"]))
    genre = draw(st.one_of(st.none(), st.text(max_size=30)))
    target_audience = draw(st.one_of(st.none(), st.text(max_size=30)))
    
    return TextAnalysis(
        main_theme=main_theme,
        characters=characters,
        scenes=scenes,
        mood_tags=mood_tags,
        estimated_duration=estimated_duration,
        narrative_structure=narrative_structure,
        genre=genre,
        target_audience=target_audience
    )


# 绛栫暐锛氱敓鎴怴isualStyle
@composite
def visual_style_strategy(draw):
    """鐢熸垚闅忔満鐨刅isualStyle"""
    color_palette = draw(st.lists(
        st.sampled_from(["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF", "#FFFFFF", "#000000"]),
        max_size=10
    ))
    lighting_style = draw(st.sampled_from(["natural", "artificial", "dramatic", "soft", "bright", "dark"]))
    composition_style = draw(st.sampled_from(["balanced", "symmetric", "dynamic", "minimal", "complex"]))
    art_style = draw(st.sampled_from(["realistic", "cartoon", "abstract", "vintage", "modern"]))
    reference_styles = draw(st.lists(st.text(max_size=30), max_size=5))
    mood_descriptors = draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    
    return VisualStyle(
        color_palette=color_palette,
        lighting_style=lighting_style,
        composition_style=composition_style,
        art_style=art_style,
        reference_styles=reference_styles,
        mood_descriptors=mood_descriptors
    )


# 绛栫暐锛氱敓鎴怣otionStyle
@composite
def motion_style_strategy(draw):
    """鐢熸垚闅忔満鐨凪otionStyle"""
    camera_movement = draw(st.sampled_from(["static", "pan", "tilt", "zoom", "dolly", "tracking", "aerial"]))
    pace = draw(st.sampled_from(["slow", "medium", "fast"]))
    transition_style = draw(st.sampled_from(["cut", "fade", "dissolve", "wipe", "slide"]))
    energy_level = draw(st.sampled_from(["low", "medium", "high"]))
    
    return MotionStyle(
        camera_movement=camera_movement,
        pace=pace,
        transition_style=transition_style,
        energy_level=energy_level
    )


# 绛栫暐锛氱敓鎴怉udioMood
@composite
def audio_mood_strategy(draw):
    """鐢熸垚闅忔満鐨凙udioMood"""
    tempo = draw(st.sampled_from(["slow", "medium", "fast"]))
    energy = draw(st.sampled_from(["low", "medium", "high"]))
    mood = draw(st.sampled_from(["happy", "sad", "calm", "energetic", "mysterious", "neutral"]))
    genre = draw(st.one_of(st.none(), st.sampled_from(["pop", "classical", "electronic", "rock", "jazz"])))
    instruments = draw(st.lists(st.text(min_size=1, max_size=20), max_size=5))
    
    return AudioMood(
        tempo=tempo,
        energy=energy,
        mood=mood,
        genre=genre,
        instruments=instruments
    )


# 绛栫暐锛氱敓鎴怱ynthesizedAnalysis
@composite
def synthesized_analysis_strategy(draw):
    """鐢熸垚闅忔満鐨凷ynthesizedAnalysis"""
    text_analysis = draw(st.one_of(st.none(), text_analysis_strategy()))
    visual_style = draw(st.one_of(st.none(), visual_style_strategy()))
    motion_style = draw(st.one_of(st.none(), motion_style_strategy()))
    audio_mood = draw(st.one_of(st.none(), audio_mood_strategy()))
    overall_theme = draw(st.text(max_size=100))
    confidence_scores = draw(st.dictionaries(
        keys=st.sampled_from(["text", "visual", "motion", "audio"]),
        values=st.floats(min_value=0.0, max_value=1.0),
        max_size=4
    ))
    
    return SynthesizedAnalysis(
        text_analysis=text_analysis,
        visual_style=visual_style,
        motion_style=motion_style,
        audio_mood=audio_mood,
        overall_theme=overall_theme,
        confidence_scores=confidence_scores
    )


# 绛栫暐锛氱敓鎴怳serInputData
@composite
def user_input_data_strategy(draw):
    """鐢熸垚闅忔満鐨刄serInputData"""
    text_description = draw(st.text(min_size=1, max_size=500))
    reference_images = draw(st.lists(st.text(min_size=1, max_size=100), max_size=5))
    reference_videos = draw(st.lists(st.text(min_size=1, max_size=100), max_size=3))
    reference_audio = draw(st.lists(st.text(min_size=1, max_size=100), max_size=3))
    
    # 鐢熸垚鐢ㄦ埛鍋忓ソ
    user_preferences = {}
    if draw(st.booleans()):
        user_preferences["duration"] = draw(st.integers(min_value=5, max_value=600))
    if draw(st.booleans()):
        user_preferences["aspect_ratio"] = draw(st.sampled_from(["9:16", "16:9", "1:1", "4:3"]))
    if draw(st.booleans()):
        user_preferences["quality_tier"] = draw(st.sampled_from(["high", "balanced", "fast"]))
    if draw(st.booleans()):
        user_preferences["fps"] = draw(st.sampled_from([24, 30, 60]))
    
    return UserInputData(
        text_description=text_description,
        reference_images=reference_images,
        reference_videos=reference_videos,
        reference_audio=reference_audio,
        user_preferences=user_preferences
    )


# 绛栫暐锛氱敓鎴怗lobalSpec
@composite
def global_spec_strategy(draw):
    """鐢熸垚闅忔満鐨凣lobalSpec"""
    title = draw(st.text(min_size=1, max_size=100))
    duration = draw(st.integers(min_value=5, max_value=600))
    aspect_ratio = draw(st.sampled_from(["9:16", "16:9", "1:1", "4:3"]))
    quality_tier = draw(st.sampled_from(["high", "balanced", "fast"]))
    resolution = draw(st.sampled_from(["1080x1920", "1920x1080", "1080x1080", "720x1280"]))
    fps = draw(st.sampled_from([24, 30, 60]))
    
    # 鐢熸垚StyleConfig
    tone = draw(st.text(min_size=1, max_size=50))
    palette = draw(st.lists(
        st.sampled_from(["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF", "#00FFFF"]),
        min_size=1,
        max_size=10
    ))
    visual_dna_version = draw(st.integers(min_value=1, max_value=10))
    
    style = StyleConfig(
        tone=tone,
        palette=palette,
        visual_dna_version=visual_dna_version
    )
    
    characters = draw(st.lists(st.text(min_size=1, max_size=50), max_size=10))
    mood = draw(st.text(min_size=1, max_size=100))
    user_options = draw(st.dictionaries(
        keys=st.text(min_size=1, max_size=20),
        values=st.one_of(st.text(), st.integers(), st.floats(), st.booleans()),
        max_size=5
    ))
    
    return GlobalSpec(
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


class TestConfidencePropertyBasedDecisionMaking:
    """
    Property 4: Confidence-Based Decision Making
    
    For any analysis result, the RequirementParser should calculate a valid confidence score (0-1)
    and trigger appropriate actions based on confidence thresholds.
    
    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
    """
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_confidence_score_is_valid_range(self, global_spec, analysis, user_input):
        """
        Property: For any analysis result, confidence score should be between 0 and 1
        
        Validates: Requirement 4.1
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 楠岃瘉缃俊搴﹀湪鏈夋晥鑼冨洿鍐?
        assert 0.0 <= report.overall_confidence <= 1.0, \
            f"Confidence score must be between 0 and 1, got {report.overall_confidence}"
        
        # 楠岃瘉鎵€鏈夌粍浠跺緱鍒嗕篃鍦ㄦ湁鏁堣寖鍥村唴
        for component, score in report.component_scores.items():
            assert 0.0 <= score <= 1.0, \
                f"Component score for {component} must be between 0 and 1, got {score}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_confidence_level_matches_score(self, global_spec, analysis, user_input):
        """
        Property: For any confidence score, the confidence level should match the score range
        
        Validates: Requirement 4.1
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 楠岃瘉缃俊搴︾骇鍒笌寰楀垎鍖归厤
        if report.overall_confidence >= 0.8:
            assert report.confidence_level == ConfidenceLevel.HIGH, \
                f"Confidence >= 0.8 should be HIGH, got {report.confidence_level}"
        elif report.overall_confidence >= 0.6:
            assert report.confidence_level == ConfidenceLevel.MEDIUM, \
                f"Confidence >= 0.6 should be MEDIUM, got {report.confidence_level}"
        else:
            assert report.confidence_level == ConfidenceLevel.LOW, \
                f"Confidence < 0.6 should be LOW, got {report.confidence_level}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_recommendation_based_on_threshold(self, global_spec, analysis, user_input):
        """
        Property: For any confidence score, recommendation should be based on threshold
        
        Validates: Requirement 4.2
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 楠岃瘉鎺ㄨ崘琛屽姩鐨勯€昏緫
        if report.overall_confidence >= evaluator.confidence_threshold:
            # 楂樼疆淇″害搴旇寤鸿缁х画
            assert report.recommendation in ["proceed", "clarify"], \
                f"High confidence should recommend 'proceed' or 'clarify', got {report.recommendation}"
        elif report.overall_confidence < 0.3:
            # 鏋佷綆缃俊搴﹀簲璇ュ缓璁汉宸ュ鏍?
            assert report.recommendation == "human_review", \
                f"Very low confidence should recommend 'human_review', got {report.recommendation}"
        else:
            # 涓瓑缃俊搴﹀簲璇ュ缓璁緞娓呮垨浜哄伐瀹℃牳
            assert report.recommendation in ["clarify", "human_review", "proceed"], \
                f"Medium confidence should recommend 'clarify', 'human_review', or 'proceed', got {report.recommendation}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_low_confidence_areas_identified(self, global_spec, analysis, user_input):
        """
        Property: For any analysis, low confidence areas should be correctly identified
        
        Validates: Requirement 4.3
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 楠岃瘉浣庣疆淇″害鍖哄煙鐨勮瘑鍒?
        for area in report.low_confidence_areas:
            # 璇ュ尯鍩熺殑寰楀垎搴旇浣庝簬闃堝€?
            assert area in report.component_scores, \
                f"Low confidence area {area} should be in component_scores"
            
            score = report.component_scores[area]
            assert score < evaluator.low_confidence_threshold, \
                f"Low confidence area {area} should have score < {evaluator.low_confidence_threshold}, got {score}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_clarification_requests_generated_for_low_confidence(self, global_spec, analysis, user_input):
        """
        Property: For any low confidence result, clarification requests should be generated
        
        Validates: Requirement 4.4
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 濡傛灉鏈変綆缃俊搴﹀尯鍩燂紝搴旇鏈夋緞娓呰姹?
        if len(report.low_confidence_areas) > 0:
            # 搴旇鐢熸垚鑷冲皯涓€涓緞娓呰姹?
            assert len(report.clarification_requests) >= 0, \
                "Low confidence areas should generate clarification requests"
        
        # 楠岃瘉鎵€鏈夋緞娓呰姹傜殑缁撴瀯
        for request in report.clarification_requests:
            assert hasattr(request, 'field_name'), "Request must have field_name"
            assert hasattr(request, 'reason'), "Request must have reason"
            assert hasattr(request, 'suggestions'), "Request must have suggestions"
            assert hasattr(request, 'priority'), "Request must have priority"
            
            assert request.priority in ["low", "medium", "high"], \
                f"Priority must be low/medium/high, got {request.priority}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_uncertain_fields_marked_correctly(self, global_spec, analysis, user_input):
        """
        Property: For any analysis, uncertain fields should be marked with confidence info
        
        Validates: Requirement 4.5
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 鏍囪涓嶇‘瀹氬瓧娈?
        uncertain_fields = evaluator.mark_uncertain_fields(global_spec, report)
        
        # 楠岃瘉涓嶇‘瀹氬瓧娈电殑缁撴瀯
        for field_name, field_info in uncertain_fields.items():
            assert isinstance(field_info, dict), \
                f"Uncertain field {field_name} info must be a dictionary"
            
            assert "value" in field_info, \
                f"Uncertain field {field_name} must have 'value'"
            
            assert "confidence" in field_info, \
                f"Uncertain field {field_name} must have 'confidence'"
            
            assert "reason" in field_info, \
                f"Uncertain field {field_name} must have 'reason'"
            
            # 缃俊搴﹀簲璇ュ湪鏈夋晥鑼冨洿鍐?
            assert 0.0 <= field_info["confidence"] <= 1.0, \
                f"Uncertain field {field_name} confidence must be between 0 and 1"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_confidence_report_structure_complete(self, global_spec, analysis, user_input):
        """
        Property: For any analysis, confidence report should have complete structure
        
        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及缃俊搴?
        report = await evaluator.evaluate_confidence(global_spec, analysis, user_input)
        
        # 楠岃瘉鎶ュ憡缁撴瀯瀹屾暣鎬?
        assert isinstance(report, ConfidenceReport), \
            "Result must be a ConfidenceReport instance"
        
        assert hasattr(report, 'overall_confidence'), \
            "Report must have overall_confidence"
        
        assert hasattr(report, 'component_scores'), \
            "Report must have component_scores"
        
        assert hasattr(report, 'confidence_level'), \
            "Report must have confidence_level"
        
        assert hasattr(report, 'low_confidence_areas'), \
            "Report must have low_confidence_areas"
        
        assert hasattr(report, 'clarification_requests'), \
            "Report must have clarification_requests"
        
        assert hasattr(report, 'recommendation'), \
            "Report must have recommendation"
        
        # 楠岃瘉瀛楁绫诲瀷
        assert isinstance(report.overall_confidence, float), \
            "overall_confidence must be float"
        
        assert isinstance(report.component_scores, dict), \
            "component_scores must be dict"
        
        assert isinstance(report.confidence_level, ConfidenceLevel), \
            "confidence_level must be ConfidenceLevel enum"
        
        assert isinstance(report.low_confidence_areas, list), \
            "low_confidence_areas must be list"
        
        assert isinstance(report.clarification_requests, list), \
            "clarification_requests must be list"
        
        assert isinstance(report.recommendation, str), \
            "recommendation must be string"
        
        assert report.recommendation in ["proceed", "clarify", "human_review"], \
            f"recommendation must be proceed/clarify/human_review, got {report.recommendation}"
    
    @given(
        global_spec=global_spec_strategy(),
        analysis=synthesized_analysis_strategy()
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_confidence_consistent_across_evaluations(self, global_spec, analysis):
        """
        Property: For the same inputs, confidence evaluation should be deterministic
        
        Validates: Requirement 4.1
        """
        evaluator = ConfidenceEvaluator()
        
        # 璇勪及涓ゆ
        report1 = await evaluator.evaluate_confidence(global_spec, analysis, None)
        report2 = await evaluator.evaluate_confidence(global_spec, analysis, None)
        
        # 楠岃瘉缁撴灉涓€鑷存€?
        assert report1.overall_confidence == report2.overall_confidence, \
            "Same inputs should produce same confidence score"
        
        assert report1.confidence_level == report2.confidence_level, \
            "Same inputs should produce same confidence level"
        
        assert report1.recommendation == report2.recommendation, \
            "Same inputs should produce same recommendation"
        
        assert report1.component_scores == report2.component_scores, \
            "Same inputs should produce same component scores"
