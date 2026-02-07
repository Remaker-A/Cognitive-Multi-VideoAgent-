"""
输入管理器模块

负责接收和验证用户输入，统一输入格式
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

from .models import UserInputData, ProcessedInput, FileReference, ValidatedFile, FileMetadata
from .exceptions import RequirementParserError, ConfigurationError
from .utils import validate_file_format, format_file_size, clean_text
from .logger import setup_logger

logger = setup_logger(__name__)


class InputManager:
    """
    输入管理器
    
    职责：
    - 接收和验证用户输入
    - 统一输入格式
    - 验证文件格式和大小
    - 提取文件元数据
    """
    
    # 支持的文件格式
    SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    SUPPORTED_VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.aac', '.flac', '.ogg', '.m4a']
    
    # 文件大小限制（字节）
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 500 * 1024 * 1024  # 500MB
    MAX_AUDIO_SIZE = 50 * 1024 * 1024  # 50MB
    
    def __init__(
        self,
        max_text_length: int = 10000,
        max_files_per_type: int = 10
    ):
        """
        初始化输入管理器
        
        Args:
            max_text_length: 最大文本长度
            max_files_per_type: 每种类型的最大文件数
        """
        self.max_text_length = max_text_length
        self.max_files_per_type = max_files_per_type
        logger.info(
            "InputManager initialized",
            extra={
                "max_text_length": max_text_length,
                "max_files_per_type": max_files_per_type
            }
        )
    
    async def receive_user_input(self, input_data: UserInputData) -> ProcessedInput:
        """
        接收用户输入并进行初步验证
        
        Args:
            input_data: 用户输入数据
        
        Returns:
            ProcessedInput: 处理后的输入数据
        
        Raises:
            RequirementParserError: 输入验证失败
        """
        logger.info("Receiving user input", extra={"timestamp": input_data.timestamp})
        
        try:
            # 验证文本输入
            validated_text = self._validate_text(input_data.text_description)
            
            # 验证文件引用
            validated_images = await self._validate_file_references(
                input_data.reference_images,
                "image"
            )
            validated_videos = await self._validate_file_references(
                input_data.reference_videos,
                "video"
            )
            validated_audio = await self._validate_file_references(
                input_data.reference_audio,
                "audio"
            )
            
            # 构建处理后的输入
            processed_input = ProcessedInput(
                text=validated_text,
                images=validated_images,
                videos=validated_videos,
                audio=validated_audio,
                user_preferences=input_data.user_preferences or {},
                timestamp=input_data.timestamp or datetime.utcnow().isoformat(),
                metadata={}
            )
            
            logger.info(
                "User input received successfully",
                extra={
                    "text_length": len(validated_text),
                    "image_count": len(validated_images),
                    "video_count": len(validated_videos),
                    "audio_count": len(validated_audio)
                }
            )
            
            return processed_input
            
        except Exception as e:
            logger.error(f"Failed to receive user input: {e}")
            raise RequirementParserError(f"Input validation failed: {e}")
    
    def _validate_text(self, text: str) -> str:
        """
        验证文本输入
        
        Args:
            text: 输入文本
        
        Returns:
            str: 验证后的文本
        
        Raises:
            RequirementParserError: 文本验证失败
        """
        if not text or not text.strip():
            raise RequirementParserError("Text description cannot be empty")
        
        cleaned_text = clean_text(text)
        
        if len(cleaned_text) > self.max_text_length:
            logger.warning(
                f"Text length ({len(cleaned_text)}) exceeds maximum ({self.max_text_length}), truncating"
            )
            cleaned_text = cleaned_text[:self.max_text_length]
        
        return cleaned_text
    
    async def _validate_file_references(
        self,
        file_refs: List[str],
        file_type: str
    ) -> List[str]:
        """
        验证文件引用列表
        
        Args:
            file_refs: 文件引用列表（URLs）
            file_type: 文件类型（image/video/audio）
        
        Returns:
            List[str]: 验证后的文件引用列表
        
        Raises:
            RequirementParserError: 文件引用验证失败
        """
        if not file_refs:
            return []
        
        if len(file_refs) > self.max_files_per_type:
            logger.warning(
                f"{file_type} count ({len(file_refs)}) exceeds maximum ({self.max_files_per_type}), truncating"
            )
            file_refs = file_refs[:self.max_files_per_type]
        
        validated_refs = []
        for ref in file_refs:
            if not ref or not ref.strip():
                logger.warning(f"Skipping empty {file_type} reference")
                continue
            
            # 基础URL验证
            if not (ref.startswith('http://') or ref.startswith('https://') or ref.startswith('s3://')):
                logger.warning(f"Invalid {file_type} URL format: {ref}")
                continue
            
            validated_refs.append(ref.strip())
        
        return validated_refs
    
    async def validate_files(self, files: List[FileReference]) -> List[ValidatedFile]:
        """
        验证上传文件的格式和大小
        
        Args:
            files: 文件引用列表
        
        Returns:
            List[ValidatedFile]: 验证后的文件列表
        
        Raises:
            RequirementParserError: 文件验证失败
        """
        logger.info(f"Validating {len(files)} files")
        
        validated_files = []
        
        for file_ref in files:
            try:
                validated_file = await self._validate_single_file(file_ref)
                validated_files.append(validated_file)
            except Exception as e:
                logger.warning(f"File validation failed for {file_ref.url}: {e}")
                # 继续处理其他文件，不中断整个流程
                continue
        
        logger.info(f"Successfully validated {len(validated_files)}/{len(files)} files")
        return validated_files
    
    async def _validate_single_file(self, file_ref: FileReference) -> ValidatedFile:
        """
        验证单个文件
        
        Args:
            file_ref: 文件引用
        
        Returns:
            ValidatedFile: 验证后的文件
        
        Raises:
            RequirementParserError: 文件验证失败
        """
        # 验证文件格式
        file_extension = self._get_file_extension(file_ref.url)
        file_type = self._determine_file_type(file_extension)
        
        if not file_type:
            raise RequirementParserError(f"Unsupported file format: {file_extension}")
        
        # 验证文件大小
        max_size = self._get_max_file_size(file_type)
        if file_ref.size and file_ref.size > max_size:
            raise RequirementParserError(
                f"File size ({format_file_size(file_ref.size)}) exceeds maximum "
                f"({format_file_size(max_size)}) for {file_type}"
            )
        
        return ValidatedFile(
            url=file_ref.url,
            file_type=file_type,
            size=file_ref.size,
            format=file_extension,
            is_valid=True,
            validation_message="File validated successfully"
        )
    
    def _get_file_extension(self, url: str) -> str:
        """
        从URL中提取文件扩展名
        
        Args:
            url: 文件URL
        
        Returns:
            str: 文件扩展名（小写，包含点）
        """
        # 移除查询参数
        url_without_params = url.split('?')[0]
        
        # 提取文件名部分（最后一个/之后的内容）
        if '/' in url_without_params:
            filename = url_without_params.rsplit('/', 1)[-1]
        else:
            filename = url_without_params
        
        # 提取扩展名
        if '.' in filename:
            extension = '.' + filename.rsplit('.', 1)[-1].lower()
            return extension
        
        return ''
    
    def _determine_file_type(self, extension: str) -> Optional[str]:
        """
        根据扩展名确定文件类型
        
        Args:
            extension: 文件扩展名
        
        Returns:
            Optional[str]: 文件类型（image/video/audio）或None
        """
        if extension in self.SUPPORTED_IMAGE_FORMATS:
            return "image"
        elif extension in self.SUPPORTED_VIDEO_FORMATS:
            return "video"
        elif extension in self.SUPPORTED_AUDIO_FORMATS:
            return "audio"
        return None
    
    def _get_max_file_size(self, file_type: str) -> int:
        """
        获取文件类型的最大大小限制
        
        Args:
            file_type: 文件类型
        
        Returns:
            int: 最大文件大小（字节）
        """
        size_limits = {
            "image": self.MAX_IMAGE_SIZE,
            "video": self.MAX_VIDEO_SIZE,
            "audio": self.MAX_AUDIO_SIZE
        }
        return size_limits.get(file_type, 0)
    
    async def extract_metadata(self, files: List[ValidatedFile]) -> FileMetadata:
        """
        提取文件基础元数据
        
        Args:
            files: 验证后的文件列表
        
        Returns:
            FileMetadata: 文件元数据
        """
        logger.info(f"Extracting metadata from {len(files)} files")
        
        # 按类型分组
        images = [f for f in files if f.file_type == "image"]
        videos = [f for f in files if f.file_type == "video"]
        audio = [f for f in files if f.file_type == "audio"]
        
        # 计算总大小
        total_size = sum(f.size for f in files if f.size)
        
        metadata = FileMetadata(
            total_files=len(files),
            image_count=len(images),
            video_count=len(videos),
            audio_count=len(audio),
            total_size=total_size,
            formats={
                "images": list(set(f.format for f in images)),
                "videos": list(set(f.format for f in videos)),
                "audio": list(set(f.format for f in audio))
            }
        )
        
        logger.info(
            "Metadata extracted",
            extra={
                "total_files": metadata.total_files,
                "total_size": format_file_size(metadata.total_size)
            }
        )
        
        return metadata
