"""
Series Blackboard - 系列级黑板

负责Series级别的数据管理：
- Series基础信息
- Series Bible（剧集圣经）
- Asset Registry（资产注册表）
- Series Budget（系列预算）
- Cross-Episode管理
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .exceptions import (
    SeriesNotFoundError,
    DatabaseError,
    CacheError
)


class SeriesBlackboard:
    """Series级别黑板 - 管理整个剧集系列"""
    
    def __init__(self, db_pool, redis_client, s3_client=None):
        """
        初始化 Series Blackboard
        
        Args:
            db_pool: PostgreSQL 连接池
            redis_client: Redis 客户端
            s3_client: S3/MinIO 客户端（可选）
        """
        self.db = db_pool
        self.redis = redis_client
        self.s3 = s3_client
    
    # ========== Series CRUD ==========
    
    def create_series(
        self,
        series_id: str,
        series_spec: Dict[str, Any],
        series_budget: Dict[str, Any],
        show_bible: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建新Series
        
        Args:
            series_id: Series ID
            series_spec: Series规格
            series_budget: Series预算
            show_bible: Series Bible（可选）
            
        Returns:
            Dict: 创建的Series数据
        """
        series = {
            "series_id": series_id,
            "version": 1,
            "status": "created",
            "series_spec": series_spec,
            "show_bible": show_bible or {},
            "asset_registry": {
                "characters": {},
                "scenes": {},
                "shots": {},
                "audio": {},
                "lockedAssets": []
            },
            "continuity_ledger": [],
            "series_budget": series_budget,
            "change_log": [],
            "collaborators": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO series (
                    series_id, version, status, series_spec, show_bible,
                    asset_registry, continuity_ledger, series_budget,
                    change_log, collaborators
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    series['series_id'],
                    series['version'],
                    series['status'],
                    json.dumps(series['series_spec']),
                    json.dumps(series['show_bible']),
                    json.dumps(series['asset_registry']),
                    json.dumps(series['continuity_ledger']),
                    json.dumps(series['series_budget']),
                    json.dumps(series['change_log']),
                    json.dumps(series['collaborators'])
                )
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            # 写入缓存
            cache_key = f"series:{series_id}"
            self.redis.setex(cache_key, 3600, json.dumps(series))
            
            return series
        except Exception as e:
            raise DatabaseError(f"Failed to create series {series_id}: {str(e)}")
    
    def get_series(self, series_id: str) -> Dict[str, Any]:
        """
        获取Series完整数据
        
        Args:
            series_id: Series ID
            
        Returns:
            Dict: Series数据
            
        Raises:
            SeriesNotFoundError: Series不存在
        """
        cache_key = f"series:{series_id}"
        
        # 尝试从缓存读取
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Cache read failed: {e}")
        
        # 从数据库读取
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    series_id, version, status, created_at, updated_at,
                    series_spec, show_bible, asset_registry, continuity_ledger,
                    series_budget, change_log, collaborators
                FROM series
                WHERE series_id = %s
                """,
                (series_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if not result:
                raise SeriesNotFoundError(f"Series {series_id} not found")
            
            series = {
                "series_id": result[0],
                "version": result[1],
                "status": result[2],
                "created_at": result[3].isoformat() if result[3] else None,
                "updated_at": result[4].isoformat() if result[4] else None,
                "series_spec": result[5],
                "show_bible": result[6],
                "asset_registry": result[7],
                "continuity_ledger": result[8],
                "series_budget": result[9],
                "change_log": result[10],
                "collaborators": result[11]
            }
            
            # 写入缓存
            try:
                self.redis.setex(cache_key, 3600, json.dumps(series))
            except Exception as e:
                print(f"Cache write failed: {e}")
            
            return series
        except SeriesNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get series: {str(e)}")
    
    def update_series_status(self, series_id: str, new_status: str):
        """
        更新Series状态
        
        Args:
            series_id: Series ID
            new_status: 新状态
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE series
                SET status = %s, updated_at = NOW()
                WHERE series_id = %s
                """,
                (new_status, series_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(series_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update series status: {str(e)}")
    
    # ========== Series Bible 操作 ==========
    
    def get_series_bible(self, series_id: str) -> Dict[str, Any]:
        """获取Series Bible"""
        series = self.get_series(series_id)
        return series.get('show_bible', {})
    
    def update_series_bible(
        self,
        series_id: str,
        show_bible: Dict[str, Any]
    ):
        """
        更新Series Bible
        
        Args:
            series_id: Series ID
            show_bible: 新的Series Bible数据
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE series
                SET show_bible = %s, updated_at = NOW(), version = version + 1
                WHERE series_id = %s
                """,
                (json.dumps(show_bible), series_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(series_id)
            self._log_change(series_id, "UPDATE_SERIES_BIBLE", show_bible)
        except Exception as e:
            raise DatabaseError(f"Failed to update series bible: {str(e)}")
    
    # ========== Asset Registry 操作 ==========
    
    def get_asset_registry(self, series_id: str) -> Dict[str, Any]:
        """获取Asset Registry"""
        series = self.get_series(series_id)
        return series.get('asset_registry', {})
    
    def update_character_dna(
        self,
        series_id: str,
        character_id: str,
        character_dna: Dict[str, Any]
    ):
        """
        更新角色DNA
        
        Args:
            series_id: Series ID
            character_id: 角色ID
            character_dna: 角色DNA数据
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            path = f'{{characters,{character_id}}}'
            cursor.execute(
                """
                UPDATE series
                SET asset_registry = jsonb_set(
                    asset_registry,
                    %s,
                    %s::jsonb
                ),
                updated_at = NOW(),
                version = version + 1
                WHERE series_id = %s
                """,
                (path, json.dumps(character_dna), series_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(series_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update character DNA: {str(e)}")
    
    def update_scene_dna(
        self,
        series_id: str,
        scene_id: str,
        scene_dna: Dict[str, Any]
    ):
        """更新场景DNA"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            path = f'{{scenes,{scene_id}}}'
            cursor.execute(
                """
                UPDATE series
                SET asset_registry = jsonb_set(
                    asset_registry,
                    %s,
                    %s::jsonb
                ),
                updated_at = NOW()
                WHERE series_id = %s
                """,
                (path, json.dumps(scene_dna), series_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(series_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update scene DNA: {str(e)}")
    
    # ========== Budget 操作 ==========
    
    def get_series_budget(self, series_id: str) -> Dict[str, Any]:
        """获取Series预算"""
        series = self.get_series(series_id)
        return series.get('series_budget', {})
    
    def update_series_budget(
        self,
        series_id: str,
        series_budget: Dict[str, Any]
    ):
        """更新Series预算"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE series
                SET series_budget = %s, updated_at = NOW()
                WHERE series_id = %s
                """,
                (json.dumps(series_budget), series_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(series_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update series budget: {str(e)}")
    
    # ========== 辅助方法 ==========
    
    def _invalidate_cache(self, series_id: str):
        """失效缓存"""
        try:
            patterns = [
                f"series:{series_id}",
                f"series:{series_id}:*"
            ]
            
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache invalidation failed: {e}")
    
    def _log_change(self, series_id: str, change_type: str, data: Dict[str, Any]):
        """记录变更日志"""
        # TODO: 实现完整的变更日志记录
        pass
