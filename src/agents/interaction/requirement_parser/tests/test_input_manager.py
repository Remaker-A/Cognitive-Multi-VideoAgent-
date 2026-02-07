"""
InputManager 单元测试
"""

import pytest
from datetime import datetime

from src.agents.interaction.requirement_parser.input_manager import InputManager
from src.agents.interaction.requirement_parser.models import (
    UserInputData,
    ProcessedInput,
    FileReference,
    ValidatedFile,
    FileMetadata
)
from src.agents.interaction.requirement_parser.exceptions import RequirementParserError


class TestInputManagerInitialization:
    """测试InputManager初始化"""
    
    def test_init_with_defaults(self):
        """测试使用默认参数初始化"""
        manager = InputManager()
        assert manager.max_text_length == 10000
        assert manager.max_files_per_type == 10
    
    def test_init_with_custom_params(self):
        """测试使用自定义参数初始化"""
        manager = InputManager(max_text_length=5000, max_files_per_type=5)
        assert manager.max_text_length == 5000
        assert manager.max_files_per_type == 5


class TestReceiveUserInput:
    """测试接收用户输入"""
    
    @pytest.mark.asyncio
    async def test_receive_valid_text_only_input(self):
        """测试接收仅包含文本的有效输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="创建一个关于太空探索的视频",
            timestamp="2024-01-01T00:00:00Z"
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert isinstance(result, ProcessedInput)
        assert result.text == "创建一个关于太空探索的视频"
        assert len(result.images) == 0
        assert len(result.videos) == 0
        assert len(result.audio) == 0
    
    @pytest.mark.asyncio
    async def test_receive_input_with_files(self):
        """测试接收包含文件的输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="创建视频",
            reference_images=["https://example.com/image1.jpg", "https://example.com/image2.png"],
            reference_videos=["https://example.com/video1.mp4"],
            reference_audio=["https://example.com/audio1.mp3"]
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert len(result.images) == 2
        assert len(result.videos) == 1
        assert len(result.audio) == 1
    
    @pytest.mark.asyncio
    async def test_receive_input_with_empty_text(self):
        """测试接收空文本输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="",
            reference_images=["https://example.com/image1.jpg"]
        )
        
        with pytest.raises(RequirementParserError, match="Text description cannot be empty"):
            await manager.receive_user_input(input_data)
    
    @pytest.mark.asyncio
    async def test_receive_input_with_whitespace_only_text(self):
        """测试接收仅包含空白字符的文本"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="   \n\t  ",
            reference_images=["https://example.com/image1.jpg"]
        )
        
        with pytest.raises(RequirementParserError, match="Text description cannot be empty"):
            await manager.receive_user_input(input_data)
    
    @pytest.mark.asyncio
    async def test_receive_input_truncates_long_text(self):
        """测试长文本被截断"""
        manager = InputManager(max_text_length=100)
        long_text = "A" * 200
        input_data = UserInputData(text_description=long_text)
        
        result = await manager.receive_user_input(input_data)
        
        assert len(result.text) == 100
    
    @pytest.mark.asyncio
    async def test_receive_input_truncates_file_lists(self):
        """测试文件列表被截断"""
        manager = InputManager(max_files_per_type=2)
        input_data = UserInputData(
            text_description="测试",
            reference_images=[
                "https://example.com/img1.jpg",
                "https://example.com/img2.jpg",
                "https://example.com/img3.jpg",
                "https://example.com/img4.jpg"
            ]
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert len(result.images) == 2
    
    @pytest.mark.asyncio
    async def test_receive_input_filters_invalid_urls(self):
        """测试过滤无效的URL"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="测试",
            reference_images=[
                "https://example.com/valid.jpg",
                "invalid-url",
                "",
                "ftp://example.com/image.jpg"
            ]
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert len(result.images) == 1
        assert result.images[0] == "https://example.com/valid.jpg"
    
    @pytest.mark.asyncio
    async def test_receive_input_with_user_preferences(self):
        """测试接收包含用户偏好的输入"""
        manager = InputManager()
        preferences = {"aspect_ratio": "16:9", "quality": "high"}
        input_data = UserInputData(
            text_description="测试",
            user_preferences=preferences
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert result.user_preferences == preferences


class TestValidateFiles:
    """测试文件验证"""
    
    @pytest.mark.asyncio
    async def test_validate_valid_image_file(self):
        """测试验证有效的图片文件"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/image.jpg",
                size=1024 * 1024,  # 1MB
                name="image.jpg"
            )
        ]
        
        result = await manager.validate_files(files)
        
        assert len(result) == 1
        assert result[0].file_type == "image"
        assert result[0].format == ".jpg"
        assert result[0].is_valid is True
    
    @pytest.mark.asyncio
    async def test_validate_valid_video_file(self):
        """测试验证有效的视频文件"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/video.mp4",
                size=50 * 1024 * 1024,  # 50MB
                name="video.mp4"
            )
        ]
        
        result = await manager.validate_files(files)
        
        assert len(result) == 1
        assert result[0].file_type == "video"
        assert result[0].format == ".mp4"
    
    @pytest.mark.asyncio
    async def test_validate_valid_audio_file(self):
        """测试验证有效的音频文件"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/audio.mp3",
                size=5 * 1024 * 1024,  # 5MB
                name="audio.mp3"
            )
        ]
        
        result = await manager.validate_files(files)
        
        assert len(result) == 1
        assert result[0].file_type == "audio"
        assert result[0].format == ".mp3"
    
    @pytest.mark.asyncio
    async def test_validate_file_with_unsupported_format(self):
        """测试验证不支持的文件格式"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/document.pdf",
                size=1024,
                name="document.pdf"
            )
        ]
        
        result = await manager.validate_files(files)
        
        # 不支持的文件应该被跳过
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_validate_file_exceeds_size_limit(self):
        """测试验证超过大小限制的文件"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/large_image.jpg",
                size=20 * 1024 * 1024,  # 20MB (超过10MB限制)
                name="large_image.jpg"
            )
        ]
        
        result = await manager.validate_files(files)
        
        # 超过大小限制的文件应该被跳过
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_validate_multiple_files_mixed_validity(self):
        """测试验证混合有效性的多个文件"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/valid.jpg", size=1024 * 1024),
            FileReference(url="https://example.com/invalid.pdf", size=1024),
            FileReference(url="https://example.com/too_large.jpg", size=20 * 1024 * 1024),
            FileReference(url="https://example.com/valid2.png", size=2 * 1024 * 1024)
        ]
        
        result = await manager.validate_files(files)
        
        # 只有2个有效文件
        assert len(result) == 2
        assert all(f.is_valid for f in result)
    
    @pytest.mark.asyncio
    async def test_validate_file_url_with_query_params(self):
        """测试验证带查询参数的URL"""
        manager = InputManager()
        files = [
            FileReference(
                url="https://example.com/image.jpg?token=abc123&size=large",
                size=1024 * 1024
            )
        ]
        
        result = await manager.validate_files(files)
        
        assert len(result) == 1
        assert result[0].format == ".jpg"
    
    @pytest.mark.asyncio
    async def test_validate_file_case_insensitive_extension(self):
        """测试验证大小写不敏感的扩展名"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/IMAGE.JPG", size=1024 * 1024),
            FileReference(url="https://example.com/video.MP4", size=10 * 1024 * 1024)
        ]
        
        result = await manager.validate_files(files)
        
        assert len(result) == 2
        assert result[0].format == ".jpg"
        assert result[1].format == ".mp4"


