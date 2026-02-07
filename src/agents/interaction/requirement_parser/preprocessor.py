"""
预处理器模块

负责对输入数据进行预处理，为模型分析做准备
"""

import asyncio
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse

from .models import ProcessedText, ProcessedImage, ProcessedVideo, ProcessedAudio
from .utils import clean_text, extract_key_phrases, detect_language
from .logger import setup_logger

logger = setup_logger(__name__)


class Preprocessor:
    """
    预处理器
    
    职责：
    - 清理和标准化文本输入
    - 处理图片URL和基础信息
    - 处理视频URL和基础信息
    - 处理音频URL和基础信息
    
    注意：此实现为简化版本，主要处理URL和元数据
    实际的图片/视频/音频内容分析将在后续版本中通过外部服务实现
    """
    
    def __init__(self):
        """初始化预处理器"""
        logger.info("Preprocessor initialized")
    
    async def process_text(self, text: str) -> ProcessedText:
        """
        清理和标准化文本输入
        
        Args:
            text: 原始文本
        
        Returns:
            ProcessedText: 处理后的文本数据
        """
        logger.info("Processing text input", extra={"text_length": len(text)})
        
        try:
            # 清理文本
            cleaned = clean_text(text)
            
            # 检测语言
            language = detect_language(cleaned)
            
            # 计算词数
            word_count = len(cleaned.split())
            
            # 提取关键短语
            key_phrases = extract_key_phrases(cleaned)
            
            # 简单的情感分析（基于关键词）
            sentiment = self._analyze_sentiment(cleaned)
            
            processed = ProcessedText(
                original=text,
                cleaned=cleaned,
                language=language,
                word_count=word_count,
                key_phrases=key_phrases,
                sentiment=sentiment
            )
            
            logger.info(
                "Text processing completed",
                extra={
                    "language": language,
                    "word_count": word_count,
                    "key_phrases_count": len(key_phrases)
                }
            )
            
            return processed
            
        except Exception as e:
            logger.error(f"Failed to process text: {e}")
            # 返回基础处理结果
            return ProcessedText(
                original=text,
                cleaned=clean_text(text),
                language="unknown",
                word_count=len(text.split()),
                key_phrases=[],
                sentiment="neutral"
            )
    
    def _analyze_sentiment(self, text: str) -> str:
        """
        简单的情感分析
        
        Args:
            text: 文本内容
        
        Returns:
            str: 情感标签（positive/negative/neutral）
        """
        # 简单的关键词匹配
        positive_keywords = [
            "开心", "快乐", "美好", "温馨", "欢乐", "喜悦", "幸福",
            "happy", "joy", "wonderful", "beautiful", "cheerful"
        ]
        negative_keywords = [
            "悲伤", "难过", "痛苦", "恐怖", "可怕", "悲惨",
            "sad", "painful", "terrible", "horrible", "tragic"
        ]
        
        text_lower = text.lower()
        
        positive_count = sum(1 for kw in positive_keywords if kw in text_lower)
        negative_count = sum(1 for kw in negative_keywords if kw in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def process_images(self, image_urls: List[str]) -> List[ProcessedImage]:
        """
        处理图片URL和基础信息
        
        Args:
            image_urls: 图片URL列表
        
        Returns:
            List[ProcessedImage]: 处理后的图片数据列表
        
        注意：此实现为简化版本，仅处理URL和基础元数据
        实际的图片内容分析（尺寸、颜色等）需要外部服务支持
        """
        logger.info(f"Processing {len(image_urls)} images")
        
        if not image_urls:
            return []
        
        processed_images = []
        
        for url in image_urls:
            try:
                processed = await self._process_single_image(url)
                processed_images.append(processed)
            except Exception as e:
                logger.warning(f"Failed to process image {url}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_images)}/{len(image_urls)} images")
        return processed_images
    
    async def _process_single_image(self, url: str) -> ProcessedImage:
        """
        处理单个图片
        
        Args:
            url: 图片URL
        
        Returns:
            ProcessedImage: 处理后的图片数据
        """
        # 从URL提取格式
        format_ext = self._extract_format_from_url(url)
        
        # 创建处理后的图片对象（使用默认值）
        # 实际应用中，这些值应该通过图片分析服务获取
        processed = ProcessedImage(
            url=url,
            width=1920,  # 默认值
            height=1080,  # 默认值
            format=format_ext,
            file_size=0,  # 未知
            dominant_colors=[],  # 需要图片分析服务
            thumbnail_url=None,
            metadata={
                "source_url": url,
                "processed": True
            }
        )
        
        return processed
    
    async def process_videos(self, video_urls: List[str]) -> List[ProcessedVideo]:
        """
        处理视频URL和基础信息
        
        Args:
            video_urls: 视频URL列表
        
        Returns:
            List[ProcessedVideo]: 处理后的视频数据列表
        
        注意：此实现为简化版本，仅处理URL和基础元数据
        实际的视频内容分析（时长、关键帧等）需要外部服务支持
        """
        logger.info(f"Processing {len(video_urls)} videos")
        
        if not video_urls:
            return []
        
        processed_videos = []
        
        for url in video_urls:
            try:
                processed = await self._process_single_video(url)
                processed_videos.append(processed)
            except Exception as e:
                logger.warning(f"Failed to process video {url}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_videos)}/{len(video_urls)} videos")
        return processed_videos
    
    async def _process_single_video(self, url: str) -> ProcessedVideo:
        """
        处理单个视频
        
        Args:
            url: 视频URL
        
        Returns:
            ProcessedVideo: 处理后的视频数据
        """
        # 从URL提取格式
        format_ext = self._extract_format_from_url(url)
        
        # 创建处理后的视频对象（使用默认值）
        # 实际应用中，这些值应该通过视频分析服务获取
        processed = ProcessedVideo(
            url=url,
            duration=30.0,  # 默认30秒
            width=1920,  # 默认值
            height=1080,  # 默认值
            fps=30.0,  # 默认30fps
            format=format_ext,
            file_size=0,  # 未知
            thumbnail_url=None,
            keyframes=[],  # 需要视频分析服务
            metadata={
                "source_url": url,
                "processed": True
            }
        )
        
        return processed
    
    async def process_audio(self, audio_urls: List[str]) -> List[ProcessedAudio]:
        """
        处理音频URL和基础信息
        
        Args:
            audio_urls: 音频URL列表
        
        Returns:
            List[ProcessedAudio]: 处理后的音频数据列表
        
        注意：此实现为简化版本，仅处理URL和基础元数据
        实际的音频内容分析（时长、采样率等）需要外部服务支持
        """
        logger.info(f"Processing {len(audio_urls)} audio files")
        
        if not audio_urls:
            return []
        
        processed_audio = []
        
        for url in audio_urls:
            try:
                processed = await self._process_single_audio(url)
                processed_audio.append(processed)
            except Exception as e:
                logger.warning(f"Failed to process audio {url}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(processed_audio)}/{len(audio_urls)} audio files")
        return processed_audio
    
    async def _process_single_audio(self, url: str) -> ProcessedAudio:
        """
        处理单个音频
        
        Args:
            url: 音频URL
        
        Returns:
            ProcessedAudio: 处理后的音频数据
        """
        # 从URL提取格式
        format_ext = self._extract_format_from_url(url)
        
        # 创建处理后的音频对象（使用默认值）
        # 实际应用中，这些值应该通过音频分析服务获取
        processed = ProcessedAudio(
            url=url,
            duration=180.0,  # 默认3分钟
            format=format_ext,
            file_size=0,  # 未知
            sample_rate=44100,  # 默认44.1kHz
            channels=2,  # 默认立体声
            metadata={
                "source_url": url,
                "processed": True
            }
        )
        
        return processed
    
    def _extract_format_from_url(self, url: str) -> str:
        """
        从URL中提取文件格式
        
        Args:
            url: 文件URL
        
        Returns:
            str: 文件格式（扩展名）
        """
        try:
            # 移除查询参数
            url_without_params = url.split('?')[0]
            
            # 提取文件名
            if '/' in url_without_params:
                filename = url_without_params.rsplit('/', 1)[-1]
            else:
                filename = url_without_params
            
            # 提取扩展名
            if '.' in filename:
                return '.' + filename.rsplit('.', 1)[-1].lower()
            
            return '.unknown'
            
        except Exception as e:
            logger.warning(f"Failed to extract format from URL {url}: {e}")
            return '.unknown'
    
    async def process_all(
        self,
        text: str,
        image_urls: List[str],
        video_urls: List[str],
        audio_urls: List[str]
    ) -> Dict[str, Any]:
        """
        处理所有输入数据
        
        Args:
            text: 文本描述
            image_urls: 图片URL列表
            video_urls: 视频URL列表
            audio_urls: 音频URL列表
        
        Returns:
            Dict[str, Any]: 包含所有处理结果的字典
        """
        logger.info("Processing all input data")
        
        # 并发处理所有数据
        results = await asyncio.gather(
            self.process_text(text),
            self.process_images(image_urls),
            self.process_videos(video_urls),
            self.process_audio(audio_urls),
            return_exceptions=True
        )
        
        # 提取结果
        processed_text = results[0] if not isinstance(results[0], Exception) else None
        processed_images = results[1] if not isinstance(results[1], Exception) else []
        processed_videos = results[2] if not isinstance(results[2], Exception) else []
        processed_audio = results[3] if not isinstance(results[3], Exception) else []
        
        return {
            "text": processed_text,
            "images": processed_images,
            "videos": processed_videos,
            "audio": processed_audio
        }
