"""
Storage Service - 对象存储服务

负责 S3 兼容存储、artifact 管理、缓存复用和元数据管理。
"""

from .artifact import Artifact, ArtifactType, ArtifactStatus
from .storage_service import StorageService
from .s3_client import S3Client
from .cache_manager import CacheManager
from .metadata_manager import MetadataManager

__all__ = [
    'Artifact',
    'ArtifactType',
    'ArtifactStatus',
    'StorageService',
    'S3Client',
    'CacheManager',
    'MetadataManager',
]