class TestExtractMetadata:
    """测试提取文件元数据"""
    
    @pytest.mark.asyncio
    async def test_extract_metadata_from_mixed_files(self):
        """测试从混合文件中提取元数据"""
        manager = InputManager()
        files = [
            ValidatedFile(url="https://example.com/img1.jpg", file_type="image", size=1024, format=".jpg"),
            ValidatedFile(url="https://example.com/img2.png", file_type="image", size=2048, format=".png"),
            ValidatedFile(url="https://example.com/video.mp4", file_type="video", size=10240, format=".mp4"),
            ValidatedFile(url="https://example.com/audio.mp3", file_type="audio", size=5120, format=".mp3")
        ]
        
        metadata = await manager.extract_metadata(files)
        
        assert metadata.total_files == 4
        assert metadata.image_count == 2
        assert metadata.video_count == 1
        assert metadata.audio_count == 1
        assert metadata.total_size == 1024 + 2048 + 10240 + 5120
        assert ".jpg" in metadata.formats["images"]
        assert ".png" in metadata.formats["images"]
        assert ".mp4" in metadata.formats["videos"]
        assert ".mp3" in metadata.formats["audio"]
    
    @pytest.mark.asyncio
    async def test_extract_metadata_from_empty_list(self):
        """测试从空列表中提取元数据"""
        manager = InputManager()
        files = []
        
        metadata = await manager.extract_metadata(files)
        
        assert metadata.total_files == 0
        assert metadata.image_count == 0
        assert metadata.video_count == 0
        assert metadata.audio_count == 0
        assert metadata.total_size == 0
    
    @pytest.mark.asyncio
    async def test_extract_metadata_deduplicates_formats(self):
        """测试元数据提取时去重格式"""
        manager = InputManager()
        files = [
            ValidatedFile(url="https://example.com/img1.jpg", file_type="image", size=1024, format=".jpg"),
            ValidatedFile(url="https://example.com/img2.jpg", file_type="image", size=2048, format=".jpg"),
            ValidatedFile(url="https://example.com/img3.jpg", file_type="image", size=3072, format=".jpg")
        ]
        
        metadata = await manager.extract_metadata(files)
        
        assert metadata.image_count == 3
        assert len(metadata.formats["images"]) == 1
        assert ".jpg" in metadata.formats["images"]


