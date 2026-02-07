"""
Preprocessor 单元测试
"""

import pytest

from src.agents.interaction.requirement_parser.preprocessor import Preprocessor
from src.agents.interaction.requirement_parser.models import (
    ProcessedText,
    ProcessedImage,
    ProcessedVideo,
    ProcessedAudio
)


class TestPreprocessorInitialization:
    """测试Preprocessor初始化"""
    
    def test_init(self):
        """测试初始化"""
        preprocessor = Preprocessor()
        assert preprocessor is not None


class TestProcessText:
    """测试文本处理"""
    
    @pytest.mark.asyncio
    async def test_process_simple_chinese_text(self):
        """测试处理简单中文文本"""
        preprocessor = Preprocessor()
        text = "创建一个关于太空探索的视频"
        
        result = await preprocessor.process_text(text)
        
        assert isinstance(result, ProcessedText)
        assert result.original == text
        assert result.cleaned == text
        assert result.language == "zh"
        assert result.word_count > 0
        assert isinstance(result.key_phrases, list)
        assert result.sentiment in ["positive", "negative", "neutral"]
    
    @pytest.mark.asyncio
    async def test_process_english_text(self):
        """测试处理英文文本"""
        preprocessor = Preprocessor()
        text = "Create a video about space exploration"
        
        result = await preprocessor.process_text(text)
        
        assert isinstance(result, ProcessedText)
        assert result.language == "en"
        assert result.word_count == 6
    
    @pytest.mark.asyncio
    async def test_process_text_with_extra_whitespace(self):
        """测试处理包含多余空白的文本"""
        preprocessor = Preprocessor()
        text = "  创建   一个   视频  \n\n  "
        
        result = await preprocessor.process_text(text)
        
        assert result.cleaned == "创建 一个 视频"
        assert result.word_count == 3
    
    @pytest.mark.asyncio
    async def test_process_positive_sentiment_text(self):
        """测试处理积极情感文本"""
        preprocessor = Preprocessor()
        text = "创建一个快乐、美好、温馨的家庭聚会视频"
        
        result = await preprocessor.process_text(text)
        
        assert result.sentiment == "positive"
    
    @pytest.mark.asyncio
    async def test_process_negative_sentiment_text(self):
        """测试处理消极情感文本"""
        preprocessor = Preprocessor()
        text = "一个悲伤、痛苦、可怕的故事"
        
        result = await preprocessor.process_text(text)
        
        assert result.sentiment == "negative"
    
    @pytest.mark.asyncio
    async def test_process_neutral_sentiment_text(self):
        """测试处理中性情感文本"""
        preprocessor = Preprocessor()
        text = "创建一个关于技术的视频"
        
        result = await preprocessor.process_text(text)
        
        assert result.sentiment == "neutral"
    
    @pytest.mark.asyncio
    async def test_process_text_extracts_key_phrases(self):
        """测试提取关键短语"""
        preprocessor = Preprocessor()
        text = "创建一个关于太空探索的科幻视频，包含宇宙飞船和外星人"
        
        result = await preprocessor.process_text(text)
        
        assert len(result.key_phrases) > 0
        # 关键短语应该包含重要词汇
        key_phrases_str = " ".join(result.key_phrases)
        assert any(word in key_phrases_str for word in ["太空", "探索", "科幻", "视频"])


class TestProcessImages:
    """测试图片处理"""
    
    @pytest.mark.asyncio
    async def test_process_empty_image_list(self):
        """测试处理空图片列表"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_images([])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_process_single_image(self):
        """测试处理单个图片"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/image.jpg"]
        
        result = await preprocessor.process_images(urls)
        
        assert len(result) == 1
        assert isinstance(result[0], ProcessedImage)
        assert result[0].url == urls[0]
        assert result[0].format == ".jpg"
        assert result[0].width > 0
        assert result[0].height > 0
    
    @pytest.mark.asyncio
    async def test_process_multiple_images(self):
        """测试处理多个图片"""
        preprocessor = Preprocessor()
        urls = [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
            "https://example.com/image3.gif"
        ]
        
        result = await preprocessor.process_images(urls)
        
        assert len(result) == 3
        assert result[0].format == ".jpg"
        assert result[1].format == ".png"
        assert result[2].format == ".gif"
    
    @pytest.mark.asyncio
    async def test_process_image_with_query_params(self):
        """测试处理带查询参数的图片URL"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/image.jpg?size=large&token=abc123"]
        
        result = await preprocessor.process_images(urls)
        
        assert len(result) == 1
        assert result[0].format == ".jpg"
    
    @pytest.mark.asyncio
    async def test_process_image_metadata(self):
        """测试图片元数据"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/image.jpg"]
        
        result = await preprocessor.process_images(urls)
        
        assert result[0].metadata["source_url"] == urls[0]
        assert result[0].metadata["processed"] is True


