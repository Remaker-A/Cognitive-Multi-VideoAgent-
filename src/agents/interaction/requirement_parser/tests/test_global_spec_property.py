"""
GlobalSpec鐢熸垚鍣ㄥ睘鎬ф祴璇?

Feature: requirement-parser-agent, Property 2: GlobalSpec Structure Completeness
Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
from hypothesis import given, strategies as st, settings
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
    UserInputData
)
from ..global_spec_generator import GlobalSpecGenerator


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


class TestGlobalSpecPropertyCompleteness:
    """
    Property 2: GlobalSpec Structure Completeness
    
    For any valid user input, the generated GlobalSpec should contain all required fields
    (title, duration, aspect_ratio, quality_tier, style configuration, characters, mood)
    with valid values.
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
    """
    
    @given(
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_global_spec_has_all_required_fields(self, analysis, user_input):
        """
        Property: For any analysis result, GlobalSpec should have all required fields
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 鐢熸垚GlobalSpec
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 楠岃瘉鎵€鏈夊繀闇€瀛楁瀛樺湪
        assert hasattr(global_spec, 'title'), "GlobalSpec must have 'title' field"
        assert hasattr(global_spec, 'duration'), "GlobalSpec must have 'duration' field"
        assert hasattr(global_spec, 'aspect_ratio'), "GlobalSpec must have 'aspect_ratio' field"
        assert hasattr(global_spec, 'quality_tier'), "GlobalSpec must have 'quality_tier' field"
        assert hasattr(global_spec, 'resolution'), "GlobalSpec must have 'resolution' field"
        assert hasattr(global_spec, 'fps'), "GlobalSpec must have 'fps' field"
        assert hasattr(global_spec, 'style'), "GlobalSpec must have 'style' field"
        assert hasattr(global_spec, 'characters'), "GlobalSpec must have 'characters' field"
        assert hasattr(global_spec, 'mood'), "GlobalSpec must have 'mood' field"
        assert hasattr(global_spec, 'user_options'), "GlobalSpec must have 'user_options' field"
    
    @given(
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_global_spec_fields_have_valid_values(self, analysis, user_input):
        """
        Property: For any analysis result, GlobalSpec fields should have valid values
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 鐢熸垚GlobalSpec
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 楠岃瘉瀛楁鍊肩殑鏈夋晥鎬?
        # Requirement 2.1: 鍩虹閰嶇疆
        assert isinstance(global_spec.title, str), "title must be a string"
        assert len(global_spec.title) > 0, "title must not be empty"
        
        assert isinstance(global_spec.duration, int), "duration must be an integer"
        assert global_spec.duration > 0, "duration must be positive"
        assert 5 <= global_spec.duration <= 600, "duration must be between 5 and 600 seconds"
        
        assert isinstance(global_spec.aspect_ratio, str), "aspect_ratio must be a string"
        assert global_spec.aspect_ratio in ["9:16", "16:9", "1:1", "4:3"], \
            "aspect_ratio must be a valid ratio"
        
        assert isinstance(global_spec.quality_tier, str), "quality_tier must be a string"
        assert global_spec.quality_tier in ["high", "balanced", "fast"], \
            "quality_tier must be a valid tier"
        
        assert isinstance(global_spec.resolution, str), "resolution must be a string"
        assert "x" in global_spec.resolution, "resolution must be in format WIDTHxHEIGHT"
        
        assert isinstance(global_spec.fps, int), "fps must be an integer"
        assert global_spec.fps in [24, 30, 60], "fps must be a valid frame rate"
        
        # Requirement 2.2: 椋庢牸閰嶇疆
        assert isinstance(global_spec.style, StyleConfig), "style must be a StyleConfig instance"
        assert isinstance(global_spec.style.tone, str), "style.tone must be a string"
        assert len(global_spec.style.tone) > 0, "style.tone must not be empty"
        
        assert isinstance(global_spec.style.palette, list), "style.palette must be a list"
        assert len(global_spec.style.palette) > 0, "style.palette must not be empty"
        assert all(isinstance(color, str) for color in global_spec.style.palette), \
            "all palette colors must be strings"
        
        assert isinstance(global_spec.style.visual_dna_version, int), \
            "style.visual_dna_version must be an integer"
        assert global_spec.style.visual_dna_version > 0, \
            "style.visual_dna_version must be positive"
        
        # Requirement 2.3: 瑙掕壊淇℃伅
        assert isinstance(global_spec.characters, list), "characters must be a list"
        assert all(isinstance(char, str) for char in global_spec.characters), \
            "all characters must be strings"
        
        # Requirement 2.4: 鎯呯华鏍囩
        assert isinstance(global_spec.mood, str), "mood must be a string"
        assert len(global_spec.mood) > 0, "mood must not be empty"
        
        # Requirement 2.5: 鐢ㄦ埛閫夐」
        assert isinstance(global_spec.user_options, dict), "user_options must be a dictionary"
    
    @given(
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_global_spec_respects_user_preferences(self, analysis, user_input):
        """
        Property: For any user input with preferences, GlobalSpec should respect those preferences
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 鐢熸垚GlobalSpec
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 濡傛灉鐢ㄦ埛鎻愪緵浜嗗亸濂斤紝楠岃瘉瀹冧滑琚皧閲?
        if user_input and user_input.user_preferences:
            prefs = user_input.user_preferences
            
            # 楠岃瘉鏃堕暱鍋忓ソ
            if "duration" in prefs:
                duration = prefs["duration"]
                if isinstance(duration, (int, float)) and 5 <= duration <= 600:
                    assert global_spec.duration == int(duration), \
                        "GlobalSpec should respect user's duration preference"
            
            # 楠岃瘉瀹介珮姣斿亸濂?
            if "aspect_ratio" in prefs:
                aspect_ratio = prefs["aspect_ratio"]
                if aspect_ratio in ["9:16", "16:9", "1:1", "4:3"]:
                    assert global_spec.aspect_ratio == aspect_ratio, \
                        "GlobalSpec should respect user's aspect_ratio preference"
            
            # 楠岃瘉璐ㄩ噺妗ｄ綅鍋忓ソ
            if "quality_tier" in prefs:
                quality_tier = prefs["quality_tier"]
                if quality_tier in ["high", "balanced", "fast"]:
                    assert global_spec.quality_tier == quality_tier, \
                        "GlobalSpec should respect user's quality_tier preference"
            
            # 楠岃瘉甯х巼鍋忓ソ
            if "fps" in prefs:
                fps = prefs["fps"]
                if fps in [24, 30, 60]:
                    assert global_spec.fps == fps, \
                        "GlobalSpec should respect user's fps preference"
    
    @given(analysis=synthesized_analysis_strategy())
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_global_spec_provides_defaults_when_info_missing(self, analysis):
        """
        Property: For any analysis with missing information, GlobalSpec should provide reasonable defaults
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 鐢熸垚GlobalSpec锛堜笉鎻愪緵鐢ㄦ埛杈撳叆锛?
        global_spec = await generator.generate_spec(analysis, user_input=None)
        
        # 楠岃瘉鍗充娇娌℃湁鐢ㄦ埛杈撳叆锛屼篃鑳界敓鎴愭湁鏁堢殑GlobalSpec
        assert global_spec.title is not None and len(global_spec.title) > 0
        assert global_spec.duration > 0
        assert global_spec.aspect_ratio in ["9:16", "16:9", "1:1", "4:3"]
        assert global_spec.quality_tier in ["high", "balanced", "fast"]
        assert global_spec.fps in [24, 30, 60]
        assert global_spec.style.tone is not None and len(global_spec.style.tone) > 0
        assert len(global_spec.style.palette) > 0
        assert global_spec.mood is not None and len(global_spec.mood) > 0
    
    @given(
        analysis=synthesized_analysis_strategy(),
        user_input=st.one_of(st.none(), user_input_data_strategy())
    )
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_global_spec_to_dict_is_serializable(self, analysis, user_input):
        """
        Property: For any GlobalSpec, to_dict() should produce a serializable dictionary
        
        Validates: Requirements 2.1, 2.2, 2.3, 2.4
        """
        generator = GlobalSpecGenerator()
        
        # 鐢熸垚GlobalSpec
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 杞崲涓哄瓧鍏?
        spec_dict = global_spec.to_dict()
        
        # 楠岃瘉瀛楀吀鍖呭惈鎵€鏈夊繀闇€瀛楁
        assert "title" in spec_dict
        assert "duration" in spec_dict
        assert "aspect_ratio" in spec_dict
        assert "quality_tier" in spec_dict
        assert "resolution" in spec_dict
        assert "fps" in spec_dict
        assert "style" in spec_dict
        assert "characters" in spec_dict
        assert "mood" in spec_dict
        assert "user_options" in spec_dict
        
        # 楠岃瘉style鏄瓧鍏?
        assert isinstance(spec_dict["style"], dict)
        assert "tone" in spec_dict["style"]
        assert "palette" in spec_dict["style"]
        assert "visual_dna_version" in spec_dict["style"]
        
        # 楠岃瘉鎵€鏈夊€奸兘鏄彲搴忓垪鍖栫殑鍩烘湰绫诲瀷
        import json
        try:
            json.dumps(spec_dict)
        except (TypeError, ValueError) as e:
            pytest.fail(f"GlobalSpec.to_dict() should produce JSON-serializable output: {e}")
