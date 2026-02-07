"""
Shot 规划器

负责规划每个 shot 的具体细节。
"""

import logging
from typing import Dict, Any, List

from .camera_language import CameraLanguage, ShotType, CameraMovement, CameraAngle, CameraSpec


logger = logging.getLogger(__name__)


class ShotPlanner:
    """Shot 规划器"""
    
    def __init__(self):
        """初始化规划器"""
        self.camera_language = CameraLanguage()
    
    def plan_shot(
        self,
        shot: Dict[str, Any],
        dna_bank: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        规划单个镜头
        
        Args:
            shot: Shot 数据
            dna_bank: DNA Bank（可选）
            
        Returns:
            Dict: Shot 规划结果
        """
        shot_id = shot.get("shot_id")
        logger.info(f"Planning shot: {shot_id}")
        
        # 1. 选择镜头类型
        shot_type = self._select_shot_type(shot)
        
        # 2. 选择镜头运动
        movement = self._select_movement(shot)
        
        # 3. 选择镜头角度
        angle = self._select_angle(shot)
        
        # 4. 创建镜头规格
        camera_spec = CameraSpec(
            shot_type=shot_type,
            movement=movement,
            angle=angle,
            duration=shot.get("duration", 5),
            fps=24
        )
        
        # 5. 计算 keyframe 数量
        keyframe_count = self._calculate_keyframe_count(shot.get("duration", 5))
        
        # 6. 提取 DNA 需求
        dna_requirements = self._extract_dna_needs(shot, dna_bank)
        
        # 7. 生成运动计划
        motion_plan = self._design_motion(shot, movement)
        
        # 8. 识别视觉元素
        visual_hooks = self._identify_visual_elements(shot)
        
        plan = {
            "shot_id": shot_id,
            "camera": camera_spec.to_dict(),
            "keyframe_count": keyframe_count,
            "dna_requirements": dna_requirements,
            "motion_plan": motion_plan,
            "visual_hooks": visual_hooks,
            "shot_description_enhanced": self._enhance_description(shot, camera_spec)
        }
        
        logger.debug(f"Shot plan created: {keyframe_count} keyframes, {shot_type.value}")
        
        return plan
    
    def _select_shot_type(self, shot: Dict[str, Any]) -> ShotType:
        """选择镜头类型"""
        # 从 shot.type 获取
        shot_type_str = shot.get("type", "").lower()
        
        if "portrait" in shot_type_str or "close" in shot_type_str:
            return ShotType.CLOSE_UP
        elif "action" in shot_type_str:
            return ShotType.MEDIUM_SHOT
        elif "environment" in shot_type_str or "establishing" in shot_type_str:
            return ShotType.LONG_SHOT
        elif "full" in shot_type_str:
            return ShotType.FULL_SHOT
        
        # 根据情绪选择
        mood_tags = shot.get("mood_tags", [])
        if mood_tags:
            return self.camera_language.select_shot_type_by_mood(mood_tags[0])
        
        return ShotType.MEDIUM_SHOT  # 默认
    
    def _select_movement(self, shot: Dict[str, Any]) -> CameraMovement:
        """选择镜头运动"""
        description = shot.get("description", "").lower()
        
        # 关键词匹配
        if "walking" in description or "moving" in description:
            return CameraMovement.TRACKING
        elif "approach" in description or "closer" in description:
            return CameraMovement.DOLLY_IN
        elif "reveal" in description or "pull back" in description:
            return CameraMovement.DOLLY_OUT
        
        # 根据情绪
        mood_tags = shot.get("mood_tags", [])
        if mood_tags:
            return self.camera_language.select_movement_by_mood(mood_tags[0])
        
        return CameraMovement.STATIC  # 默认静止
    
    def _select_angle(self, shot: Dict[str, Any]) -> CameraAngle:
        """选择镜头角度"""
        description = shot.get("description", "").lower()
        
        if "from above" in description or "overhead" in description:
            return CameraAngle.HIGH_ANGLE
        elif "from below" in description or "looking up" in description:
            return CameraAngle.LOW_ANGLE
        
        return CameraAngle.EYE_LEVEL  # 默认平视
    
    def _calculate_keyframe_count(self, duration: float) -> int:
        """
        计算 keyframe 数量
        
        Args:
            duration: 时长（秒）
            
        Returns:
            int: Keyframe 数量
        """
        # 简单规则：每 3-5 秒一个 keyframe
        if duration <= 3:
            return 1
        elif duration <= 7:
            return 2
        else:
            return max(2, int(duration / 3))
    
    def _extract_dna_needs(
        self,
        shot: Dict[str, Any],
        dna_bank: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """提取 DNA 需求"""
        characters = shot.get("characters", [])
        
        requirements = {
            "characters": characters,
            "requires_dna": len(characters) > 0,
            "dna_available": False
        }
        
        if dna_bank and characters:
            # 检查 DNA 是否可用
            available_chars = [c for c in characters if c in dna_bank]
            requirements["dna_available"] = len(available_chars) > 0
            requirements["available_characters"] = available_chars
        
        return requirements
    
    def _design_motion(
        self,
        shot: Dict[str, Any],
        movement: CameraMovement
    ) -> Dict[str, Any]:
        """设计运动计划"""
        return {
            "movement_type": movement.value,
            "speed": "smooth",
            "easing": "ease-in-out",
            "description": self.camera_language.get_movement_description(movement)
        }
    
    def _identify_visual_elements(self, shot: Dict[str, Any]) -> List[str]:
        """识别视觉元素"""
        elements = []
        
        description = shot.get("description", "")
        
        # 简单的关键词提取
        keywords = ["character", "face", "environment", "object", "light", "color"]
        
        for keyword in keywords:
            if keyword in description.lower():
                elements.append(keyword)
        
        return elements
    
    def _enhance_description(
        self,
        shot: Dict[str, Any],
        camera_spec: CameraSpec
    ) -> str:
        """增强 shot 描述，添加镜头信息"""
        original_desc = shot.get("description", "")
        
        shot_type_desc = self.camera_language.get_shot_description(camera_spec.shot_type)
        movement_desc = self.camera_language.get_movement_description(camera_spec.movement)
        
        enhanced = f"{original_desc}, {shot_type_desc}"
        
        if camera_spec.movement != CameraMovement.STATIC:
            enhanced += f", {movement_desc}"
        
        return enhanced