class TestProcessVideos:
    """测试视频处理"""
    
    @pytest.mark.asyncio
    async def test_process_empty_video_list(self):
        """测试处理空视频列表"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_videos([])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_process_single_video(self):
        """测试处理单个视频"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/video.mp4"]
        
        result = await preprocessor.process_videos(urls)
        
        assert len(result) == 1
        assert isinstance(result[0], ProcessedVideo)
        assert result[0].url == urls[0]
        assert result[0].format == ".mp4"
        assert result[0].duration > 0
        assert result[0].fps > 0
    
    @pytest.mark.asyncio
    async def test_process_multiple_videos(self):
        """测试处理多个视频"""
        preprocessor = Preprocessor()
        urls = [
            "https://example.com/video1.mp4",
            "https://example.com/video2.mov",
            "https://example.com/video3.avi"
        ]
        
        result = await preprocessor.process_videos(urls)
        
        assert len(result) == 3
        assert result[0].format == ".mp4"
        assert result[1].format == ".mov"
        assert result[2].format == ".avi"
    
    @pytest.mark.asyncio
    async def test_process_video_metadata(self):
        """测试视频元数据"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/video.mp4"]
        
        result = await preprocessor.process_videos(urls)
        
        assert result[0].metadata["source_url"] == urls[0]
        assert result[0].metadata["processed"] is True
        assert result[0].width > 0
        assert result[0].height > 0


class TestProcessAudio:
    """测试音频处理"""
    
    @pytest.mark.asyncio
    async def test_process_empty_audio_list(self):
        """测试处理空音频列表"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_audio([])
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_process_single_audio(self):
        """测试处理单个音频"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/audio.mp3"]
        
        result = await preprocessor.process_audio(urls)
        
        assert len(result) == 1
        assert isinstance(result[0], ProcessedAudio)
        assert result[0].url == urls[0]
        assert result[0].format == ".mp3"
        assert result[0].duration > 0
        assert result[0].sample_rate > 0
        assert result[0].channels > 0
    
    @pytest.mark.asyncio
    async def test_process_multiple_audio(self):
        """测试处理多个音频"""
        preprocessor = Preprocessor()
        urls = [
            "https://example.com/audio1.mp3",
            "https://example.com/audio2.wav",
            "https://example.com/audio3.aac"
        ]
        
        result = await preprocessor.process_audio(urls)
        
        assert len(result) == 3
        assert result[0].format == ".mp3"
        assert result[1].format == ".wav"
        assert result[2].format == ".aac"
    
    @pytest.mark.asyncio
    async def test_process_audio_metadata(self):
        """测试音频元数据"""
        preprocessor = Preprocessor()
        urls = ["https://example.com/audio.mp3"]
        
        result = await preprocessor.process_audio(urls)
        
        assert result[0].metadata["source_url"] == urls[0]
        assert result[0].metadata["processed"] is True


class TestExtractFormatFromUrl:
    """测试从URL提取格式"""
    
    def test_extract_format_standard_url(self):
        """测试从标准URL提取格式"""
        preprocessor = Preprocessor()
        
        assert preprocessor._extract_format_from_url("https://example.com/file.jpg") == ".jpg"
        assert preprocessor._extract_format_from_url("https://example.com/file.mp4") == ".mp4"
        assert preprocessor._extract_format_from_url("https://example.com/file.mp3") == ".mp3"
    
    def test_extract_format_with_query_params(self):
        """测试从带查询参数的URL提取格式"""
        preprocessor = Preprocessor()
        url = "https://example.com/file.jpg?token=abc&size=large"
        
        assert preprocessor._extract_format_from_url(url) == ".jpg"
    
    def test_extract_format_no_extension(self):
        """测试从无扩展名的URL提取格式"""
        preprocessor = Preprocessor()
        url = "https://example.com/file"
        
        assert preprocessor._extract_format_from_url(url) == ".unknown"
    
    def test_extract_format_case_insensitive(self):
        """测试格式提取大小写不敏感"""
        preprocessor = Preprocessor()
        
        assert preprocessor._extract_format_from_url("https://example.com/FILE.JPG") == ".jpg"
        assert preprocessor._extract_format_from_url("https://example.com/file.Mp4") == ".mp4"


class TestProcessAll:
    """测试处理所有输入"""
    
    @pytest.mark.asyncio
    async def test_process_all_with_complete_input(self):
        """测试处理完整输入"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_all(
            text="创建一个视频",
            image_urls=["https://example.com/img.jpg"],
            video_urls=["https://example.com/vid.mp4"],
            audio_urls=["https://example.com/aud.mp3"]
        )
        
        assert "text" in result
        assert "images" in result
        assert "videos" in result
        assert "audio" in result
        
        assert isinstance(result["text"], ProcessedText)
        assert len(result["images"]) == 1
        assert len(result["videos"]) == 1
        assert len(result["audio"]) == 1
    
    @pytest.mark.asyncio
    async def test_process_all_with_text_only(self):
        """测试仅处理文本"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_all(
            text="创建一个视频",
            image_urls=[],
            video_urls=[],
            audio_urls=[]
        )
        
        assert isinstance(result["text"], ProcessedText)
        assert result["images"] == []
        assert result["videos"] == []
        assert result["audio"] == []
    
    @pytest.mark.asyncio
    async def test_process_all_with_multiple_files(self):
        """测试处理多个文件"""
        preprocessor = Preprocessor()
        
        result = await preprocessor.process_all(
            text="创建视频",
            image_urls=[
                "https://example.com/img1.jpg",
                "https://example.com/img2.png"
            ],
            video_urls=[
                "https://example.com/vid1.mp4",
                "https://example.com/vid2.mov"
            ],
            audio_urls=[
                "https://example.com/aud1.mp3"
            ]
        )
        
        assert len(result["images"]) == 2
        assert len(result["videos"]) == 2
        assert len(result["audio"]) == 1


class TestSentimentAnalysis:
    """测试情感分析"""
    
    def test_analyze_positive_sentiment(self):
        """测试分析积极情感"""
        preprocessor = Preprocessor()
        
        assert preprocessor._analyze_sentiment("这是一个快乐的故事") == "positive"
        assert preprocessor._analyze_sentiment("This is a happy story") == "positive"
    
    def test_analyze_negative_sentiment(self):
        """测试分析消极情感"""
        preprocessor = Preprocessor()
        
        assert preprocessor._analyze_sentiment("这是一个悲伤的故事") == "negative"
        assert preprocessor._analyze_sentiment("This is a sad story") == "negative"
    
    def test_analyze_neutral_sentiment(self):
        """测试分析中性情感"""
        preprocessor = Preprocessor()
        
        assert preprocessor._analyze_sentiment("这是一个技术文档") == "neutral"
        assert preprocessor._analyze_sentiment("This is a technical document") == "neutral"
    
    def test_analyze_mixed_sentiment_positive_dominant(self):
        """测试分析混合情感（积极占主导）"""
        preprocessor = Preprocessor()
        
        text = "虽然有些悲伤，但整体是快乐、美好、温馨的"
        assert preprocessor._analyze_sentiment(text) == "positive"
    
    def test_analyze_mixed_sentiment_negative_dominant(self):
        """测试分析混合情感（消极占主导）"""
        preprocessor = Preprocessor()
        
        text = "虽然有些快乐，但整体是悲伤、痛苦、可怕的"
        assert preprocessor._analyze_sentiment(text) == "negative"