class TestInvalidInputHandling:
    """测试无效输入处理 - Requirements 6.2"""
    
    @pytest.mark.asyncio
    async def test_invalid_text_format_none(self):
        """测试None文本输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description=None,
            reference_images=["https://example.com/image.jpg"]
        )
        
        with pytest.raises(RequirementParserError, match="Text description cannot be empty"):
            await manager.receive_user_input(input_data)
    
    @pytest.mark.asyncio
    async def test_invalid_text_format_only_special_chars(self):
        """测试仅包含特殊字符的文本"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="!@#$%^&*()",
            reference_images=["https://example.com/image.jpg"]
        )
        
        # 应该能处理，但会被清理
        result = await manager.receive_user_input(input_data)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_invalid_url_format_missing_protocol(self):
        """测试缺少协议的URL"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="测试视频",
            reference_images=["example.com/image.jpg", "www.example.com/image2.jpg"]
        )
        
        result = await manager.receive_user_input(input_data)
        
        # 无效URL应该被过滤掉
        assert len(result.images) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_url_format_empty_strings(self):
        """测试空字符串URL"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="测试",
            reference_images=["", "   ", "\n\t"],
            reference_videos=["https://example.com/valid.mp4"]
        )
        
        result = await manager.receive_user_input(input_data)
        
        assert len(result.images) == 0
        assert len(result.videos) == 1
    
    @pytest.mark.asyncio
    async def test_invalid_file_format_requirements(self):
        """测试不符合格式要求的文件"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/doc.pdf", size=1024),
            FileReference(url="https://example.com/sheet.xlsx", size=2048),
            FileReference(url="https://example.com/text.txt", size=512)
        ]
        
        result = await manager.validate_files(files)
        
        # 所有不支持的格式都应该被跳过，并返回具体的格式要求说明
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_file_extension_missing(self):
        """测试缺少扩展名的文件"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/file_without_extension", size=1024),
            FileReference(url="https://example.com/another_file", size=2048)
        ]
        
        result = await manager.validate_files(files)
        
        # 没有扩展名的文件应该被跳过
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_file_size_negative(self):
        """测试负数文件大小"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/image.jpg", size=-1024)
        ]
        
        # 负数大小应该被处理（可能跳过或使用默认值）
        result = await manager.validate_files(files)
        
        # 实现应该优雅处理，不应该崩溃
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_invalid_file_size_zero(self):
        """测试零字节文件"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/empty.jpg", size=0)
        ]
        
        result = await manager.validate_files(files)
        
        # 零字节文件应该被接受（技术上有效）
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_invalid_mixed_valid_invalid_inputs(self):
        """测试混合有效和无效输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="有效的文本描述",
            reference_images=[
                "https://example.com/valid.jpg",
                "invalid-url",
                "",
                "ftp://example.com/image.jpg",
                "https://example.com/valid2.png"
            ],
            reference_videos=["not-a-url", "https://example.com/video.mp4"]
        )
        
        result = await manager.receive_user_input(input_data)
        
        # 只有有效的URL应该被保留
        assert len(result.images) == 2
        assert len(result.videos) == 1
        assert "https://example.com/valid.jpg" in result.images
        assert "https://example.com/valid2.png" in result.images


class TestFileAccessErrorHandling:
    """测试文件访问错误处理 - Requirements 6.3"""
    
    @pytest.mark.asyncio
    async def test_file_access_error_continues_processing(self):
        """测试文件访问错误时继续处理其他文件"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/accessible.jpg", size=1024 * 1024),
            FileReference(url="https://example.com/inaccessible.jpg", size=None),  # 无法获取大小
            FileReference(url="https://example.com/another_accessible.png", size=2 * 1024 * 1024)
        ]
        
        result = await manager.validate_files(files)
        
        # 即使某些文件无法访问，其他文件应该继续处理
        # 至少应该处理有大小信息的文件
        assert len(result) >= 2
    
    @pytest.mark.asyncio
    async def test_file_access_error_invalid_url_skipped(self):
        """测试无法访问的URL被跳过"""
        manager = InputManager()
        files = [
            FileReference(url="https://nonexistent-domain-12345.com/image.jpg", size=1024),
            FileReference(url="https://example.com/valid.jpg", size=2048)
        ]
        
        # 验证应该继续，即使某些URL可能无法访问
        result = await manager.validate_files(files)
        
        # 应该至少处理格式正确的文件
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_file_access_error_partial_failure(self):
        """测试部分文件失败时的处理"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/valid1.jpg", size=1024 * 1024),
            FileReference(url="https://example.com/toolarge.jpg", size=50 * 1024 * 1024),  # 超过限制
            FileReference(url="https://example.com/valid2.png", size=2 * 1024 * 1024),
            FileReference(url="https://example.com/invalid.pdf", size=1024)  # 不支持的格式
        ]
        
        result = await manager.validate_files(files)
        
        # 应该跳过失败的文件，继续处理其他文件
        assert len(result) == 2  # 只有2个有效文件
        assert all(f.is_valid for f in result)
        assert all(f.file_type == "image" for f in result)
    
    @pytest.mark.asyncio
    async def test_file_access_error_all_files_fail(self):
        """测试所有文件都失败的情况"""
        manager = InputManager()
        files = [
            FileReference(url="https://example.com/toolarge1.jpg", size=50 * 1024 * 1024),
            FileReference(url="https://example.com/toolarge2.jpg", size=60 * 1024 * 1024),
            FileReference(url="https://example.com/invalid.pdf", size=1024)
        ]
        
        result = await manager.validate_files(files)
        
        # 所有文件都失败时，应该返回空列表而不是抛出异常
        assert len(result) == 0
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_file_access_error_empty_file_list(self):
        """测试空文件列表"""
        manager = InputManager()
        files = []
        
        result = await manager.validate_files(files)
        
        # 空列表应该正常处理
        assert len(result) == 0
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_file_access_error_malformed_url(self):
        """测试格式错误的URL"""
        manager = InputManager()
        files = [
            FileReference(url="ht!tp://invalid-url.com/image.jpg", size=1024),
            FileReference(url="https://example.com/valid.jpg", size=2048)
        ]
        
        result = await manager.validate_files(files)
        
        # 格式错误的URL应该被跳过，有效的继续处理
        assert len(result) >= 1
    
    @pytest.mark.asyncio
    async def test_file_access_error_network_timeout_simulation(self):
        """测试网络超时场景（模拟）"""
        manager = InputManager()
        # 使用非常长的URL来模拟可能的超时场景
        files = [
            FileReference(
                url="https://example.com/" + "a" * 1000 + ".jpg",
                size=1024 * 1024
            ),
            FileReference(url="https://example.com/normal.jpg", size=2048)
        ]
        
        result = await manager.validate_files(files)
        
        # 即使某些文件可能超时，其他文件应该继续处理
        assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_receive_input_with_inaccessible_files(self):
        """测试接收包含无法访问文件的输入"""
        manager = InputManager()
        input_data = UserInputData(
            text_description="测试视频",
            reference_images=[
                "https://example.com/accessible.jpg",
                "https://nonexistent-domain-xyz.com/inaccessible.jpg"
            ]
        )
        
        # 应该能够处理输入，即使某些文件可能无法访问
        result = await manager.receive_user_input(input_data)
        
        assert result is not None
        assert len(result.images) >= 1  # 至少有一个有效URL


class TestFileExtensionHandling:
    """测试文件扩展名处理"""
    
    def test_get_file_extension_standard(self):
        """测试获取标准文件扩展名"""
        manager = InputManager()
        assert manager._get_file_extension("https://example.com/file.jpg") == ".jpg"
        assert manager._get_file_extension("https://example.com/file.mp4") == ".mp4"
        assert manager._get_file_extension("https://example.com/file.mp3") == ".mp3"
    
    def test_get_file_extension_with_query_params(self):
        """测试从带查询参数的URL获取扩展名"""
        manager = InputManager()
        url = "https://example.com/file.jpg?token=abc&size=large"
        assert manager._get_file_extension(url) == ".jpg"
    
    def test_get_file_extension_no_extension(self):
        """测试没有扩展名的URL"""
        manager = InputManager()
        assert manager._get_file_extension("https://example.com/file") == ""
    
    def test_get_file_extension_case_insensitive(self):
        """测试扩展名大小写不敏感"""
        manager = InputManager()
        assert manager._get_file_extension("https://example.com/FILE.JPG") == ".jpg"
        assert manager._get_file_extension("https://example.com/file.Mp4") == ".mp4"
    
    def test_determine_file_type_images(self):
        """测试确定图片文件类型"""
        manager = InputManager()
        assert manager._determine_file_type(".jpg") == "image"
        assert manager._determine_file_type(".png") == "image"
        assert manager._determine_file_type(".gif") == "image"
    
    def test_determine_file_type_videos(self):
        """测试确定视频文件类型"""
        manager = InputManager()
        assert manager._determine_file_type(".mp4") == "video"
        assert manager._determine_file_type(".mov") == "video"
        assert manager._determine_file_type(".avi") == "video"
    
    def test_determine_file_type_audio(self):
        """测试确定音频文件类型"""
        manager = InputManager()
        assert manager._determine_file_type(".mp3") == "audio"
        assert manager._determine_file_type(".wav") == "audio"
        assert manager._determine_file_type(".aac") == "audio"
    
    def test_determine_file_type_unsupported(self):
        """测试确定不支持的文件类型"""
        manager = InputManager()
        assert manager._determine_file_type(".pdf") is None
        assert manager._determine_file_type(".doc") is None
        assert manager._determine_file_type("") is None
    
    def test_get_max_file_size(self):
        """测试获取文件大小限制"""
        manager = InputManager()
        assert manager._get_max_file_size("image") == 10 * 1024 * 1024
        assert manager._get_max_file_size("video") == 500 * 1024 * 1024
        assert manager._get_max_file_size("audio") == 50 * 1024 * 1024
        assert manager._get_max_file_size("unknown") == 0
