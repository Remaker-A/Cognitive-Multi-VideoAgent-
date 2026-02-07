"""
对象检测器

使用 YOLO 或其他模型检测视频帧中的对象。
"""

import logging
from typing import List, Optional
import numpy as np

from ..data_structures import Detection

logger = logging.getLogger(__name__)


class ObjectDetector:
    """
    对象检测器
    
    使用 YOLO v8 或其他模型检测视频帧中的对象。
    """
    
    def __init__(self, model_name: str = "yolov8n", confidence_threshold: float = 0.5):
        """
        初始化对象检测器
        
        Args:
            model_name: 模型名称
            confidence_threshold: 置信度阈值
        """
        self.model_name = model_name
        self.confidence_threshold = confidence_threshold
        self.model = None
        
        # 延迟加载模型
        self._load_model()
        
        logger.info(f"ObjectDetector initialized with {model_name}")
    
    def _load_model(self):
        """加载检测模型"""
        try:
            # 尝试加载 YOLO
            from ultralytics import YOLO
            self.model = YOLO(self.model_name)
            logger.info("YOLO model loaded successfully")
        except ImportError:
            logger.warning("ultralytics not installed, using mock detector")
            self.model = None
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            self.model = None
    
    def detect(self, frame: np.ndarray, frame_id: int = 0) -> List[Detection]:
        """
        检测单帧中的对象
        
        Args:
            frame: 视频帧
            frame_id: 帧ID
            
        Returns:
            List[Detection]: 检测结果列表
        """
        if self.model is None:
            # 使用 mock 检测器
            return self._mock_detect(frame, frame_id)
        
        try:
            # 使用 YOLO 检测
            results = self.model(frame, verbose=False)[0]
            
            detections = []
            for box in results.boxes:
                # 提取检测信息
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                
                if confidence < self.confidence_threshold:
                    continue
                
                # 获取类别名称
                class_name = results.names[class_id]
                
                detection = Detection(
                    bbox=(int(x1), int(y1), int(x2), int(y2)),
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    frame_id=frame_id
                )
                detections.append(detection)
            
            return detections
            
        except Exception as e:
            logger.error(f"Detection failed: {e}")
            return []
    
    def detect_batch(
        self,
        frames: List[np.ndarray],
        start_frame_id: int = 0
    ) -> List[List[Detection]]:
        """
        批量检测多帧
        
        Args:
            frames: 视频帧列表
            start_frame_id: 起始帧ID
            
        Returns:
            List[List[Detection]]: 每帧的检测结果
        """
        all_detections = []
        
        for i, frame in enumerate(frames):
            frame_id = start_frame_id + i
            detections = self.detect(frame, frame_id)
            all_detections.append(detections)
        
        logger.info(f"Batch detection completed for {len(frames)} frames")
        return all_detections
    
    def _mock_detect(self, frame: np.ndarray, frame_id: int) -> List[Detection]:
        """Mock 检测器（用于测试）"""
        h, w = frame.shape[:2]
        
        # 生成一些假的检测结果
        detections = [
            Detection(
                bbox=(w//4, h//4, w//2, h//2),
                class_id=0,
                class_name="person",
                confidence=0.9,
                frame_id=frame_id
            )
        ]
        
        return detections
