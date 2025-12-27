"""
缓存管理器

基于生成参数的缓存查找和复用。
"""

import hashlib
import json
import logging
from typing import Dict, Any, Optional

from .artifact import Artifact


logger = logging.getLogger(__name__)


class CacheManager:
    """
    缓存管理器
    
    Features:
    - 基于生成参数的缓存键计算
    - 缓存查找
    - 缓存统计
    """
    
    def __init__(self, blackboard):
        """
        初始化缓存管理器
        
        Args:
            blackboard: Shared Blackboard 实例
        """
        self.blackboard = blackboard
    
    def compute_cache_key(self, generation_params: Dict[str, Any]) -> str:
        """
        计算缓存键
        
        Args:
            generation_params: 生成参数
            
        Returns:
            str: 缓存键（SHA256 哈希）
        """
        # 标准化参数（排序键）
        normalized = json.dumps(generation_params, sort_keys=True)
        
        # 计算 SHA256 哈希
        cache_key = hashlib.sha256(normalized.encode()).hexdigest()
        
        return cache_key
    
    def find_cached_artifact(self, generation_params: Dict[str, Any]) -> Optional[Artifact]:
        """
        查找缓存的 artifact
        
        Args:
            generation_params: 生成参数
            
        Returns:
            Optional[Artifact]: 缓存的 artifact，如果未找到则返回 None
        """
        cache_key = self.compute_cache_key(generation_params)
        
        try:
            # 从数据库查询
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT * FROM artifacts
                WHERE cache_key = %s
                AND status = 'AVAILABLE'
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (cache_key,)
            )
            
            row = cursor.fetchone()
            
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            if row:
                # 转换为 Artifact 对象
                artifact = Artifact.from_dict({
                    "artifact_id": row[0],
                    "project_id": row[1],
                    "type": row[2],
                    "status": row[3],
                    "storage_url": row[4],
                    "file_size": row[5],
                    "content_type": row[6],
                    "checksum": row[7],
                    "metadata": row[8],
                    "generation_params": row[9],
                    "cache_key": row[10]
                })
                
                logger.info(f"Cache hit for key {cache_key[:8]}...")
                return artifact
            
            logger.debug(f"Cache miss for key {cache_key[:8]}...")
            return None
            
        except Exception as e:
            logger.error(f"Failed to find cached artifact: {e}")
            return None
    
    def register_cache_hit(self, artifact_id: str) -> None:
        """
        记录缓存命中
        
        Args:
            artifact_id: Artifact ID
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            # 更新访问计数
            cursor.execute(
                """
                UPDATE artifacts
                SET access_count = access_count + 1,
                    last_accessed_at = NOW()
                WHERE artifact_id = %s
                """,
                (artifact_id,)
            )
            
            conn.commit()
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            logger.debug(f"Registered cache hit for {artifact_id}")
            
        except Exception as e:
            logger.error(f"Failed to register cache hit: {e}")
    
    def get_cache_stats(self, project_id: str) -> Dict[str, Any]:
        """
        获取缓存统计
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 缓存统计信息
        """
        try:
            conn = self.blackboard.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_artifacts,
                    SUM(access_count) as total_accesses,
                    AVG(access_count) as avg_reuse
                FROM artifacts
                WHERE project_id = %s
                AND status = 'AVAILABLE'
                """,
                (project_id,)
            )
            
            row = cursor.fetchone()
            
            cursor.close()
            self.blackboard.db.putconn(conn)
            
            return {
                "total_artifacts": row[0] or 0,
                "total_accesses": row[1] or 0,
                "avg_reuse": float(row[2]) if row[2] else 0.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {}
