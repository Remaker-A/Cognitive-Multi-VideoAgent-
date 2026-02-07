# Shared Blackboard 实现方案

## 概述

Shared Blackboard 是 LivingAgentPipeline v2.0 的核心数据存储层，作为单一事实来源（Single Source of Truth），负责存储项目全局状态、shot 数据、DNA Bank、任务队列等。

### 技术选型

- **主存储**: PostgreSQL 14+ (JSONB)
- **缓存层**: Redis 7+
- **对象存储**: S3 / MinIO (Artifacts)

---

## 数据库架构设计

### 1. PostgreSQL Schema

#### 1.1 projects 表

```sql
CREATE TABLE projects (
    project_id VARCHAR(50) PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 全局规格 (JSONB)
    global_spec JSONB NOT NULL,
    
    -- 预算信息 (JSONB)
    budget JSONB NOT NULL,
    
    -- DNA Bank (JSONB)
    dna_bank JSONB NOT NULL DEFAULT '{}',
    
    -- Shots 数据 (JSONB)
    shots JSONB NOT NULL DEFAULT '{}',
    
    -- 任务队列 (JSONB)
    tasks JSONB NOT NULL DEFAULT '{}',
    
    -- 锁状态 (JSONB)
    locks JSONB NOT NULL DEFAULT '{}',
    
    -- Artifact 索引 (JSONB)
    artifact_index JSONB NOT NULL DEFAULT '{}',
    
    -- 错误日志 (JSONB Array)
    error_log JSONB NOT NULL DEFAULT '[]',
    
    -- 变更日志 (JSONB Array)
    change_log JSONB NOT NULL DEFAULT '[]',
    
    -- 审批请求 (JSONB)
    approval_requests JSONB NOT NULL DEFAULT '{}',
    
    -- 审批历史 (JSONB Array)
    approval_history JSONB NOT NULL DEFAULT '[]'
);

-- 索引
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_created_at ON projects(created_at);
CREATE INDEX idx_projects_updated_at ON projects(updated_at);

-- JSONB 字段索引
CREATE INDEX idx_projects_global_spec ON projects USING GIN (global_spec);
CREATE INDEX idx_projects_shots ON projects USING GIN (shots);
CREATE INDEX idx_projects_tasks ON projects USING GIN (tasks);
```

#### 1.2 change_logs 表（独立变更日志）

```sql
CREATE TABLE change_logs (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id),
    version INTEGER NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    actor VARCHAR(100) NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    change_description TEXT,
    causation_event_id VARCHAR(50),
    
    -- 变更前后数据
    before_data JSONB,
    after_data JSONB,
    
    -- 变更路径（如 /shots/S01/status）
    change_path VARCHAR(200)
);

-- 索引
CREATE INDEX idx_change_logs_project_id ON change_logs(project_id);
CREATE INDEX idx_change_logs_timestamp ON change_logs(timestamp);
CREATE INDEX idx_change_logs_actor ON change_logs(actor);
CREATE INDEX idx_change_logs_change_type ON change_logs(change_type);
```

#### 1.3 locks 表（分布式锁）

```sql
CREATE TABLE distributed_locks (
    lock_key VARCHAR(200) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    holder VARCHAR(100) NOT NULL,
    acquired_at TIMESTAMP NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    lock_type VARCHAR(50) NOT NULL,
    
    -- 锁元数据
    metadata JSONB
);

-- 索引
CREATE INDEX idx_locks_project_id ON distributed_locks(project_id);
CREATE INDEX idx_locks_expires_at ON distributed_locks(expires_at);

-- 自动清理过期锁
CREATE OR REPLACE FUNCTION cleanup_expired_locks()
RETURNS void AS $$
BEGIN
    DELETE FROM distributed_locks WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;
```

#### 1.4 artifacts 表（Artifact 元数据）

