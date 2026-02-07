"""
Shot Blackboard - 镜头级黑板

负责Shot级别的数据管理：
- Shot Spec（镜头规格）
- Prompt Pack（提示词包）
- Artifacts（产物）
- QA Results（质量检查）
- Cost Ledger（成本账本）
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional

from .exceptions import (
    ShotNotFoundError,
    EpisodeNotFoundError,
    DatabaseError
)


class ShotBlackboard:
    """Shot级别黑板 - 管理镜头数据"""
    
    def __init__(self, db_pool, redis_client, episode_blackboard):
        """
        初始化 Shot Blackboard
        
        Args:
            db_pool: PostgreSQL 连接池
            redis_client: Redis 客户端
            episode_blackboard: EpisodeBlackboard实例（用于跨层访问）
        """
        self.db = db_pool
        self.redis = redis_client
        self.episode_bb = episode_blackboard
    
    # ========== Shot CRUD ==========
    
    def create_shot(
        self,
        shot_id: str,
        shot_number: int,
        episode_id: str,
        series_id: str,
        shot_spec: Dict[str, Any],
        scene_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        创建新Shot
        
        Args:
            shot_id: Shot ID
            shot_number: Shot编号
            episode_id: 所属Episode ID
            series_id: 所属Series ID
            shot_spec: Shot规格
            scene_id: 场景ID（可选）
            
        Returns:
            Dict: 创建的Shot数据
        """
        shot = {
            "shot_id": shot_id,
            "shot_number": shot_number,
            "scene_id": scene_id,
            "episode_id": episode_id,
            "series_id": series_id,
            "version": 1,
            "status": "planned",
            "shot_spec": shot_spec,
            "referenced_assets": {},
            "prompt_pack": None,
            "generation_plan": None,
            "artifacts": {},
            "qa_results": {},
            "cost_ledger": {
                "keyframeGeneration": 0,
                "videoGeneration": 0,
                "audioGeneration": 0,
                "qaAndFix": 0,
                "retries": 0,
                "total": 0
            },
            "artifact_index": [],
            "change_history": []
        }
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO shots (
                    shot_id, shot_number, scene_id, episode_id, series_id,
                    version, status, shot_spec, referenced_assets, prompt_pack,
                    generation_plan, artifacts, qa_results, cost_ledger,
                    artifact_index, change_history
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    shot['shot_id'],
                    shot['shot_number'],
                    shot['scene_id'],
                    shot['episode_id'],
                    shot['series_id'],
                    shot['version'],
                    shot['status'],
                    json.dumps(shot['shot_spec']),
                    json.dumps(shot['referenced_assets']),
                    None,  # prompt_pack初始为NULL
                    None,  # generation_plan初始为NULL
                    json.dumps(shot['artifacts']),
                    json.dumps(shot['qa_results']),
                    json.dumps(shot['cost_ledger']),
                    json.dumps(shot['artifact_index']),
                    json.dumps(shot['change_history'])
                )
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            # 写入缓存
            cache_key = f"shot:{shot_id}"
            self.redis.setex(cache_key, 3600, json.dumps(shot))
            
            return shot
        except Exception as e:
            raise DatabaseError(f"Failed to create shot: {str(e)}")
    
    def get_shot(self, shot_id: str) -> Dict[str, Any]:
        """
        获取Shot完整数据
        
        Args:
            shot_id: Shot ID
            
        Returns:
            Dict: Shot数据
        """
        cache_key = f"shot:{shot_id}"
        
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
                    shot_id, shot_number, scene_id, episode_id, series_id,
                    version, status, created_at, updated_at, shot_spec,
                    referenced_assets, prompt_pack, generation_plan,
                    artifacts, qa_results, cost_ledger, artifact_index,
                    change_history
                FROM shots
                WHERE shot_id = %s
                """,
                (shot_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if not result:
                raise ShotNotFoundError(f"Shot {shot_id} not found")
            
            shot = {
                "shot_id": result[0],
                "shot_number": result[1],
                "scene_id": result[2],
                "episode_id": result[3],
                "series_id": result[4],
                "version": result[5],
                "status": result[6],
                "created_at": result[7].isoformat() if result[7] else None,
                "updated_at": result[8].isoformat() if result[8] else None,
                "shot_spec": result[9],
                "referenced_assets": result[10],
                "prompt_pack": result[11],
                "generation_plan": result[12],
                "artifacts": result[13],
                "qa_results": result[14],
                "cost_ledger": result[15],
                "artifact_index": result[16],
                "change_history": result[17]
            }
            
            # 写入缓存
            try:
                self.redis.setex(cache_key, 3600, json.dumps(shot))
            except Exception:
                pass
            
            return shot
        except ShotNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get shot: {str(e)}")
    
    def get_all_shots(self, episode_id: str) -> Dict[str, Any]:
        """获取Episode下的所有Shots"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT shot_id, shot_number, status, artifacts
                FROM shots
                WHERE episode_id = %s
                ORDER BY shot_number
                """,
                (episode_id,)
            )
            
            results = cursor.fetchall()
            cursor.close()
            self.db.putconn(conn)
            
            shots = {}
            for row in results:
                shots[row[0]] = {
                    "shot_id": row[0],
                    "shot_number": row[1],
                    "status": row[2],
                    "artifacts": row[3]
                }
            
            return shots
        except Exception as e:
            raise DatabaseError(f"Failed to get shots: {str(e)}")
    
    # ========== Shot更新操作 ==========
    
    def update_shot_status(self, shot_id: str, new_status: str):
        """更新Shot状态"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE shots
                SET status = %s, updated_at = NOW()
                WHERE shot_id = %s
                """,
                (new_status, shot_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(shot_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update shot status: {str(e)}")
    
    def update_prompt_pack(self, shot_id: str, prompt_pack: Dict[str, Any]):
        """更新Prompt Pack"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE shots
                SET prompt_pack = %s, updated_at = NOW()
                WHERE shot_id = %s
                """,
                (json.dumps(prompt_pack), shot_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(shot_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update prompt pack: {str(e)}")
    
    def update_artifacts(self, shot_id: str, artifacts: Dict[str, Any]):
        """更新Artifacts"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE shots
                SET artifacts = %s, updated_at = NOW()
                WHERE shot_id = %s
                """,
                (json.dumps(artifacts), shot_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(shot_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update artifacts: {str(e)}")
    
    def update_qa_results(self, shot_id: str, qa_results: Dict[str, Any]):
        """更新QA Results"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE shots
                SET qa_results = %s, updated_at = NOW()
                WHERE shot_id = %s
                """,
                (json.dumps(qa_results), shot_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(shot_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update QA results: {str(e)}")
    
    def update_cost_ledger(self, shot_id: str, cost_ledger: Dict[str, Any]):
        """更新Cost Ledger"""
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE shots
                SET cost_ledger = %s, updated_at = NOW()
                WHERE shot_id = %s
                """,
                (json.dumps(cost_ledger), shot_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(shot_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update cost ledger: {str(e)}")
    
    # ========== 辅助方法 ==========
    
    def _invalidate_cache(self, shot_id: str):
        """失效缓存"""
        try:
            cache_key = f"shot:{shot_id}"
            self.redis.delete(cache_key)
        except Exception as e:
            print(f"Cache invalidation failed: {e}")
