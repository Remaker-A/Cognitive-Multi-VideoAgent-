# Shared Blackboard

Shared Blackboard 是 LivingAgentPipeline v2.0 的核心数据存储层，作为单一事实来源（Single Source of Truth），负责存储项目全局状态、shot 数据、DNA Bank、任务队列等。

## 技术栈

- **PostgreSQL 14+**: 主存储，使用 JSONB 存储灵活数据结构
- **Redis 7+**: 缓存层，提升读取性能
- **MinIO/S3**: 对象存储，存储生成的 artifacts

## 快速开始

### 1. 启动基础设施

```bash
# 启动 Docker 服务
docker-compose up -d

# 等待服务就绪并初始化
bash scripts/init_blackboard.sh
```

### 2. 安装依赖

```bash
pip install psycopg2-binary redis boto3
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件配置数据库连接信息
```

### 4. 使用 Blackboard

```python
from src.infrastructure.blackboard.factory import BlackboardFactory

# 创建 Blackboard 实例
blackboard = BlackboardFactory.create()

# 创建项目
project = blackboard.create_project(
    project_id="PROJ-001",
    global_spec={"title": "My Project"},
    budget={"total": 100.0, "used": 0.0}
)

# 获取项目
project = blackboard.get_project("PROJ-001")
```

## 核心功能

### 项目管理

```python
# 创建项目
project = blackboard.create_project(project_id, global_spec, budget)

# 获取项目
project = blackboard.get_project(project_id)

# 更新项目状态
blackboard.update_project_status(project_id, "RENDERING")
```

### 预算管理

```python
# 获取预算
budget = blackboard.get_budget(project_id)

# 更新预算
blackboard.update_budget(project_id, new_budget)

# 增加成本
blackboard.add_cost(project_id, 10.5, "Image generation")
```

### Shot 操作

```python
# 更新 shot
blackboard.update_shot(project_id, shot_id, shot_data)

# 获取 shot
shot = blackboard.get_shot(project_id, shot_id)

# 获取所有 shots
all_shots = blackboard.get_all_shots(project_id)
```

### DNA Bank

```python
# 更新 DNA Bank
blackboard.update_dna_bank(project_id, character_id, dna_entry)

# 获取 DNA Bank
dna_bank = blackboard.get_dna_bank(project_id)
```

### 分布式锁

```python
from src.infrastructure.blackboard import DistributedLock

# 使用上下文管理器
with DistributedLock(blackboard.redis, "my_lock"):
    # 在锁保护下执行操作
    pass
```

## 数据库 Schema

### projects 表

主表，存储项目的所有数据：

- `project_id`: 项目 ID（主键）
- `version`: 版本号（乐观锁）
- `status`: 项目状态
- `global_spec`: 全局规格（JSONB）
- `budget`: 预算信息（JSONB）
- `dna_bank`: DNA Bank（JSONB）
- `shots`: Shots 数据（JSONB）
- `tasks`: 任务队列（JSONB）
- `artifact_index`: Artifact 索引（JSONB）

### change_logs 表

变更日志表，记录所有变更历史。

### distributed_locks 表

分布式锁表（备用，主要使用 Redis）。

### artifacts 表

Artifact 元数据表。

## 缓存策略

### 写策略

**Write-Through**: 写入时同时更新数据库和缓存

### 读策略

**Cache-Aside**: 先读缓存，缓存未命中再读数据库

### 缓存失效

- **TTL**: 1 小时
- **主动失效**: 数据更新时立即失效
- **发布/订阅**: 通知其他实例缓存失效

## 性能优化

### 连接池配置

```python
# PostgreSQL 连接池
db_min_conn = 5
db_max_conn = 20

# Redis 连接池
redis_max_connections = 50
```

### 批量操作

```python
# 批量更新 shots
blackboard.batch_update_shots(project_id, shot_updates)
```

## 测试

### 运行单元测试

```bash
pytest tests/test_blackboard.py -v
```

### 运行集成测试

```bash
# 确保 Docker 服务已启动
docker-compose up -d

# 运行集成测试
pytest tests/test_blackboard.py::test_integration_create_and_get_project -v
```

## 监控

### 健康检查

```python
# PostgreSQL
docker exec blackboard_postgres pg_isready -U postgres

# Redis
docker exec blackboard_redis redis-cli ping

# MinIO
docker exec blackboard_minio mc ls local/artifacts
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f postgres
docker-compose logs -f redis
docker-compose logs -f minio
```

## 故障排查

### 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
docker ps | grep postgres

# 检查连接
docker exec blackboard_postgres psql -U postgres -d blackboard -c "SELECT 1"
```

### Redis 连接失败

```bash
# 检查 Redis 是否运行
docker ps | grep redis

# 测试连接
docker exec blackboard_redis redis-cli ping
```

### 缓存不一致

```bash
# 清空 Redis 缓存
docker exec blackboard_redis redis-cli FLUSHDB
```

## 更多示例

查看 `examples/blackboard_usage.py` 获取更多使用示例。

## 架构文档

详细的架构设计和实现方案请参考：
- `blackboard-implementation.md`: 完整实现方案
- `design.md`: 系统整体设计文档

## License

MIT
