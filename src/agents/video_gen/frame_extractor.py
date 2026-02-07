"""
帧提取器和 Embedding 提取

从视频中提取帧并计算 embeddings。
"""

import logging
import cv2
import numpy as np
from typing import List, Optional
from PIL import Image


logger = logging.getLogger(__name__)


class FrameExtractor:
    """
    帧提取器
    
    从视频中提取关键帧并计算 embeddings。
    """
    
    def __init__(self):
        """初始化提取器"""
        self.model = None
        self._load_model()
        
        logger.info("FrameExtractor initialized")
    
    def _load_model(self):
        """加载 embedding 模型"""
        try:
            from transformers import CLIPModel, CLIPProcessor
            
            self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            
            logger.info("CLIP model loaded for frame embeddings")
            
        except ImportError as e:
            logger.error(f"Failed to load CLIP model: {e}")
            self.model = None
    
    def extract_frames(
        self,
        video_path: str,
        num_frames: int = 10
    ) -> List[np.ndarray]:
        """
        提取视频帧
        
        Args:
            video_path: 视频路径
            num_frames: 提取帧数
            
        Returns:
            List[np.ndarray]: 帧列表
        """
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Failed to open video: {video_path}")
                return []
            
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                logger.warning("Video has no frames")
                return []
            
            # 计算采样间隔
            interval = max(1, total_frames // num_frames)
            
            frames = []
            frame_indices = range(0, total_frames, interval)[:num_frames]
            
            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                
                if ret:
                    # 转换为 RGB
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frames.append(frame_rgb)
            
            cap.release()
            
            logger.info(f"Extracted {len(frames)} frames from video")
            
            return frames
            
        except Exception as e:
            logger.error(f"Frame extraction failed: {e}", exc_info=True)
            return []
    
    def extract_embeddings(
        self,
        frames: List[np.ndarray]
    ) -> Optional[List[np.ndarray]]:
        """
        提取帧 embeddings
        
        Args:
            frames: 帧列表
            
        Returns:
            Optional[List[np.ndarray]]: Embedding 列表
        """
        if self.model is None:
            logger.warning("Model not loaded, skipping embedding extraction")
            return None
        
        if not frames:
            return None
        
        try:
            embeddings = []
            
            for frame in frames:
                # 转换为 PIL Image
                image = Image.fromarray(frame)
                
                # 预处理
                inputs = self.processor(images=image, return_tensors="pt")
                
                # 提取特征
                image_features = self.model.get_image_features(**inputs)
                
                # 转换为 numpy
                embedding = image_features.detach().numpy()[0]
                
                # 归一化
                embedding = embedding / np.linalg.norm(embedding)
                
                embeddings.append(embedding)
            
            logger.info(f"Extracted {len(embeddings)} frame embeddings")
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}", exc_info=True)
            return None
