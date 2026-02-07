"""
Blackboard 异常定义
"""


class BlackboardError(Exception):
    """Blackboard 基础异常"""
    pass


class ProjectNotFoundError(BlackboardError):
    """项目未找到异常"""
    pass


class ShotNotFoundError(BlackboardError):
    """Shot 未找到异常"""
    pass


class VersionConflictError(BlackboardError):
    """版本冲突异常"""
    pass


class LockAcquisitionError(BlackboardError):
    """锁获取失败异常"""
    pass


class CacheError(BlackboardError):
    """缓存错误异常"""
    pass


class DatabaseError(BlackboardError):
    """数据库错误异常"""
    pass