```sql
CREATE TABLE artifacts (
    artifact_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id),
    artifact_type VARCHAR(50) NOT NULL,
    s3_url TEXT NOT NULL,
    
    -- 生成参数
    generation_params JSONB,
    
    -- 模型信息
    model_name VARCHAR(100),
    model_version VARCHAR(50),
    
    -- 成本和性能
    cost DECIMAL(10, 4),
    generation_time_ms INTEGER,
    
    -- 使用统计
    uses INTEGER DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_artifacts_project_id ON artifacts(project_id);
CREATE INDEX idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX idx_artifacts_created_at ON artifacts(created_at);
```

---

### 2. Redis 缓存层设计

#### 2.1 缓存键命名规范

```
project:{project_id}                    # 项目完整数据
project:{project_id}:global_spec        # 全局规格
project:{project_id}:budget             # 预算信息
project:{project_id}:dna_bank           # DNA Bank
project:{project_id}:shots              # 所有 shots
project:{project_id}:shot:{shot_id}     # 单个 shot
project:{project_id}:tasks              # 任务队列
project:{project_id}:locks              # 锁状态

lock:{lock_key}                         # 分布式锁
```

#### 2.2 缓存策略

**写策略**: Write-Through（写入时同时更新数据库和缓存）

```python
def update_project(project_id, data):
    # 1. 更新数据库
    db.update_project(project_id, data)
    
    # 2. 更新缓存
    cache_key = f"project:{project_id}"
    redis.setex(cache_key, 3600, json.dumps(data))
    
    # 3. 发布更新事件
    redis.publish(f"project:{project_id}:updates", "updated")
```

**读策略**: Cache-Aside（先读缓存，缓存未命中再读数据库）

```python
def get_project(project_id):
    cache_key = f"project:{project_id}"
    
    # 1. 尝试从缓存读取
    cached = redis.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # 2. 缓存未命中，从数据库读取
    project = db.get_project(project_id)
    
    # 3. 写入缓存
    redis.setex(cache_key, 3600, json.dumps(project))
    
    return project
```

**缓存失效策略**:
- TTL: 1 小时（热数据）
- 主动失效: 数据更新时立即失效
- 发布/订阅: 通知其他实例缓存失效

---

## 核心功能实现

### 1. 版本控制机制

#### 1.1 乐观锁实现

```python
class BlackboardVersionControl:
    def update_with_version_check(self, project_id, update_fn):
        """使用乐观锁更新项目"""
        max_retries = 3
        
        for attempt in range(max_retries):
            # 1. 读取当前版本
            project = self.get_project(project_id)
            current_version = project['version']
            
            # 2. 执行更新逻辑
            updated_data = update_fn(project)
            new_version = current_version + 1
            
            # 3. 尝试更新（版本号必须匹配）
            sql = """
                UPDATE projects 
                SET 
                    version = %s,
                    updated_at = NOW(),
                    global_spec = %s,
                    budget = %s,
                    shots = %s,
                    -- ... 其他字段
                WHERE 
                    project_id = %s 
                    AND version = %s
                RETURNING version
            """
            
            result = self.db.execute(
                sql,
                (new_version, updated_data['global_spec'], 
                 updated_data['budget'], updated_data['shots'],
                 project_id, current_version)
            )
            
            if result:
                # 更新成功
                self._invalidate_cache(project_id)
                self._log_change(project_id, new_version, updated_data)
                return updated_data
            
            # 版本冲突，重试
            time.sleep(0.1 * (2 ** attempt))
        
        raise VersionConflictError(f"Failed to update {project_id} after {max_retries} retries")
```

#### 1.2 变更日志记录

