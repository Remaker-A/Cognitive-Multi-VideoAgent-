"""
Artifact 数据模型

定义 artifact 的数据结构、类型和状态。
"""

from enum import Enum
from typing import Any, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, field
import uuid


class ArtifactType(str, Enum):
    """Artifact 类型枚举"""
    # 图像
    IMAGE = "IMAGE"
    KEYFRAME = "KEYFRAME"
    REFERENCE_IMAGE = "REFERENCE_IMAGE"
    
    # 视频
    VIDEO = "VIDEO"
    PREVIEW_VIDEO = "PREVIEW_VIDEO"
    FINAL_VIDEO = "FINAL_VIDEO"
    
    # 音频
    AUDIO = "AUDIO"
    MUSIC = "MUSIC"
    VOICE = "VOICE"
    
    # 文本
    SCRIPT = "SCRIPT"
    PROMPT = "PROMPT"
    
    # 其他
    MODEL = "MODEL"
    EMBEDDING = "EMBEDDING"
    METADATA = "METADATA"


class ArtifactStatus(str, Enum):
    """Artifact 状态枚举"""
    UPLOADING = "UPLOADING"      # 上传中
    AVAILABLE = "AVAILABLE"      # 可用
    PROCESSING = "PROCESSING"    # 处理中
    EXPIRED = "EXPIRED"          # 已过期
    DELETED = "DELETED"          # 已删除


@dataclass
class Artifact:
    """
    Artifact 数据模型
    
    表示系统中的一个存储对象（图像、视频、音频等）。
    """
    # 基础信息
    artifact_id: str = field(default_factory=lambda: f"ART-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}")
    project_id: str = ""
    type: ArtifactType = ArtifactType.IMAGE
    status: ArtifactStatus = ArtifactStatus.UPLOADING
    
    # 存储信息
    storage_url: str = ""  # S3 URL (s3://bucket/key)
    file_size: int = 0
    content_type: str = "application/octet-stream"
    checksum: str = ""  # MD5 或 SHA256
    
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # 生成参数（用于缓存复用）
    generation_params: Dict[str, Any] = field(default_factory=dict)
    cache_key: Optional[str] = None
    
    # 关联信息
    shot_id: Optional[str] = None
    task_id: Optional[str] = None
    
    # 时间戳
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    
    # 使用统计
    access_count: int = 0
    last_accessed_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "artifact_id": self.artifact_id,
            "project_id": self.project_id,
            "type": self.type.value if isinstance(self.type, ArtifactType) else self.type,
            "status": self.status.value if isinstance(self.status, ArtifactStatus) else self.status,
            "storage_url": self.storage_url,
            "file_size": self.file_size,
            "content_type": self.content_type,
            "checksum": self.checksum,
            "metadata": self.metadata,
            "generation_params": self.generation_params,
            "cache_key": self.cache_key,
            "shot_id": self.shot_id,
            "task_id": self.task_id,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "access_count": self.access_count,
            "last_accessed_at": self.last_accessed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Artifact':
        """从字典创建"""
        artifact_type = ArtifactType(data["type"]) if isinstance(data["type"], str) else data["type"]
        artifact_status = ArtifactStatus(data["status"]) if isinstance(data["status"], str) else data["status"]
        
        return cls(
            artifact_id=data.get("artifact_id", ""),
            project_id=data.get("project_id", ""),
            type=artifact_type,
            status=artifact_status,
            storage_url=data.get("storage_url", ""),
            file_size=data.get("file_size", 0),
            content_type=data.get("content_type", "application/octet-stream"),
            checksum=data.get("checksum", ""),
            metadata=data.get("metadata", {}),
            generation_params=data.get("generation_params", {}),
            cache_key=data.get("cache_key"),
            shot_id=data.get("shot_id"),
            task_id=data.get("task_id"),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            expires_at=data.get("expires_at"),
            access_count=data.get("access_count", 0),
            last_accessed_at=data.get("last_accessed_at")
        )
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        if not self.expires_at:
            return False
        
        expires = datetime.fromisoformat(self.expires_at)
        return datetime.utcnow() > expires
    
    def __repr__(self) -> str:
        return f"Artifact(id={self.artifact_id}, type={self.type.value}, size={self.file_size})"
