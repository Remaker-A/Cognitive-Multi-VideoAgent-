"""
Shared Blackboard - 共享黑板基础设施

作为单一事实来源（Single Source of Truth），负责存储项目全局状态、
shot 数据、DNA Bank、任务队列等。

技术栈:
- PostgreSQL 14+ (JSONB)
- Redis 7+ (缓存层)
- S3/MinIO (对象存储)
"""

from .blackboard import SharedBlackboard
from .lock import DistributedLock
from .exceptions import (
    ProjectNotFoundError,
    ShotNotFoundError,
    VersionConflictError,
    LockAcquisitionError
)

__all__ = [
    'SharedBlackboard',
    'DistributedLock',
    'ProjectNotFoundError',
    'ShotNotFoundError',
    'VersionConflictError',
    'LockAcquisitionError',
]
