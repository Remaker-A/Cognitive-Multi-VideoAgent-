"""
MultimodalAnalyzer 单元测试
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.agents.interaction.requirement_parser.multimodal_analyzer import MultimodalAnalyzer
from src.agents.interaction.requirement_parser.deepseek_client import DeepSeekClient
from src.agents.interaction.requirement_parser.models import (
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
    SceneInfo,
    MultimodalAnalysisResponse
)


class TestMultimodalAnalyzerInitialization:
    """测试MultimodalAnalyzer初始化"""
    
    def test_init(self):
        """测试初始化"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        assert analyzer is not None
        assert analyzer.deepseek_client == mock_client


class TestAnalyzeTextIntent:
    """测试文本意图分析"""
    
    @pytest.mark.asyncio
    async def test_analyze_simple_text(self):
        """测试分析简单文本"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text="""```json
{
    "main_theme": "太空探索",
    "characters": [{"name": "宇航员", "description": "勇敢的探险家", "role": "protagonist", "traits": ["勇敢", "聪明"]}],
    "scenes": [{"description": "太空站", "location": "太空", "mood": "神秘"}],
    "mood_tags": ["神秘", "冒险"],
    "estimated_duration": 60,
    "narrative_structure": "linear",
    "genre": "科幻",
    "target_audience": "成人"
}
```""",
            confidence=0.8,
            tokens_used=100,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        text = ProcessedText(
            original="创建一个关于太空探索的视频",
            cleaned="创建一个关于太空探索的视频",
            language="zh",
            word_count=8,
            key_phrases=["太空", "探索"],
            sentiment="neutral"
        )
        
        result = await analyzer.analyze_text_intent(text)
        
        assert isinstance(result, TextAnalysis)
        assert result.main_theme == "太空探索"
        assert len(result.characters) == 1
        assert result.characters[0].name == "宇航员"
        assert len(result.scenes) == 1
        assert result.scenes[0].description == "太空站"
        assert "神秘" in result.mood_tags
        assert result.estimated_duration == 60
        assert result.genre == "科幻"
    
    @pytest.mark.asyncio
    async def test_analyze_text_with_api_error(self):
        """测试API错误时的降级处理"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(side_effect=Exception("API Error"))
        
        analyzer = MultimodalAnalyzer(mock_client)
        text = ProcessedText(
            original="创建视频",
            cleaned="创建视频",
            language="zh",
            word_count=2,
            key_phrases=["创建", "视频"],
            sentiment="neutral"
        )
        
        result = await analyzer.analyze_text_intent(text)
        
        # 应该返回降级结果
        assert isinstance(result, TextAnalysis)
        assert result.main_theme == "创建视频"
        assert result.estimated_duration == 30
    
    @pytest.mark.asyncio
    async def test_analyze_text_with_invalid_json(self):
        """测试解析无效JSON时的降级处理"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text="这不是有效的JSON",
            confidence=0.5,
            tokens_used=50,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        text = ProcessedText(
            original="测试文本",
            cleaned="测试文本",
            language="zh",
            word_count=2,
            key_phrases=[],
            sentiment="neutral"
        )
        
        result = await analyzer.analyze_text_intent(text)
        
        # 应该返回降级结果
        assert isinstance(result, TextAnalysis)
        assert result.main_theme == "测试文本"


class TestAnalyzeVisualStyle:
    """测试视觉风格分析"""
    
    @pytest.mark.asyncio
    async def test_analyze_visual_style_with_images(self):
        """测试分析视觉风格"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text="""```json
{
    "color_palette": ["#FF5733", "#33FF57", "#3357FF"],
    "lighting_style": "dramatic",
    "composition_style": "dynamic",
    "art_style": "cinematic",
    "reference_styles": ["电影感", "戏剧性"],
    "mood_descriptors": ["紧张", "激动"]
}
```""",
            confidence=0.85,
            tokens_used=120,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        images = [
            ProcessedImage(
                url="https://example.com/img1.jpg",
                width=1920,
                height=1080,
                format=".jpg",
                file_size=1024000
            )
        ]
        
        result = await analyzer.analyze_visual_style(images)
        
        assert isinstance(result, VisualStyle)
        assert len(result.color_palette) == 3
        assert result.lighting_style == "dramatic"
        assert result.composition_style == "dynamic"
        assert result.art_style == "cinematic"
        assert len(result.reference_styles) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_visual_style_empty_images(self):
        """测试空图片列表"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        result = await analyzer.analyze_visual_style([])
        
        # 应该返回默认视觉风格
        assert isinstance(result, VisualStyle)
        assert result.lighting_style == "natural"
        assert result.art_style == "realistic"
    
    @pytest.mark.asyncio
    async def test_analyze_visual_style_with_api_error(self):
        """测试API错误时的降级处理"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(side_effect=Exception("API Error"))
        
        analyzer = MultimodalAnalyzer(mock_client)
        images = [
            ProcessedImage(
                url="https://example.com/img.jpg",
                width=1920,
                height=1080,
                format=".jpg",
                file_size=1024000
            )
        ]
        
        result = await analyzer.analyze_visual_style(images)
        
        # 应该返回默认视觉风格
        assert isinstance(result, VisualStyle)


class TestAnalyzeMotionStyle:
    """测试运动风格分析"""
    
    @pytest.mark.asyncio
    async def test_analyze_motion_style_with_videos(self):
        """测试分析运动风格"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text="""```json
{
    "camera_movement": "tracking",
    "pace": "fast",
    "transition_style": "fade",
    "energy_level": "high"
}
```""",
            confidence=0.8,
            tokens_used=100,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        videos = [
            ProcessedVideo(
                url="https://example.com/vid.mp4",
                duration=30.0,
                width=1920,
                height=1080,
                fps=30.0,
                format=".mp4",
                file_size=5120000
            )
        ]
        
        result = await analyzer.analyze_motion_style(videos)
        
        assert isinstance(result, MotionStyle)
        assert result.camera_movement == "tracking"
        assert result.pace == "fast"
        assert result.transition_style == "fade"
        assert result.energy_level == "high"
    
    @pytest.mark.asyncio
    async def test_analyze_motion_style_empty_videos(self):
        """测试空视频列表"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        result = await analyzer.analyze_motion_style([])
        
        # 应该返回默认运动风格
        assert isinstance(result, MotionStyle)
        assert result.camera_movement == "static"
        assert result.pace == "medium"


