"""
Shared Blackboard 核心实现

提供项目数据的 CRUD 操作，包括：
- 项目级别操作
- GlobalSpec 操作
- Budget 操作
- DNA Bank 操作
- Shot 操作
- Artifact 操作
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from .lock import DistributedLock
from .exceptions import (
    ProjectNotFoundError,
    ShotNotFoundError,
    VersionConflictError,
    DatabaseError,
    CacheError
)


class SharedBlackboard:
    """共享黑板 - 单一事实来源"""
    
    def __init__(self, db_pool, redis_client, s3_client=None):
        """
        初始化 Shared Blackboard
        
        Args:
            db_pool: PostgreSQL 连接池
            redis_client: Redis 客户端
            s3_client: S3/MinIO 客户端（可选）
        """
        self.db = db_pool
        self.redis = redis_client
        self.s3 = s3_client
    
    # ========== 项目级别操作 ==========
    
    def create_project(
        self,
        project_id: str,
        global_spec: Dict[str, Any],
        budget: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        创建新项目
        
        Args:
            project_id: 项目 ID
            global_spec: 全局规格
            budget: 预算信息
            
        Returns:
            Dict: 创建的项目数据
        """
        project = {
            "project_id": project_id,
            "version": 1,
            "status": "CREATED",
            "global_spec": global_spec,
            "budget": budget,
            "dna_bank": {},
            "shots": {},
            "tasks": {},
            "locks": {},
            "artifact_index": {},
            "error_log": [],
            "change_log": [],
            "approval_requests": {},
            "approval_history": []
        }
        
        try:
            # 写入数据库
            self._insert_project_to_db(project)
            
            # 写入缓存
            cache_key = f"project:{project_id}"
            self.redis.setex(cache_key, 3600, json.dumps(project))
            
            return project
        except Exception as e:
            raise DatabaseError(f"Failed to create project {project_id}: {str(e)}")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """
        获取项目完整数据
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 项目数据
            
        Raises:
            ProjectNotFoundError: 项目不存在
        """
        cache_key = f"project:{project_id}"
        
        try:
            # 尝试从缓存读取
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            # 缓存失败不影响主流程
            print(f"Cache read failed: {e}")
        
        # 从数据库读取
        project = self._get_project_from_db(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        
        # 写入缓存
        try:
            self.redis.setex(cache_key, 3600, json.dumps(project))
        except Exception as e:
            print(f"Cache write failed: {e}")
        
        return project
    
    def update_project_status(self, project_id: str, new_status: str):
        """
        更新项目状态
        
        Args:
            project_id: 项目 ID
            new_status: 新状态
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE projects
                SET status = %s, updated_at = NOW()
                WHERE project_id = %s
                """,
                (new_status, project_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            # 失效缓存
            self._invalidate_cache(project_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update project status: {str(e)}")
    
    # ========== GlobalSpec 操作 ==========
    
    def get_global_spec(self, project_id: str) -> Dict[str, Any]:
        """
        获取全局规格
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 全局规格数据
        """
        cache_key = f"project:{project_id}:global_spec"
        
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT global_spec FROM projects WHERE project_id = %s",
                (project_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if result:
                global_spec = result[0]
                self.redis.setex(cache_key, 3600, json.dumps(global_spec))
                return global_spec
            
            raise ProjectNotFoundError(f"Project {project_id} not found")
        except Exception as e:
            raise DatabaseError(f"Failed to get global_spec: {str(e)}")
    
    def update_global_spec(self, project_id: str, global_spec: Dict[str, Any]):
        """
        更新全局规格（需要锁）
        
        Args:
            project_id: 项目 ID
            global_spec: 新的全局规格
        """
        with DistributedLock(self.redis, f"project:{project_id}:global_style"):
            try:
                conn = self.db.getconn()
                cursor = conn.cursor()
                
                cursor.execute(
                    """
                    UPDATE projects
                    SET global_spec = %s, updated_at = NOW(), version = version + 1
                    WHERE project_id = %s
                    """,
                    (json.dumps(global_spec), project_id)
                )
                
                conn.commit()
                cursor.close()
                self.db.putconn(conn)
                
                self._invalidate_cache(project_id)
                self._log_change(project_id, "UPDATE_GLOBAL_SPEC", global_spec)
            except Exception as e:
                raise DatabaseError(f"Failed to update global_spec: {str(e)}")
    
    # ========== Budget 操作 ==========
    
    def get_budget(self, project_id: str) -> Dict[str, Any]:
        """
        获取预算信息
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 预算数据
        """
        cache_key = f"project:{project_id}:budget"
        
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT budget FROM projects WHERE project_id = %s",
                (project_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if result:
                budget = result[0]
                self.redis.setex(cache_key, 3600, json.dumps(budget))
                return budget
            
            raise ProjectNotFoundError(f"Project {project_id} not found")
        except Exception as e:
            raise DatabaseError(f"Failed to get budget: {str(e)}")
    
    def update_budget(self, project_id: str, budget: Dict[str, Any]):
        """
        更新预算
        
        Args:
            project_id: 项目 ID
            budget: 新的预算数据
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE projects
                SET budget = %s, updated_at = NOW()
                WHERE project_id = %s
                """,
                (json.dumps(budget), project_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(project_id)
        except Exception as e:
            raise DatabaseError(f"Failed to update budget: {str(e)}")
    
    def add_cost(self, project_id: str, cost: float, description: str):
        """
        增加成本
        
        Args:
            project_id: 项目 ID
            cost: 增加的成本
            description: 成本描述
        """
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                UPDATE projects
                SET budget = jsonb_set(
                    budget,
                    '{used}',
                    ((budget->>'used')::numeric + %s)::text::jsonb
                ),
                updated_at = NOW()
                WHERE project_id = %s
                """,
                (cost, project_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(project_id)
            self._log_change(project_id, "ADD_COST", {"cost": cost, "description": description})
        except Exception as e:
            raise DatabaseError(f"Failed to add cost: {str(e)}")
    
    # ========== DNA Bank 操作 ==========
    
    def get_dna_bank(self, project_id: str) -> Dict[str, Any]:
        """
        获取 DNA Bank
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: DNA Bank 数据
        """
        cache_key = f"project:{project_id}:dna_bank"
        
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT dna_bank FROM projects WHERE project_id = %s",
                (project_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if result:
                dna_bank = result[0]
                self.redis.setex(cache_key, 3600, json.dumps(dna_bank))
                return dna_bank
            
            return {}
        except Exception as e:
            raise DatabaseError(f"Failed to get dna_bank: {str(e)}")
    
    def update_dna_bank(
        self,
        project_id: str,
        character_id: str,
        dna_entry: Dict[str, Any]
    ):
        """
        更新 DNA Bank（需要锁）
        
        Args:
            project_id: 项目 ID
            character_id: 角色 ID
            dna_entry: DNA 条目数据
        """
        with DistributedLock(self.redis, f"project:{project_id}:dna_bank"):
            try:
                conn = self.db.getconn()
                cursor = conn.cursor()
                
                path = f'{{{character_id}}}'
                cursor.execute(
                    """
                    UPDATE projects
                    SET dna_bank = jsonb_set(
                        dna_bank,
                        %s,
                        %s::jsonb
                    ),
                    updated_at = NOW(),
                    version = version + 1
                    WHERE project_id = %s
                    """,
                    (path, json.dumps(dna_entry), project_id)
                )
                
                conn.commit()
                cursor.close()
                self.db.putconn(conn)
                
                self._invalidate_cache(project_id)
                self._log_change(project_id, "UPDATE_DNA_BANK", {
                    "character_id": character_id,
                    "dna_entry": dna_entry
                })
            except Exception as e:
                raise DatabaseError(f"Failed to update dna_bank: {str(e)}")
    
    # ========== Shot 操作 ==========
    
    def get_shot(self, project_id: str, shot_id: str) -> Dict[str, Any]:
        """
        获取单个 shot
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            
        Returns:
            Dict: Shot 数据
            
        Raises:
            ShotNotFoundError: Shot 不存在
        """
        cache_key = f"project:{project_id}:shot:{shot_id}"
        
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT shots->%s as shot FROM projects WHERE project_id = %s",
                (shot_id, project_id)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if result and result[0]:
                shot = result[0]
                self.redis.setex(cache_key, 3600, json.dumps(shot))
                return shot
            
            raise ShotNotFoundError(f"Shot {shot_id} not found in project {project_id}")
        except ShotNotFoundError:
            raise
        except Exception as e:
            raise DatabaseError(f"Failed to get shot: {str(e)}")
    
    def update_shot(
        self,
        project_id: str,
        shot_id: str,
        shot_data: Dict[str, Any]
    ):
        """
        更新 shot（shot 级别锁）
        
        Args:
            project_id: 项目 ID
            shot_id: Shot ID
            shot_data: Shot 数据
        """
        with DistributedLock(self.redis, f"project:{project_id}:shot:{shot_id}"):
            try:
                conn = self.db.getconn()
                cursor = conn.cursor()
                
                path = f'{{{shot_id}}}'
                cursor.execute(
                    """
                    UPDATE projects
                    SET shots = jsonb_set(
                        shots,
                        %s,
                        %s::jsonb
                    ),
                    updated_at = NOW()
                    WHERE project_id = %s
                    """,
                    (path, json.dumps(shot_data), project_id)
                )
                
                conn.commit()
                cursor.close()
                self.db.putconn(conn)
                
                # 失效缓存
                self.redis.delete(f"project:{project_id}:shot:{shot_id}")
                self._invalidate_cache(project_id)
                
                self._log_change(project_id, "UPDATE_SHOT", {
                    "shot_id": shot_id,
                    "shot_data": shot_data
                })
            except Exception as e:
                raise DatabaseError(f"Failed to update shot: {str(e)}")
    
    def get_all_shots(self, project_id: str) -> Dict[str, Any]:
        """
        获取所有 shots
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 所有 shots 数据
        """
        cache_key = f"project:{project_id}:shots"
        
        try:
            cached = self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT shots FROM projects WHERE project_id = %s",
                (project_id,)
            )
            
            result = cursor.fetchone()
            cursor.close()
            self.db.putconn(conn)
            
            if result:
                shots = result[0]
                self.redis.setex(cache_key, 3600, json.dumps(shots))
                return shots
            
            return {}
        except Exception as e:
            raise DatabaseError(f"Failed to get all shots: {str(e)}")
    
    # ========== Artifact 操作 ==========
    
    def register_artifact(
        self,
        project_id: str,
        artifact_url: str,
        metadata: Dict[str, Any]
    ):
        """
        注册 artifact
        
        Args:
            project_id: 项目 ID
            artifact_url: Artifact URL
            metadata: Artifact 元数据
        """
        artifact_entry = {
            "seed": metadata.get('seed'),
            "model": metadata.get('model'),
            "model_version": metadata.get('model_version'),
            "prompt": metadata.get('prompt'),
            "cost": metadata.get('cost'),
            "created_at": datetime.now().isoformat(),
            "uses": 0
        }
        
        try:
            conn = self.db.getconn()
            cursor = conn.cursor()
            
            # 更新 artifact_index
            path = f'{{{artifact_url}}}'
            cursor.execute(
                """
                UPDATE projects
                SET artifact_index = jsonb_set(
                    artifact_index,
                    %s,
                    %s::jsonb
                ),
                updated_at = NOW()
                WHERE project_id = %s
                """,
                (path, json.dumps(artifact_entry), project_id)
            )
            
            conn.commit()
            cursor.close()
            self.db.putconn(conn)
            
            self._invalidate_cache(project_id)
        except Exception as e:
            raise DatabaseError(f"Failed to register artifact: {str(e)}")
    
    # ========== 辅助方法 ==========
    
    def _insert_project_to_db(self, project: Dict[str, Any]):
        """将项目插入数据库"""
        conn = self.db.getconn()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO projects (
                project_id, version, status, global_spec, budget,
                dna_bank, shots, tasks, locks, artifact_index,
                error_log, change_log, approval_requests, approval_history
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                project['project_id'],
                project['version'],
                project['status'],
                json.dumps(project['global_spec']),
                json.dumps(project['budget']),
                json.dumps(project['dna_bank']),
                json.dumps(project['shots']),
                json.dumps(project['tasks']),
                json.dumps(project['locks']),
                json.dumps(project['artifact_index']),
                json.dumps(project['error_log']),
                json.dumps(project['change_log']),
                json.dumps(project['approval_requests']),
                json.dumps(project['approval_history'])
            )
        )
        
        conn.commit()
        cursor.close()
        self.db.putconn(conn)
    
    def _get_project_from_db(self, project_id: str) -> Optional[Dict[str, Any]]:
        """从数据库获取项目"""
        conn = self.db.getconn()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT 
                project_id, version, status, created_at, updated_at,
                global_spec, budget, dna_bank, shots, tasks, locks,
                artifact_index, error_log, change_log,
                approval_requests, approval_history
            FROM projects
            WHERE project_id = %s
            """,
            (project_id,)
        )
        
        result = cursor.fetchone()
        cursor.close()
        self.db.putconn(conn)
        
        if not result:
            return None
        
        return {
            "project_id": result[0],
            "version": result[1],
            "status": result[2],
            "created_at": result[3].isoformat() if result[3] else None,
            "updated_at": result[4].isoformat() if result[4] else None,
            "global_spec": result[5],
            "budget": result[6],
            "dna_bank": result[7],
            "shots": result[8],
            "tasks": result[9],
            "locks": result[10],
            "artifact_index": result[11],
            "error_log": result[12],
            "change_log": result[13],
            "approval_requests": result[14],
            "approval_history": result[15]
        }
    
    def _invalidate_cache(self, project_id: str):
        """失效缓存"""
        try:
            # 删除项目相关的所有缓存
            patterns = [
                f"project:{project_id}",
                f"project:{project_id}:*"
            ]
            
            for pattern in patterns:
                keys = self.redis.keys(pattern)
                if keys:
                    self.redis.delete(*keys)
        except Exception as e:
            print(f"Cache invalidation failed: {e}")
    
    def _log_change(self, project_id: str, change_type: str, data: Dict[str, Any]):
        """
        记录变更日志
        
        Args:
            project_id: 项目 ID
            change_type: 变更类型
            data: 变更数据
        """
        # TODO: 实现完整的变更日志记录
        pass