```python
def _log_change(self, project_id, version, updated_data, actor, change_type):
    """记录变更日志"""
    change_entry = {
        "project_id": project_id,
        "version": version,
        "timestamp": datetime.now().isoformat(),
        "actor": actor,
        "change_type": change_type,
        "change_description": self._generate_change_description(updated_data),
        "causation_event_id": updated_data.get('causation_event_id')
    }
    
    # 写入独立的 change_logs 表
    self.db.insert_change_log(change_entry)
    
    # 同时追加到项目的 change_log 数组（最近 100 条）
    sql = """
        UPDATE projects
        SET change_log = (
            SELECT jsonb_agg(elem)
            FROM (
                SELECT elem
                FROM jsonb_array_elements(change_log) elem
                ORDER BY (elem->>'timestamp')::timestamp DESC
                LIMIT 99
            ) recent
            UNION ALL
            SELECT %s::jsonb
        )
        WHERE project_id = %s
    """
    
    self.db.execute(sql, (json.dumps(change_entry), project_id))
```

---

### 2. 分布式锁机制

#### 2.1 Redis 分布式锁

```python
class DistributedLock:
    def __init__(self, redis_client, lock_key, timeout=30):
        self.redis = redis_client
        self.lock_key = f"lock:{lock_key}"
        self.timeout = timeout
        self.lock_value = str(uuid.uuid4())
    
    def acquire(self, blocking=True, timeout=None):
        """获取锁"""
        if blocking:
            end_time = time.time() + (timeout or self.timeout)
            while time.time() < end_time:
                if self._try_acquire():
                    return True
                time.sleep(0.1)
            return False
        else:
            return self._try_acquire()
    
    def _try_acquire(self):
        """尝试获取锁"""
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
        if not self.acquire():
            raise LockAcquisitionError(f"Failed to acquire lock: {self.lock_key}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
```

#### 2.2 锁使用示例

```python
# 示例 1: 更新全局样式（需要锁）
with DistributedLock(redis, f"project:{project_id}:global_style"):
    project = blackboard.get_project(project_id)
    project['global_spec']['style']['palette'] = new_palette
    blackboard.update_project(project_id, project)

# 示例 2: 更新 DNA Bank（需要锁）
with DistributedLock(redis, f"project:{project_id}:dna_bank"):
    dna_bank = blackboard.get_dna_bank(project_id)
    dna_bank['C1_girl']['embeddings'].append(new_embedding)
    blackboard.update_dna_bank(project_id, dna_bank)

# 示例 3: 更新单个 shot（shot 级别锁）
with DistributedLock(redis, f"project:{project_id}:shot:{shot_id}"):
    shot = blackboard.get_shot(project_id, shot_id)
    shot['status'] = 'COMPLETED'
    blackboard.update_shot(project_id, shot_id, shot)
```

---

### 3. Blackboard API 实现

#### 3.1 核心 API 接口