class TestAnalyzeAudioMood:
    """测试音频情绪分析"""
    
    @pytest.mark.asyncio
    async def test_analyze_audio_mood_with_audio(self):
        """测试分析音频情绪"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text="""```json
{
    "tempo": "fast",
    "energy": "high",
    "mood": "excited",
    "genre": "electronic",
    "instruments": ["synthesizer", "drums"]
}
```""",
            confidence=0.8,
            tokens_used=100,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        audio = [
            ProcessedAudio(
                url="https://example.com/audio.mp3",
                duration=180.0,
                format=".mp3",
                file_size=3072000,
                sample_rate=44100,
                channels=2
            )
        ]
        
        result = await analyzer.analyze_audio_mood(audio)
        
        assert isinstance(result, AudioMood)
        assert result.tempo == "fast"
        assert result.energy == "high"
        assert result.mood == "excited"
        assert result.genre == "electronic"
        assert len(result.instruments) == 2
    
    @pytest.mark.asyncio
    async def test_analyze_audio_mood_empty_audio(self):
        """测试空音频列表"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        result = await analyzer.analyze_audio_mood([])
        
        # 应该返回默认音频情绪
        assert isinstance(result, AudioMood)
        assert result.tempo == "medium"
        assert result.mood == "neutral"


class TestSynthesizeAnalysis:
    """测试分析结果综合"""
    
    @pytest.mark.asyncio
    async def test_synthesize_complete_analysis(self):
        """测试综合完整分析结果"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="太空探索",
            characters=[CharacterInfo(name="宇航员", description="", role="protagonist")],
            scenes=[SceneInfo(description="太空站", location="太空", mood="神秘")],
            mood_tags=["神秘", "冒险"],
            estimated_duration=60
        )
        
        visual_style = VisualStyle(
            color_palette=["#FF5733"],
            lighting_style="dramatic",
            art_style="cinematic"
        )
        
        motion_style = MotionStyle(
            camera_movement="tracking",
            pace="fast",
            energy_level="high"
        )
        
        audio_mood = AudioMood(
            tempo="fast",
            energy="high",
            mood="excited"
        )
        
        result = await analyzer.synthesize_analysis(
            text_analysis, visual_style, motion_style, audio_mood
        )
        
        assert isinstance(result, SynthesizedAnalysis)
        assert result.text_analysis == text_analysis
        assert result.visual_style == visual_style
        assert result.motion_style == motion_style
        assert result.audio_mood == audio_mood
        assert result.overall_theme != ""
        assert "text" in result.confidence_scores
        assert "visual" in result.confidence_scores
        assert "motion" in result.confidence_scores
        assert "audio" in result.confidence_scores
        assert result.processing_metadata["modality_count"] == 4
    
    @pytest.mark.asyncio
    async def test_synthesize_text_only_analysis(self):
        """测试仅文本分析的综合"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="简单主题",
            estimated_duration=30
        )
        
        result = await analyzer.synthesize_analysis(
            text_analysis, None, None, None
        )
        
        assert isinstance(result, SynthesizedAnalysis)
        assert result.text_analysis == text_analysis
        assert result.visual_style is None
        assert result.motion_style is None
        assert result.audio_mood is None
        assert result.processing_metadata["modality_count"] == 1
    
    @pytest.mark.asyncio
    async def test_synthesize_determines_overall_theme(self):
        """测试确定整体主题"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="冒险故事",
            estimated_duration=30
        )
        
        visual_style = VisualStyle(
            art_style="cartoon",
            mood_descriptors=["欢快"]
        )
        
        result = await analyzer.synthesize_analysis(
            text_analysis, visual_style, None, None
        )
        
        assert "冒险故事" in result.overall_theme or "cartoon" in result.overall_theme or "欢快" in result.overall_theme


class TestConfidenceCalculation:
    """测试置信度计算"""
    
    def test_calculate_text_confidence_high(self):
        """测试高置信度文本分析"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="完整的主题描述",
            characters=[CharacterInfo(name="角色1", description="", role="protagonist")],
            scenes=[SceneInfo(description="场景1", location="", mood="")],
            mood_tags=["标签1"],
            estimated_duration=30
        )
        
        confidence = analyzer._calculate_text_confidence(text_analysis)
        
        assert 0.8 <= confidence <= 1.0
    
    def test_calculate_text_confidence_low(self):
        """测试低置信度文本分析"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="短",
            estimated_duration=30
        )
        
        confidence = analyzer._calculate_text_confidence(text_analysis)
        
        assert confidence < 0.5
    
    def test_calculate_visual_confidence(self):
        """测试视觉风格置信度计算"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        visual_style = VisualStyle(
            color_palette=["#FF5733"],
            lighting_style="dramatic",
            art_style="cinematic"
        )
        
        confidence = analyzer._calculate_visual_confidence(visual_style)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_motion_confidence(self):
        """测试运动风格置信度计算"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        motion_style = MotionStyle(
            camera_movement="tracking",
            pace="fast"
        )
        
        confidence = analyzer._calculate_motion_confidence(motion_style)
        
        assert 0.0 <= confidence <= 1.0
    
    def test_calculate_audio_confidence(self):
        """测试音频情绪置信度计算"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        audio_mood = AudioMood(
            tempo="fast",
            energy="high",
            mood="excited",
            genre="electronic"
        )
        
        confidence = analyzer._calculate_audio_confidence(audio_mood)
        
        assert 0.0 <= confidence <= 1.0


