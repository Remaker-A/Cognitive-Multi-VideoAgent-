"""
GlobalSpec生成器单元测试

测试默认值设置和配置合理性验证
Validates: Requirements 2.5
"""

import pytest

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


class TestGlobalSpecGeneratorDefaults:
    """
    测试GlobalSpec生成器的默认值设置
    
    Validates: Requirements 2.5
    """
    
    @pytest.mark.asyncio
    async def test_generates_spec_with_minimal_analysis(self):
        """
        测试：当分析结果最少时，应该使用默认值生成有效的GlobalSpec
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 创建最小的分析结果
        minimal_analysis = SynthesizedAnalysis(
            text_analysis=None,
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="",
            confidence_scores={}
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(minimal_analysis)
        
        # 验证所有必需字段都有有效的默认值
        assert global_spec.title is not None
        assert len(global_spec.title) > 0
        assert global_spec.duration == 30  # 默认时长
        assert global_spec.aspect_ratio == "9:16"  # 默认宽高比
        assert global_spec.quality_tier == "balanced"  # 默认质量档位
        assert global_spec.fps == 30  # 默认帧率
        assert global_spec.style.tone == "natural"  # 默认色调
        assert len(global_spec.style.palette) > 0  # 默认调色板
        assert global_spec.mood is not None
        assert len(global_spec.mood) > 0
    
    @pytest.mark.asyncio
    async def test_uses_default_duration_when_not_specified(self):
        """
        测试：当没有指定时长时，应该使用默认值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 创建没有时长信息的分析结果
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试主题",
                estimated_duration=0  # 无效的时长
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试主题"
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(analysis)
        
        # 验证使用了默认时长
        assert global_spec.duration == 30
    
    @pytest.mark.asyncio
    async def test_uses_default_aspect_ratio_when_not_specified(self):
        """
        测试：当没有指定宽高比时，应该使用默认值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 生成GlobalSpec（不提供用户偏好）
        global_spec = await generator.generate_spec(analysis)
        
        # 验证使用了默认宽高比
        assert global_spec.aspect_ratio == "9:16"
    
    @pytest.mark.asyncio
    async def test_uses_default_quality_tier_when_not_specified(self):
        """
        测试：当没有指定质量档位时，应该使用默认值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(analysis)
        
        # 验证使用了默认质量档位
        assert global_spec.quality_tier == "balanced"
    
    @pytest.mark.asyncio
    async def test_uses_default_fps_when_not_specified(self):
        """
        测试：当没有指定帧率时，应该使用默认值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(analysis)
        
        # 验证使用了默认帧率
        assert global_spec.fps == 30
    
    @pytest.mark.asyncio
    async def test_uses_default_style_when_no_visual_info(self):
        """
        测试：当没有视觉信息时，应该使用默认风格配置
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,  # 没有视觉风格
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(analysis)
        
        # 验证使用了默认风格配置
        assert global_spec.style.tone == "natural"
        assert len(global_spec.style.palette) > 0
        assert global_spec.style.visual_dna_version == 1
    
    @pytest.mark.asyncio
    async def test_uses_default_mood_when_no_mood_info(self):
        """
        测试：当没有情绪信息时，应该使用默认情绪
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试",
                mood_tags=[]  # 没有情绪标签
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 生成GlobalSpec
        global_spec = await generator.generate_spec(analysis)
        
        # 验证有默认情绪
        assert global_spec.mood == "neutral"


class TestGlobalSpecGeneratorValidation:
    """
    测试GlobalSpec生成器的配置合理性验证
    
    Validates: Requirements 2.5
    """
    
    @pytest.mark.asyncio
    async def test_validates_duration_range(self):
        """
        测试：时长应该在合理范围内（5-600秒）
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 测试过短的时长
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试",
                estimated_duration=2  # 太短
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        # 应该使用默认值而不是无效值
        assert global_spec.duration >= 5
        assert global_spec.duration <= 600
    
    @pytest.mark.asyncio
    async def test_validates_aspect_ratio_values(self):
        """
        测试：宽高比应该是有效的预定义值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 测试无效的宽高比偏好
        user_input = UserInputData(
            text_description="测试",
            user_preferences={"aspect_ratio": "invalid"}
        )
        
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 应该使用默认值而不是无效值
        assert global_spec.aspect_ratio in ["9:16", "16:9", "1:1", "4:3"]
    
    @pytest.mark.asyncio
    async def test_validates_quality_tier_values(self):
        """
        测试：质量档位应该是有效的预定义值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 测试无效的质量档位偏好
        user_input = UserInputData(
            text_description="测试",
            user_preferences={"quality_tier": "invalid"}
        )
        
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 应该使用默认值而不是无效值
        assert global_spec.quality_tier in ["high", "balanced", "fast"]
    
    @pytest.mark.asyncio
    async def test_validates_fps_values(self):
        """
        测试：帧率应该是有效的预定义值
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 测试无效的帧率偏好
        user_input = UserInputData(
            text_description="测试",
            user_preferences={"fps": 120}  # 不支持的帧率
        )
        
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 应该使用默认值而不是无效值
        assert global_spec.fps in [24, 30, 60]
    
    @pytest.mark.asyncio
    async def test_title_length_is_reasonable(self):
        """
        测试：标题长度应该在合理范围内
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        # 创建一个非常长的主题
        long_theme = "这是一个非常非常非常非常非常非常非常非常非常非常长的主题" * 10
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme=long_theme),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme=long_theme
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        # 标题应该被截断到合理长度
        assert len(global_spec.title) <= 50
    
    @pytest.mark.asyncio
    async def test_resolution_matches_aspect_ratio(self):
        """
        测试：分辨率应该与宽高比匹配
        
        Validates: Requirements 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        # 测试不同的宽高比
        for aspect_ratio in ["9:16", "16:9", "1:1"]:
            user_input = UserInputData(
                text_description="测试",
                user_preferences={"aspect_ratio": aspect_ratio}
            )
            
            global_spec = await generator.generate_spec(analysis, user_input)
            
            # 验证分辨率格式正确
            assert "x" in global_spec.resolution
            width, height = global_spec.resolution.split("x")
            width, height = int(width), int(height)
            
            # 验证分辨率与宽高比匹配
            if aspect_ratio == "9:16":
                assert width < height  # 竖屏
            elif aspect_ratio == "16:9":
                assert width > height  # 横屏
            elif aspect_ratio == "1:1":
                assert width == height  # 正方形


class TestGlobalSpecGeneratorExtraction:
    """
    测试GlobalSpec生成器的信息提取功能
    
    Validates: Requirements 2.1, 2.2, 2.3, 2.4
    """
    
    @pytest.mark.asyncio
    async def test_extracts_title_from_text_analysis(self):
        """
        测试：从文本分析中提取标题
        
        Validates: Requirements 2.1
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="探险家的奇幻旅程"),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="探险"
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        assert global_spec.title == "探险家的奇幻旅程"
    
    @pytest.mark.asyncio
    async def test_extracts_characters_from_text_analysis(self):
        """
        测试：从文本分析中提取角色列表
        
        Validates: Requirements 2.3
        """
        generator = GlobalSpecGenerator()
        
        characters = [
            CharacterInfo(name="小明", description="主角", role="protagonist"),
            CharacterInfo(name="小红", description="配角", role="supporting")
        ]
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试",
                characters=characters
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        assert len(global_spec.characters) == 2
        assert "小明" in global_spec.characters
        assert "小红" in global_spec.characters
    
    @pytest.mark.asyncio
    async def test_extracts_mood_from_multiple_sources(self):
        """
        测试：从多个来源提取情绪标签
        
        Validates: Requirements 2.4
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试",
                mood_tags=["欢快", "温馨"]
            ),
            visual_style=VisualStyle(
                mood_descriptors=["明亮", "活泼"]
            ),
            motion_style=None,
            audio_mood=AudioMood(mood="happy"),
            overall_theme="测试"
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        # 验证情绪标签包含来自不同来源的信息
        assert "欢快" in global_spec.mood or "温馨" in global_spec.mood or \
               "明亮" in global_spec.mood or "happy" in global_spec.mood
    
    @pytest.mark.asyncio
    async def test_synthesizes_style_from_visual_analysis(self):
        """
        测试：从视觉分析综合风格配置
        
        Validates: Requirements 2.2
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(main_theme="测试"),
            visual_style=VisualStyle(
                color_palette=["#FF0000", "#00FF00", "#0000FF"],
                lighting_style="dramatic"
            ),
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        global_spec = await generator.generate_spec(analysis)
        
        # 验证风格配置使用了视觉分析的信息
        assert global_spec.style.tone == "dramatic"
        assert "#FF0000" in global_spec.style.palette
        assert "#00FF00" in global_spec.style.palette
        assert "#0000FF" in global_spec.style.palette
    
    @pytest.mark.asyncio
    async def test_respects_user_duration_preference(self):
        """
        测试：尊重用户的时长偏好
        
        Validates: Requirements 2.1, 2.5
        """
        generator = GlobalSpecGenerator()
        
        analysis = SynthesizedAnalysis(
            text_analysis=TextAnalysis(
                main_theme="测试",
                estimated_duration=30
            ),
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme="测试"
        )
        
        user_input = UserInputData(
            text_description="测试",
            user_preferences={"duration": 60}
        )
        
        global_spec = await generator.generate_spec(analysis, user_input)
        
        # 用户偏好应该优先于分析结果
        assert global_spec.duration == 60
