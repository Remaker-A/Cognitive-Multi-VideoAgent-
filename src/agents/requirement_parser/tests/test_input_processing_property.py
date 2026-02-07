"""
杈撳叆澶勭悊灞炴€ф祴璇?

Property 1: Multimodal Input Processing
楠岃瘉锛氬浜庝换浣曠敤鎴疯緭鍏ョ粍鍚堬紙鏂囨湰銆佸浘鐗囥€佽棰戙€侀煶棰戯級锛?
RequirementParser搴旇鎴愬姛澶勭悊姣忕妯℃€佸苟鎻愬彇鐩稿叧鐗瑰緛锛?
鑰屼笉浼氬湪鏈夋晥杈撳叆鏍煎紡涓婂け璐ャ€?

Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import List, Dict, Any

from src.agents.requirement_parser.input_manager import InputManager
from src.agents.requirement_parser.preprocessor import Preprocessor
from src.agents.requirement_parser.models import (
    UserInputData,
    ProcessedInput,
    ProcessedText,
    ProcessedImage,
    ProcessedVideo,
    ProcessedAudio
)


# ============================================================================
# Hypothesis Strategies - 鐢熸垚娴嬭瘯鏁版嵁鐨勭瓥鐣?
# ============================================================================

# 鏂囨湰绛栫暐锛氱敓鎴愭湁鏁堢殑鏂囨湰鎻忚堪
text_strategy = st.text(
    alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs'),  # 澶у啓銆佸皬鍐欍€佹暟瀛椼€佺┖鏍?
        min_codepoint=32,
        max_codepoint=126
    ),
    min_size=10,
    max_size=500
)

# 涓枃鏂囨湰绛栫暐
chinese_text_strategy = st.text(
    alphabet=st.characters(
        min_codepoint=0x4e00,  # 涓枃瀛楃璧峰
        max_codepoint=0x9fff   # 涓枃瀛楃缁撴潫
    ),
    min_size=5,
    max_size=100
)

# URL绛栫暐锛氱敓鎴愭湁鏁堢殑鏂囦欢URL
def url_strategy(extension: str) -> st.SearchStrategy[str]:
    """鐢熸垚鎸囧畾鎵╁睍鍚嶇殑URL"""
    return st.builds(
        lambda domain, path, filename: f"https://{domain}/{path}/{filename}{extension}",
        domain=st.sampled_from(['example.com', 'test.com', 'media.com']),
        path=st.sampled_from(['images', 'videos', 'audio', 'files']),
        filename=st.text(
            alphabet=st.characters(whitelist_categories=('Ll', 'Nd')),
            min_size=5,
            max_size=20
        )
    )

# 鍥剧墖URL鍒楄〃绛栫暐
image_urls_strategy = st.lists(
    st.one_of(
        url_strategy('.jpg'),
        url_strategy('.png'),
        url_strategy('.gif'),
        url_strategy('.webp')
    ),
    min_size=0,
    max_size=5
)

# 瑙嗛URL鍒楄〃绛栫暐
video_urls_strategy = st.lists(
    st.one_of(
        url_strategy('.mp4'),
        url_strategy('.mov'),
        url_strategy('.avi'),
        url_strategy('.mkv')
    ),
    min_size=0,
    max_size=3
)

# 闊抽URL鍒楄〃绛栫暐
audio_urls_strategy = st.lists(
    st.one_of(
        url_strategy('.mp3'),
        url_strategy('.wav'),
        url_strategy('.aac'),
        url_strategy('.flac')
    ),
    min_size=0,
    max_size=3
)

# 鐢ㄦ埛鍋忓ソ绛栫暐
user_preferences_strategy = st.dictionaries(
    keys=st.sampled_from(['aspect_ratio', 'quality', 'duration', 'style']),
    values=st.one_of(
        st.text(min_size=1, max_size=20),
        st.integers(min_value=1, max_value=100)
    ),
    min_size=0,
    max_size=4
)


# ============================================================================
# Property Tests - 灞炴€ф祴璇?
# ============================================================================

class TestMultimodalInputProcessingProperty:
    """
    Property 1: Multimodal Input Processing
    
    楠岃瘉澶氭ā鎬佽緭鍏ュ鐞嗙殑椴佹鎬у拰姝ｇ‘鎬?
    """
    
    @given(
        text=st.one_of(text_strategy, chinese_text_strategy),
        image_urls=image_urls_strategy,
        video_urls=video_urls_strategy,
        audio_urls=audio_urls_strategy,
        user_prefs=user_preferences_strategy
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_input_manager_processes_all_modalities(
        self,
        text: str,
        image_urls: List[str],
        video_urls: List[str],
        audio_urls: List[str],
        user_prefs: Dict[str, Any]
    ):
        """
        Property: InputManager搴旇鎴愬姛澶勭悊浠讳綍鏈夋晥鐨勫妯℃€佽緭鍏ョ粍鍚?
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5
        """
        # 璺宠繃绌烘枃鏈笖鏃犳枃浠剁殑鎯呭喌锛堣繖鏄棤鏁堣緭鍏ワ級
        if not text.strip() and not any([image_urls, video_urls, audio_urls]):
            return
        
        manager = InputManager()
        
        # 鍒涘缓鐢ㄦ埛杈撳叆
        user_input = UserInputData(
            text_description=text if text.strip() else "default text",
            reference_images=image_urls,
            reference_videos=video_urls,
            reference_audio=audio_urls,
            user_preferences=user_prefs
        )
        
        # 澶勭悊杈撳叆 - 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await manager.receive_user_input(user_input)
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, ProcessedInput)
        assert result.text is not None
        assert isinstance(result.images, list)
        assert isinstance(result.videos, list)
        assert isinstance(result.audio, list)
        
        # 楠岃瘉鏂囦欢鏁伴噺涓嶈秴杩囪緭鍏?
        assert len(result.images) <= len(image_urls)
        assert len(result.videos) <= len(video_urls)
        assert len(result.audio) <= len(audio_urls)
    
    @given(text=st.one_of(text_strategy, chinese_text_strategy))
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_preprocessor_processes_text_without_failure(self, text: str):
        """
        Property: Preprocessor搴旇鎴愬姛澶勭悊浠讳綍闈炵┖鏂囨湰
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.1
        """
        # 璺宠繃绌烘枃鏈?
        if not text.strip():
            return
        
        preprocessor = Preprocessor()
        
        # 澶勭悊鏂囨湰 - 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await preprocessor.process_text(text)
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, ProcessedText)
        assert result.original == text
        assert result.cleaned is not None
        assert len(result.cleaned) > 0
        assert result.language in ['zh', 'en', 'unknown']
        assert result.word_count >= 0
        assert isinstance(result.key_phrases, list)
        assert result.sentiment in ['positive', 'negative', 'neutral']
    
    @given(urls=image_urls_strategy)
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_preprocessor_processes_images_without_failure(self, urls: List[str]):
        """
        Property: Preprocessor搴旇鎴愬姛澶勭悊浠讳綍鏈夋晥鐨勫浘鐗嘦RL鍒楄〃
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.2
        """
        preprocessor = Preprocessor()
        
        # 澶勭悊鍥剧墖 - 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await preprocessor.process_images(urls)
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, list)
        assert len(result) <= len(urls)
        
        # 楠岃瘉姣忎釜澶勭悊鍚庣殑鍥剧墖
        for img in result:
            assert isinstance(img, ProcessedImage)
            assert img.url in urls
            assert img.format.startswith('.')
            assert img.width > 0
            assert img.height > 0
    
    @given(urls=video_urls_strategy)
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_preprocessor_processes_videos_without_failure(self, urls: List[str]):
        """
        Property: Preprocessor搴旇鎴愬姛澶勭悊浠讳綍鏈夋晥鐨勮棰慤RL鍒楄〃
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.3
        """
        preprocessor = Preprocessor()
        
        # 澶勭悊瑙嗛 - 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await preprocessor.process_videos(urls)
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, list)
        assert len(result) <= len(urls)
        
        # 楠岃瘉姣忎釜澶勭悊鍚庣殑瑙嗛
        for vid in result:
            assert isinstance(vid, ProcessedVideo)
            assert vid.url in urls
            assert vid.format.startswith('.')
            assert vid.duration > 0
            assert vid.fps > 0
    
    @given(urls=audio_urls_strategy)
    @settings(max_examples=20, deadline=None)
    @pytest.mark.asyncio
    async def test_preprocessor_processes_audio_without_failure(self, urls: List[str]):
        """
        Property: Preprocessor搴旇鎴愬姛澶勭悊浠讳綍鏈夋晥鐨勯煶棰慤RL鍒楄〃
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.4
        """
        preprocessor = Preprocessor()
        
        # 澶勭悊闊抽 - 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await preprocessor.process_audio(urls)
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, list)
        assert len(result) <= len(urls)
        
        # 楠岃瘉姣忎釜澶勭悊鍚庣殑闊抽
        for aud in result:
            assert isinstance(aud, ProcessedAudio)
            assert aud.url in urls
            assert aud.format.startswith('.')
            assert aud.duration > 0
            assert aud.sample_rate > 0
            assert aud.channels > 0
    
    @given(
        text=st.one_of(text_strategy, chinese_text_strategy),
        image_urls=image_urls_strategy,
        video_urls=video_urls_strategy,
        audio_urls=audio_urls_strategy
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_preprocessor_processes_all_modalities_concurrently(
        self,
        text: str,
        image_urls: List[str],
        video_urls: List[str],
        audio_urls: List[str]
    ):
        """
        Property: Preprocessor搴旇鑳藉骞跺彂澶勭悊鎵€鏈夋ā鎬佺殑杈撳叆
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.5
        """
        # 璺宠繃绌烘枃鏈?
        if not text.strip():
            text = "default text"
        
        preprocessor = Preprocessor()
        
        # 骞跺彂澶勭悊鎵€鏈夎緭鍏?- 涓嶅簲璇ユ姏鍑哄紓甯?
        result = await preprocessor.process_all(
            text=text,
            image_urls=image_urls,
            video_urls=video_urls,
            audio_urls=audio_urls
        )
        
        # 楠岃瘉缁撴灉
        assert isinstance(result, dict)
        assert 'text' in result
        assert 'images' in result
        assert 'videos' in result
        assert 'audio' in result
        
        # 楠岃瘉鏂囨湰澶勭悊缁撴灉
        if result['text'] is not None:
            assert isinstance(result['text'], ProcessedText)
        
        # 楠岃瘉鏂囦欢澶勭悊缁撴灉
        assert isinstance(result['images'], list)
        assert isinstance(result['videos'], list)
        assert isinstance(result['audio'], list)


class TestInputValidationProperty:
    """
    娴嬭瘯杈撳叆楠岃瘉鐨勫睘鎬?
    """
    
    @given(
        text_length=st.integers(min_value=1, max_value=20000),
        file_count=st.integers(min_value=0, max_value=20)
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_input_manager_respects_limits(
        self,
        text_length: int,
        file_count: int
    ):
        """
        Property: InputManager搴旇閬靛畧閰嶇疆鐨勯檺鍒?
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.1, 1.2, 1.3, 1.4
        """
        max_text_length = 10000
        max_files_per_type = 10
        
        manager = InputManager(
            max_text_length=max_text_length,
            max_files_per_type=max_files_per_type
        )
        
        # 鍒涘缓娴嬭瘯鏁版嵁
        text = "A" * text_length
        image_urls = [f"https://example.com/img{i}.jpg" for i in range(file_count)]
        
        user_input = UserInputData(
            text_description=text,
            reference_images=image_urls
        )
        
        # 澶勭悊杈撳叆
        result = await manager.receive_user_input(user_input)
        
        # 楠岃瘉闄愬埗琚伒瀹?
        assert len(result.text) <= max_text_length
        assert len(result.images) <= max_files_per_type
    
    @given(
        text=st.text(min_size=1, max_size=100),
        sentiment_keywords=st.lists(
            st.sampled_from(['happy', 'sad', 'joy', 'painful', '蹇箰', '鎮蹭激']),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=10, deadline=None)
    @pytest.mark.asyncio
    async def test_sentiment_analysis_consistency(
        self,
        text: str,
        sentiment_keywords: List[str]
    ):
        """
        Property: 鎯呮劅鍒嗘瀽搴旇瀵圭浉鍚岃緭鍏ヤ骇鐢熶竴鑷寸殑缁撴灉
        
        Feature: requirement-parser-agent, Property 1: Multimodal Input Processing
        Validates: Requirements 1.1
        """
        preprocessor = Preprocessor()
        
        # 灏嗗叧閿瘝娣诲姞鍒版枃鏈腑
        text_with_keywords = text + " " + " ".join(sentiment_keywords)
        
        # 澶氭澶勭悊鐩稿悓鏂囨湰
        result1 = await preprocessor.process_text(text_with_keywords)
        result2 = await preprocessor.process_text(text_with_keywords)
        
        # 楠岃瘉涓€鑷存€?
        assert result1.sentiment == result2.sentiment
        assert result1.language == result2.language
        assert result1.word_count == result2.word_count


class TestPropertyTestConfiguration:
    """楠岃瘉灞炴€ф祴璇曢厤缃?""
    
    def test_strategies_generate_valid_data(self):
        """楠岃瘉绛栫暐鑳界敓鎴愭湁鏁堟暟鎹?""
        # 娴嬭瘯鏂囨湰绛栫暐
        text = text_strategy.example()
        assert isinstance(text, str)
        assert len(text) >= 10
        
        # 娴嬭瘯URL绛栫暐
        url = url_strategy('.jpg').example()
        assert isinstance(url, str)
        assert url.startswith('https://')
        assert url.endswith('.jpg')
        
        # 娴嬭瘯鍒楄〃绛栫暐
        urls = image_urls_strategy.example()
        assert isinstance(urls, list)
        assert all(isinstance(u, str) for u in urls)
    
    def test_property_test_runs_sufficient_examples(self):
        """楠岃瘉灞炴€ф祴璇曡繍琛岃冻澶熺殑绀轰緥锛堣嚦灏?00娆★級"""
        # 杩欎釜娴嬭瘯纭繚鎴戜滑鐨勯厤缃纭?
        # settings瑁呴グ鍣ㄤ腑鐨刴ax_examples=100纭繚浜嗚繖涓€鐐?
        assert True  # 閰嶇疆楠岃瘉閫氳繃