class TestDetermineOverallTheme:
    """测试确定整体主题"""
    
    def test_determine_theme_from_text_only(self):
        """测试仅从文本确定主题"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="太空探索",
            estimated_duration=30
        )
        
        theme = analyzer._determine_overall_theme(text_analysis, None, None, None)
        
        assert theme == "太空探索"
    
    def test_determine_theme_from_multiple_sources(self):
        """测试从多个来源确定主题"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        text_analysis = TextAnalysis(
            main_theme="冒险",
            estimated_duration=30
        )
        
        visual_style = VisualStyle(
            art_style="cartoon",
            mood_descriptors=["欢快"]
        )
        
        motion_style = MotionStyle(
            pace="fast"
        )
        
        theme = analyzer._determine_overall_theme(
            text_analysis, visual_style, motion_style, None
        )
        
        assert "冒险" in theme or "cartoon" in theme or "快节奏" in theme
    
    def test_determine_theme_default(self):
        """测试默认主题"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        theme = analyzer._determine_overall_theme(None, None, None, None)
        
        assert theme == "视频创作"


class TestAnalyzeAll:
    """测试综合分析所有模态"""
    
    @pytest.mark.asyncio
    async def test_analyze_all_complete_input(self):
        """测试分析完整输入"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text='```json\n{"main_theme": "测试", "characters": [], "scenes": [], "mood_tags": [], "estimated_duration": 30, "narrative_structure": "linear"}\n```',
            confidence=0.8,
            tokens_used=100,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        
        text = ProcessedText(
            original="测试",
            cleaned="测试",
            language="zh",
            word_count=1,
            key_phrases=[],
            sentiment="neutral"
        )
        
        images = [ProcessedImage(
            url="https://example.com/img.jpg",
            width=1920,
            height=1080,
            format=".jpg",
            file_size=1024000
        )]
        
        videos = [ProcessedVideo(
            url="https://example.com/vid.mp4",
            duration=30.0,
            width=1920,
            height=1080,
            fps=30.0,
            format=".mp4",
            file_size=5120000
        )]
        
        audio = [ProcessedAudio(
            url="https://example.com/audio.mp3",
            duration=180.0,
            format=".mp3",
            file_size=3072000,
            sample_rate=44100,
            channels=2
        )]
        
        result = await analyzer.analyze_all(text, images, videos, audio)
        
        assert isinstance(result, SynthesizedAnalysis)
        assert result.text_analysis is not None
        assert result.visual_style is not None
        assert result.motion_style is not None
        assert result.audio_mood is not None
        assert result.processing_metadata["modality_count"] == 4
    
    @pytest.mark.asyncio
    async def test_analyze_all_text_only(self):
        """测试仅分析文本"""
        mock_client = MagicMock(spec=DeepSeekClient)
        mock_client.analyze_multimodal = AsyncMock(return_value=MultimodalAnalysisResponse(
            analysis_text='```json\n{"main_theme": "测试", "characters": [], "scenes": [], "mood_tags": [], "estimated_duration": 30, "narrative_structure": "linear"}\n```',
            confidence=0.8,
            tokens_used=100,
            model_used="DeepSeek-V3.2"
        ))
        
        analyzer = MultimodalAnalyzer(mock_client)
        
        text = ProcessedText(
            original="测试",
            cleaned="测试",
            language="zh",
            word_count=1,
            key_phrases=[],
            sentiment="neutral"
        )
        
        result = await analyzer.analyze_all(text, [], [], [])
        
        assert isinstance(result, SynthesizedAnalysis)
        assert result.text_analysis is not None
        assert result.visual_style is None
        assert result.motion_style is None
        assert result.audio_mood is None
        assert result.processing_metadata["modality_count"] == 1