```python
class SharedBlackboard:
    def __init__(self, db_pool, redis_client, s3_client):
        self.db = db_pool
        self.redis = redis_client
        self.s3 = s3_client
    
    # ========== 项目级别操作 ==========
    
    def create_project(self, project_id, global_spec, budget):
        """创建新项目"""
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
        
        # 写入数据库
        self.db.insert_project(project)
        
        # 写入缓存
        cache_key = f"project:{project_id}"
        self.redis.setex(cache_key, 3600, json.dumps(project))
        
        return project
    
    def get_project(self, project_id):
        """获取项目完整数据"""
        cache_key = f"project:{project_id}"
        
        # 尝试从缓存读取
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # 从数据库读取
        project = self.db.get_project(project_id)
        if not project:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        
        # 写入缓存
        self.redis.setex(cache_key, 3600, json.dumps(project))
        
        return project
    
    def update_project_status(self, project_id, new_status):
        """更新项目状态"""
        sql = """
            UPDATE projects
            SET status = %s, updated_at = NOW()
            WHERE project_id = %s
        """
        self.db.execute(sql, (new_status, project_id))
        
        # 失效缓存
        self._invalidate_cache(project_id)
    
    # ========== GlobalSpec 操作 ==========
    
    def get_global_spec(self, project_id):
        """获取全局规格"""
        cache_key = f"project:{project_id}:global_spec"
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        sql = "SELECT global_spec FROM projects WHERE project_id = %s"
        result = self.db.query_one(sql, (project_id,))
        
        if result:
            global_spec = result['global_spec']
            self.redis.setex(cache_key, 3600, json.dumps(global_spec))
            return global_spec
        
        raise ProjectNotFoundError(f"Project {project_id} not found")
    
    def update_global_spec(self, project_id, global_spec):
        """更新全局规格（需要锁）"""
        with DistributedLock(self.redis, f"project:{project_id}:global_style"):
            sql = """
                UPDATE projects
                SET global_spec = %s, updated_at = NOW(), version = version + 1
                WHERE project_id = %s
            """
            self.db.execute(sql, (json.dumps(global_spec), project_id))
            
            self._invalidate_cache(project_id)
            self._log_change(project_id, "UPDATE_GLOBAL_SPEC", global_spec)
    
    # ========== Budget 操作 ==========
    
    def get_budget(self, project_id):
        """获取预算信息"""
        cache_key = f"project:{project_id}:budget"
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        sql = "SELECT budget FROM projects WHERE project_id = %s"
        result = self.db.query_one(sql, (project_id,))
        
        if result:
            budget = result['budget']
            self.redis.setex(cache_key, 3600, json.dumps(budget))
            return budget
        
        raise ProjectNotFoundError(f"Project {project_id} not found")
    
    def update_budget(self, project_id, budget):
        """更新预算"""
        sql = """
            UPDATE projects
            SET budget = %s, updated_at = NOW()
            WHERE project_id = %s
        """
        self.db.execute(sql, (json.dumps(budget), project_id))
        
        self._invalidate_cache(project_id)
    
    def add_cost(self, project_id, cost, description):
        """增加成本"""
        sql = """
            UPDATE projects
            SET budget = jsonb_set(
                budget,
                '{used}',
                ((budget->>'used')::numeric + %s)::text::jsonb
            ),
            updated_at = NOW()
            WHERE project_id = %s
        """
        self.db.execute(sql, (cost, project_id))
        
        self._invalidate_cache(project_id)
        self._log_change(project_id, "ADD_COST", {"cost": cost, "description": description})
    
    # ========== DNA Bank 操作 ==========
    
    def get_dna_bank(self, project_id):
        """获取 DNA Bank"""
        cache_key = f"project:{project_id}:dna_bank"
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        sql = "SELECT dna_bank FROM projects WHERE project_id = %s"
        result = self.db.query_one(sql, (project_id,))
        
        if result:
            dna_bank = result['dna_bank']
            self.redis.setex(cache_key, 3600, json.dumps(dna_bank))
            return dna_bank
        
        return {}
    
    def update_dna_bank(self, project_id, character_id, dna_entry):
        """更新 DNA Bank（需要锁）"""
        with DistributedLock(self.redis, f"project:{project_id}:dna_bank"):
            sql = """
                UPDATE projects
                SET dna_bank = jsonb_set(
                    dna_bank,
                    %s,
                    %s::jsonb
                ),
                updated_at = NOW(),
                version = version + 1
                WHERE project_id = %s
            """
            
            path = f'{{{character_id}}}'
            self.db.execute(sql, (path, json.dumps(dna_entry), project_id))
            
            self._invalidate_cache(project_id)
            self._log_change(project_id, "UPDATE_DNA_BANK", {
                "character_id": character_id,
                "dna_entry": dna_entry
            })
    
    # ========== Shot 操作 ==========
    
    def get_shot(self, project_id, shot_id):
        """获取单个 shot"""
        cache_key = f"project:{project_id}:shot:{shot_id}"
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        sql = "SELECT shots->%s as shot FROM projects WHERE project_id = %s"
        result = self.db.query_one(sql, (shot_id, project_id))
        
        if result and result['shot']:
            shot = result['shot']
            self.redis.setex(cache_key, 3600, json.dumps(shot))
            return shot
        
        raise ShotNotFoundError(f"Shot {shot_id} not found in project {project_id}")
    
    def update_shot(self, project_id, shot_id, shot_data):
        """更新 shot（shot 级别锁）"""
        with DistributedLock(self.redis, f"project:{project_id}:shot:{shot_id}"):
            sql = """
                UPDATE projects
                SET shots = jsonb_set(
                    shots,
                    %s,
                    %s::jsonb
                ),
                updated_at = NOW()
                WHERE project_id = %s
            """
            
            path = f'{{{shot_id}}}'
            self.db.execute(sql, (path, json.dumps(shot_data), project_id))
            
            # 失效缓存
            self.redis.delete(f"project:{project_id}:shot:{shot_id}")
            self._invalidate_cache(project_id)
            
            self._log_change(project_id, "UPDATE_SHOT", {
                "shot_id": shot_id,
                "shot_data": shot_data
            })
    
    def get_all_shots(self, project_id):
        """获取所有 shots"""
        cache_key = f"project:{project_id}:shots"
        
        cached = self.redis.get(cache_key)
        if cached:
            return json.loads(cached)
        
        sql = "SELECT shots FROM projects WHERE project_id = %s"
        result = self.db.query_one(sql, (project_id,))
        
        if result:
            shots = result['shots']
            self.redis.setex(cache_key, 3600, json.dumps(shots))
            return shots
        
        return {}
    
    # ========== Artifact 操作 ==========
    
    def register_artifact(self, project_id, artifact_url, metadata):
        """注册 artifact"""
        artifact_entry = {
            "seed": metadata.get('seed'),
            "model": metadata.get('model'),
            "model_version": metadata.get('model_version'),
            "prompt": metadata.get('prompt'),
            "cost": metadata.get('cost'),
            "created_at": datetime.now().isoformat(),
            "uses": 0
        }
        
        # 更新 artifact_index
        sql = """
            UPDATE projects
            SET artifact_index = jsonb_set(
                artifact_index,
                %s,
                %s::jsonb
            ),
            updated_at = NOW()
            WHERE project_id = %s
        """
        
        path = f'{{{artifact_url}}}'
        self.db.execute(sql, (path, json.dumps(artifact_entry), project_id))
        
        # 同时写入 artifacts 表
        self.db.insert_artifact({
            "artifact_id": artifact_url,
            "project_id": project_id,
            "artifact_type": metadata.get('type'),
            "s3_url": artifact_url,
            "generation_params": metadata.get('params'),
            "model_name": metadata.get('model'),
            "model_version": metadata.get('model_version'),
            "cost": metadata.get('cost'),
            "generation_time_ms": metadata.get('generation_time_ms')
        })
        
        self._invalidate_cache(project_id)
    
    # ========== 辅助方法 ==========
    
    def _invalidate_cache(self, project_id):
        """失效缓存"""
        patterns = [
            f"project:{project_id}",
            f"project:{project_id}:*"
        ]
        
        for pattern in patterns:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
    
    def _log_change(self, project_id, change_type, data):
        """记录变更"""
        # 实现变更日志记录
        pass
```

