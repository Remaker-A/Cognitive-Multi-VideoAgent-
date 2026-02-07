"""
Keyframe 请求生成器

负责生成 keyframe 和 preview video 的请求。
"""

import logging
from typing import Dict, Any, List


logger = logging.getLogger(__name__)


class KeyframeRequester:
    """Keyframe 请求生成器"""
    
    def __init__(self):
        """初始化请求器"""
        pass
    
    def create_keyframe_requests(
        self,
        shot: Dict[str, Any],
        shot_plan: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        创建 keyframe 请求列表
        
        Args:
            shot: Shot 数据
            shot_plan: Shot 规划结果
            
        Returns:
            List[Dict]: Keyframe 请求列表
        """
        requests = []
        
        keyframe_count = shot_plan.get("keyframe_count", 1)
        shot_id = shot.get("shot_id")
        
        for i in range(keyframe_count):
            request = self._create_single_keyframe_request(
                shot,
                shot_plan,
                keyframe_index=i,
                total_keyframes=keyframe_count
            )
            requests.append(request)
        
        logger.info(f"Created {len(requests)} keyframe requests for shot {shot_id}")
        
        return requests
    
    def _create_single_keyframe_request(
        self,
        shot: Dict[str, Any],
        shot_plan: Dict[str, Any],
        keyframe_index: int,
        total_keyframes: int
    ) -> Dict[str, Any]:
        """创建单个 keyframe 请求"""
        shot_id = shot.get("shot_id")
        
        # 计算时间点（在 shot 中的位置）
        duration = shot.get("duration", 5)
        
        if total_keyframes == 1:
            time_position = duration / 2  # 中间点
        else:
            time_position = (duration / (total_keyframes - 1)) * keyframe_index
        
        request = {
            "shot_id": shot_id,
            "keyframe_index": keyframe_index,
            "keyframe_id": f"{shot_id}_K{keyframe_index:02d}",
            "time_position": time_position,
            "total_keyframes": total_keyframes,
            
            # Shot 信息
            "description": shot.get("description", ""),
            "enhanced_description": shot_plan.get("shot_description_enhanced", ""),
            "characters": shot.get("characters", []),
            "environment": shot.get("environment", ""),
            "mood_tags": shot.get("mood_tags", []),
            
            # 镜头信息
            "camera": shot_plan.get("camera", {}),
            
            # DNA 需求
            "dna_requirements": shot_plan.get("dna_requirements", {}),
            
            # 生成参数
            "quality_tier": "STANDARD",  # TODO: 从 global_spec 获取
            "aspect_ratio": "9:16"  # TODO: 从 global_spec 获取
        }
        
        return request
    
    def create_preview_video_request(
        self,
        shot: Dict[str, Any],
        shot_plan: Dict[str, Any],
        keyframes: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建 preview video 请求
        
        Args:
            shot: Shot 数据
            shot_plan: Shot 规划结果
            keyframes: 已生成的 keyframes（可选）
            
        Returns:
            Dict: Preview video 请求
        """
        shot_id = shot.get("shot_id")
        
        request = {
            "shot_id": shot_id,
            "preview_id": f"{shot_id}_PREVIEW",
            
            # Shot 信息
            "description": shot.get("description", ""),
            "duration": shot.get("duration", 5),
            "characters": shot.get("characters", []),
            
            # 镜头信息
            "camera": shot_plan.get("camera", {}),
            "motion_plan": shot_plan.get("motion_plan", {}),
            
            # 预览参数
            "resolution": 256,  # 低分辨率预览
            "fps": 12,  # 低帧率
            "quality": "preview",
            
            # Keyframe 信息（如果有）
            "keyframes": keyframes if keyframes else [],
            "has_keyframes": bool(keyframes)
        }
        
        logger.info(f"Created preview video request for shot {shot_id}")
        
        return request