class TestParseTextAnalysis:
    """测试文本分析解析"""
    
    def test_parse_valid_json(self):
        """测试解析有效JSON"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        analysis_text = """```json
{
    "main_theme": "测试主题",
    "characters": [{"name": "角色1", "description": "描述", "role": "protagonist", "traits": ["勇敢"]}],
    "scenes": [{"description": "场景1", "location": "地点1", "mood": "情绪1"}],
    "mood_tags": ["标签1", "标签2"],
    "estimated_duration": 45,
    "narrative_structure": "nonlinear",
    "genre": "动作",
    "target_audience": "青少年"
}
```"""
        
        text = ProcessedText(
            original="",
            cleaned="",
            language="zh",
            word_count=0,
            key_phrases=[]
        )
        
        result = analyzer._parse_text_analysis(analysis_text, text)
        
        assert result.main_theme == "测试主题"
        assert len(result.characters) == 1
        assert result.characters[0].name == "角色1"
        assert len(result.scenes) == 1
        assert result.estimated_duration == 45
        assert result.genre == "动作"
    
    def test_parse_json_without_code_block(self):
        """测试解析不带代码块的JSON"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        analysis_text = '{"main_theme": "主题", "characters": [], "scenes": [], "mood_tags": [], "estimated_duration": 30}'
        
        text = ProcessedText(
            original="",
            cleaned="",
            language="zh",
            word_count=0,
            key_phrases=[]
        )
        
        result = analyzer._parse_text_analysis(analysis_text, text)
        
        assert result.main_theme == "主题"
    
    def test_parse_invalid_json_fallback(self):
        """测试解析无效JSON时的降级"""
        mock_client = MagicMock(spec=DeepSeekClient)
        analyzer = MultimodalAnalyzer(mock_client)
        
        analysis_text = "这不是JSON"
        
        text = ProcessedText(
            original="原始文本",
            cleaned="原始文本",
            language="zh",
            word_count=2,
            key_phrases=[],
            sentiment="neutral"
        )
        
        result = analyzer._parse_text_analysis(analysis_text, text)
        
        # 应该返回降级结果
        assert result.main_theme == "原始文本"
        assert result.estimated_duration == 30