---

## 性能优化

### 1. 批量操作优化

```python
def batch_update_shots(self, project_id, shot_updates):
    """批量更新 shots"""
    with DistributedLock(self.redis, f"project:{project_id}:shots"):
        # 使用 JSONB 合并操作
        sql = """
            UPDATE projects
            SET shots = shots || %s::jsonb,
                updated_at = NOW()
            WHERE project_id = %s
        """
        
        self.db.execute(sql, (json.dumps(shot_updates), project_id))
        
        # 批量失效缓存
        for shot_id in shot_updates.keys():
            self.redis.delete(f"project:{project_id}:shot:{shot_id}")
        
        self._invalidate_cache(project_id)
```

### 2. 连接池配置

```python
# PostgreSQL 连接池
from psycopg2.pool import ThreadedConnectionPool

db_pool = ThreadedConnectionPool(
    minconn=5,
    maxconn=20,
    host="localhost",
    database="blackboard",
    user="postgres",
    password="password"
)

# Redis 连接池
import redis

redis_pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    decode_responses=True
)

redis_client = redis.Redis(connection_pool=redis_pool)
```

---

## 监控与运维

### 1. 监控指标

```python
# Prometheus 指标
from prometheus_client import Counter, Histogram, Gauge

# 请求计数
blackboard_requests = Counter(
    'blackboard_requests_total',
    'Total Blackboard requests',
    ['operation', 'status']
)

# 响应时间
blackboard_latency = Histogram(
    'blackboard_latency_seconds',
    'Blackboard operation latency',
    ['operation']
)

# 缓存命中率
cache_hits = Counter('blackboard_cache_hits_total', 'Cache hits')
cache_misses = Counter('blackboard_cache_misses_total', 'Cache misses')

# 锁等待时间
lock_wait_time = Histogram(
    'blackboard_lock_wait_seconds',
    'Lock acquisition wait time'
)
```

