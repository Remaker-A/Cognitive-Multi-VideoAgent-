"""
镜头语言定义

定义镜头类型、角度、运动等电影语言元素。
"""

from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass


class ShotType(str,Enum):
    """镜头类型"""
    EXTREME_CLOSE_UP = "extreme_close_up"
    CLOSE_UP = "close_up"
    MEDIUM_CLOSE_UP = "medium_close_up"
    MEDIUM_SHOT = "medium_shot"
    MEDIUM_FULL_SHOT = "medium_full_shot"
    FULL_SHOT = "full_shot"
    LONG_SHOT = "long_shot"
    EXTREME_LONG_SHOT = "extreme_long_shot"


class CameraMovement(str, Enum):
    """镜头运动"""
    STATIC = "static"
    PAN_LEFT = "pan_left"
    PAN_RIGHT = "pan_right"
    TILT_UP = "tilt_up"
    TILT_DOWN = "tilt_down"
    DOLLY_IN = "dolly_in"
    DOLLY_OUT = "dolly_out"
    TRACKING = "tracking"
    ZOOM_IN = "zoom_in"
    ZOOM_OUT = "zoom_out"


class CameraAngle(str, Enum):
    """镜头角度"""
    EYE_LEVEL = "eye_level"
    HIGH_ANGLE = "high_angle"
    LOW_ANGLE = "low_angle"
    BIRD_EYE = "bird_eye"
    WORM_EYE = "worm_eye"


@dataclass
class CameraSpec:
    """镜头规格"""
    shot_type: ShotType
    movement: CameraMovement
    angle: CameraAngle
    duration: float
    fps: int = 24
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "shot_type": self.shot_type.value,
            "movement": self.movement.value,
            "angle": self.angle.value,
            "duration": self.duration,
            "fps": self.fps
        }


class CameraLanguage:
    """镜头语言工具类"""
    
    # 镜头类型描述
    SHOT_TYPE_DESCRIPTIONS = {
        ShotType.EXTREME_CLOSE_UP: "face only, emotional intensity, detailed features",
        ShotType.CLOSE_UP: "head and shoulders, facial expressions clear",
        ShotType.MEDIUM_CLOSE_UP: "chest up, personal interaction",
        ShotType.MEDIUM_SHOT: "waist up, character fills 60% of frame",
        ShotType.MEDIUM_FULL_SHOT: "knee up, show body language",
        ShotType.FULL_SHOT: "entire body visible, show full movement",
        ShotType.LONG_SHOT: "characters small in environment, context clear",
        ShotType.EXTREME_LONG_SHOT: "establishing shot, vast environment, tiny figures"
    }
    
    # 运动描述
    MOVEMENT_DESCRIPTIONS = {
        CameraMovement.STATIC: "locked camera, no movement, stable framing",
        CameraMovement.PAN_LEFT: "camera pans left, smooth horizontal rotation",
        CameraMovement.PAN_RIGHT: "camera pans right, smooth horizontal rotation",
        CameraMovement.TILT_UP: "camera tilts up, vertical rotation upward",
        CameraMovement.TILT_DOWN: "camera tilts down, vertical rotation downward",
        CameraMovement.DOLLY_IN: "camera moves forward toward subject",
        CameraMovement.DOLLY_OUT: "camera moves backward away from subject",
        CameraMovement.TRACKING: "camera follows subject smoothly, tracking shot",
        CameraMovement.ZOOM_IN: "lens zooms in, magnifies subject",
        CameraMovement.ZOOM_OUT: "lens zooms out, reveals more context"
    }
    
    @classmethod
    def get_shot_description(cls, shot_type: ShotType) -> str:
        """获取镜头类型描述"""
        return cls.SHOT_TYPE_DESCRIPTIONS.get(shot_type, "")
    
    @classmethod
    def get_movement_description(cls, movement: CameraMovement) -> str:
        """获取运动描述"""
        return cls.MOVEMENT_DESCRIPTIONS.get(movement, "")
    
    @classmethod
    def select_shot_type_by_mood(cls, mood: str) -> ShotType:
        """根据情绪选择镜头类型"""
        mood_lower = mood.lower()
        
        if mood_lower in ["intimate", "emotional", "tense"]:
            return ShotType.CLOSE_UP
        elif mood_lower in ["peaceful", "calm", "establishing"]:
            return ShotType.LONG_SHOT
        elif mood_lower in ["action", "dynamic"]:
            return ShotType.MEDIUM_SHOT
        else:
            return ShotType.MEDIUM_SHOT  # 默认
    
    @classmethod
    def select_movement_by_mood(cls, mood: str) -> CameraMovement:
        """根据情绪选择运动类型"""
        mood_lower = mood.lower()
        
        if mood_lower in ["calm", "peaceful", "static"]:
            return CameraMovement.STATIC
        elif mood_lower in ["following", "action"]:
            return CameraMovement.TRACKING
        elif mood_lower in ["dramatic", "intense"]:
            return CameraMovement.DOLLY_IN
        else:
            return CameraMovement.STATIC  # 默认静止
