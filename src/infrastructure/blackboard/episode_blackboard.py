"""
Episode Blackboard - 单集级黑板

负责Episode级别的数据管理：
- Episode基础信息
- Outline（大纲）
- Script（剧本）
- Storyboard（分镜）
- Episode Budget（单集预算）
- Shot管理
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .exceptions import (
    EpisodeNotFoundError,
    SeriesNotFoundError,
    DatabaseError
)


class EpisodeBlackboard:
    """Episode级别黑板 - 管理单集数据"""
    
    def __init__(self, db_pool, redis_client, series_blackboard):
        """
        初始化 Episode Blackboard
        
        Args:
            db_pool: PostgreSQL 连接池
            redis_client: Redis 客户端
            series_blackboard: SeriesBlackboard实例（用于跨层访问）
        """
        self.db = db_pool
        self.redis = redis_client
        self.series_bb = series_blackboard
    
    # ========== Episode CRUD ==========
    
    def create_episode(
        self,
        episode_id: str,
        episode_number: int,
        series_id: str,
        episode_budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建新Episode
        
        Args:
            episode_id: Episode ID
            episode_number: Episode编号
            series_id: 所属Series ID
            episode_budget: Episode预算
            
        Returns:
            Dict: 创建的Episode数据
        """
        # 验证Series存在
        try:
            self.series_bb.get_series(series_id)
        except Exception:
            raise SeriesNotFoundError(f"Series {series_id} not found")
        
        episode = {
            "episode_id": episode_id,
            "episode_number": episode_number,
            "series_id": series_id,
            "version": 1,
            "status": "not_started",
            "outline": {},
            "script": {},
            "storyboard": {},
            "episode_budget": episode_budget,
            "qa_report": {},
            "assembled_video": {},
            "approval_state": {
                "SCENE_WRITTEN": False,
                "PREVIEW_VIDEO_READY": False,
                "FINAL_VIDEO_READY": False
            },
            "change_log": [],
            "artifact_index": []
        }
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO episodes (
                    episode_id, episode_number, series_id, version, status,
                    outline, script, storyboard, episode_budget, qa_report,
                    assembled_video, approval_state, change_log, artifact_index
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    episode['episode_id'],
                    episode['episode_number'],
                    episode['series_id'],
                    episode['version'],
                    episode['status'],
                    json.dumps(episode['outline']),
                    json.dumps(episode['script']),
                    json.dumps(episode['storyboard']),
                    json.dumps(episode['episode_budget']),
                    json.dumps(episode['qa_report']),
                    json.dumps(episode['assembled_video']),
                    json.dumps(episode['approval_state']),
                    json.dumps(episode['change_log']),
                    json.dumps(episode['artifact_index'])
                )
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            # 写入缓存
            cache_key = f"episode:{episode_id}"
            self.redis.setex(cache_key, 3600, json.dumps(episode))
            
            return episode
        except Exception as e:
            raise DatabaseError(f"Failed to create episode: {str(e)}")
    
    def get_episode(self, episode_id: str) -> Dict[str, Any]:
        """
        获取Episode完整数据
        
        Args:
            episode_id: Episode ID
            
        Returns:
            Dict: Episode数据
        """
        cache_key = f"episode:{episode_id}"
        
        # 尝试从缓存读取
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        # 从数据库读取
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    episode_id, episode_number, series_id, version, status,
                    created_at, updated_at, outline, script, storyboard,
                    episode_budget, qa_report, assembled_video, approval_state,
                    change_log, artifact_index
                FROM episodes
                WHERE episode_id = %s
                """,
                (episode_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if not result:
                raise EpisodeNotFoundError(f"Episode {episode_id} not found")
            
            episode = {
                "episode_id": result[0],
                "episode_number": result[1],
                "series_id": result[2],
                "version": result[3],
                "status": result[4],
                "created_at": result[5].isoformat() if result[5] else None,
                "updated_at": result[6].isoformat() if result[6] else None,
                "outline": result[7],
                "script": result[8],
                "storyboard": result[9],
                "episode_budget": result[10],
                "qa_report": result[11],
                "assembled_video": result[12],
                "approval_state": result[13],
                "change_log": result[14],
                "artifact_index": result[15]
            }
            
            # 写入缓存
            try:
                self.redis.setex(cache_key, 3600, json.dumps(episode))
            except Exception:
                pass
            
            return episode
        except EpisodeNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get episode: {str(e)}")
    
    def get_all_episodes(self, series_id: str) -> List[Dict[str, Any]]:
        """获取Series下的所有Episodes"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT episode_id, episode_number, status, created_at
                FROM episodes
                WHERE series_id = %s
                ORDER BY episode_number
                """,
                (series_id,)
            )
            
            results = cursor.fetchall()
            cursor.close()
            self.db.putconn(conn)
            
            episodes = []
            for row in results:
                episodes.append({
                    "episode_id": row[0],
                    "episode_number": row[1],
                    "status": row[2],
                    "created_at": row[3].isoformat() if row[3] else None
                })
            
            return episodes
        except Exception as e:
            raise DatabaseError(f"Failed to get episodes: {str(e)}")
    
    # ========== Script操作 ==========
    
    def update_outline(self, episode_id: str, outline: Dict[str, Any]):
        """更新Outline"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET outline = %s, updated_at = NOW(), version = version + 1
                WHERE episode_id = %s
                """,
                (json.dumps(outline), episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update outline: {str(e)}")
    
    def update_script(self, episode_id: str, script: Dict[str, Any]):
        """更新Script"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET script = %s, updated_at = NOW(), version = version + 1
                WHERE episode_id = %s
                """,
                (json.dumps(script), episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update script: {str(e)}")
    
    def update_storyboard(self, episode_id: str, storyboard: Dict[str, Any]):
        """更新Storyboard"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET storyboard = %s, updated_at = NOW()
                WHERE episode_id = %s
                """,
                (json.dumps(storyboard), episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update storyboard: {str(e)}")
    
    # ========== 状态和预算 ==========
    
    def update_episode_status(self, episode_id: str, new_status: str):
        """更新Episode状态"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET status = %s, updated_at = NOW()
                WHERE episode_id = %s
                """,
                (new_status, episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update episode status: {str(e)}")
    
    def update_episode_budget(self, episode_id: str, episode_budget: Dict[str, Any]):
        """更新Episode预算"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET episode_budget = %s, updated_at = NOW()
                WHERE episode_id = %s
                """,
                (json.dumps(episode_budget), episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update episode budget: {str(e)}")
    
    # ========== QA Report ==========
    
    def update_qa_report(self, episode_id: str, qa_report: Dict[str, Any]):
        """更新QA报告"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE episodes
                SET qa_report = %s, updated_at = NOW()
                WHERE episode_id = %s
                """,
                (json.dumps(qa_report), episode_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(episode_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update QA report: {str(e)}")
    
    # ========== 辅助方法 ==========
    
    def _invalidate_cache(self, episode_id: str):
        """失效缓存"""
        try:
            cache_key = f"episode:{episode_id}"
            self.redis.delete(cache_key)
        except Exception as e:
            print(f"Cache invalidation failed: {e}")