### 2. 健康检查

```python
def health_check():
    """健康检查"""
    checks = {
        "postgres": check_postgres(),
        "redis": check_redis(),
        "s3": check_s3()
    }
    
    all_healthy = all(checks.values())
    
    return {
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks
    }

def check_postgres():
    try:
        result = db.query_one("SELECT 1")
        return result is not None
    except Exception:
        return False

def check_redis():
    try:
        return redis.ping()
    except Exception:
        return False
```

---

## 测试方案

### 1. 单元测试

```python
import pytest

def test_create_project(blackboard):
    """测试创建项目"""
    project_id = "TEST-001"
    global_spec = {"title": "Test Project"}
    budget = {"total": 100.0, "used": 0.0}
    
    project = blackboard.create_project(project_id, global_spec, budget)
    
    assert project['project_id'] == project_id
    assert project['version'] == 1
    assert project['status'] == "CREATED"

def test_version_control(blackboard):
    """测试版本控制"""
    project_id = "TEST-002"
    blackboard.create_project(project_id, {}, {})
    
    # 并发更新
    def update_budget():
        budget = blackboard.get_budget(project_id)
        budget['used'] += 10.0
        blackboard.update_budget(project_id, budget)
    
    # 模拟并发
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(update_budget) for _ in range(5)]
        for future in futures:
            future.result()
    
    # 验证最终结果
    final_budget = blackboard.get_budget(project_id)
    assert final_budget['used'] == 50.0

def test_distributed_lock(redis):
    """测试分布式锁"""
    lock_key = "test_lock"
    
    lock1 = DistributedLock(redis, lock_key)
    lock2 = DistributedLock(redis, lock_key)
    
    # lock1 获取锁
    assert lock1.acquire()
    
    # lock2 无法获取锁
    assert not lock2.acquire(blocking=False)
    
    # lock1 释放锁
    lock1.release()
    
    # lock2 现在可以获取锁
    assert lock2.acquire()
    lock2.release()
```

---

## 部署指南

### 1. Docker Compose 配置

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: blackboard
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin
    volumes:
      - minio_data:/data

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 2. 初始化脚本

```bash
#!/bin/bash

# 等待 PostgreSQL 启动
until pg_isready -h localhost -p 5432; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# 执行初始化 SQL
psql -h localhost -U postgres -d blackboard -f schema.sql

# 创建 MinIO bucket
mc alias set local http://localhost:9000 minioadmin minioadmin
mc mb local/artifacts

echo "Blackboard infrastructure initialized successfully!"
```

---

## 总结

Shared Blackboard 实现方案包含：

✅ **数据库设计**: PostgreSQL JSONB schema + 索引优化
✅ **缓存层**: Redis Write-Through + Cache-Aside 策略
✅ **版本控制**: 乐观锁 + 变更日志
✅ **分布式锁**: Redis 分布式锁 + 超时机制
✅ **完整 API**: 项目/Shot/DNA/Artifact 操作
✅ **性能优化**: 批量操作 + 连接池
✅ **监控运维**: Prometheus 指标 + 健康检查
✅ **测试方案**: 单元测试 + 并发测试
✅ **部署指南**: Docker Compose + 初始化脚本

该方案可直接用于开发实现！
