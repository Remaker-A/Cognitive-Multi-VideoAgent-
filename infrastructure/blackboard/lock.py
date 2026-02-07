"""
分布式锁实现

使用 Redis 实现分布式锁，支持超时和原子操作。
"""

import time
import uuid
from typing import Optional

from .exceptions import LockAcquisitionError


class DistributedLock:
    """Redis 分布式锁"""
    
    def __init__(self, redis_client, lock_key: str, timeout: int = 30):
        """
        初始化分布式锁
        
        Args:
            redis_client: Redis 客户端
            lock_key: 锁的键名
            timeout: 锁的超时时间（秒）
        """
        self.redis = redis_client
        self.lock_key = f"lock:{lock_key}"
        self.timeout = timeout
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self, blocking: bool = True, timeout: Optional[int] = None) -> bool:
        """
        获取锁
        
        Args:
            blocking: 是否阻塞等待
            timeout: 等待超时时间（秒）
            
        Returns:
            bool: 是否成功获取锁
        """
        if blocking:
            end_time = time.time() + (timeout or self.timeout)
            while time.time() < end_time:
                if self._try_acquire():
                    return True
                time.sleep(0.1)
            return False
        else:
            return self._try_acquire()
    
    def _try_acquire(self) -> bool:
        """
        尝试获取锁
        
        Returns:
            bool: 是否成功获取锁
        """
        # 使用 SET NX EX 原子操作
        result = self.redis.set(
            self.lock_key,
            self.lock_value,
            nx=True,  # 仅当键不存在时设置
            ex=self.timeout  # 过期时间
        )
        return result is True
    
    def release(self):
        """释放锁"""
        # 使用 Lua 脚本确保原子性
        lua_script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        self.redis.eval(lua_script, 1, self.lock_key, self.lock_value)
    
    def __enter__(self):
        """上下文管理器入口"""
        if not self.acquire():
            raise LockAcquisitionError(f"Failed to acquire lock: {self.lock_key}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.release()
    
    def __repr__(self):
        return f"DistributedLock(key={self.lock_key}, timeout={self.timeout})"
