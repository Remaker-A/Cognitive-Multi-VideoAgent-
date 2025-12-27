-- Shared Blackboard 数据库 Schema
-- PostgreSQL 14+

-- 1. projects 表（主表）
CREATE TABLE IF NOT EXISTS projects (
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
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);
CREATE INDEX IF NOT EXISTS idx_projects_updated_at ON projects(updated_at);

-- JSONB 字段索引
CREATE INDEX IF NOT EXISTS idx_projects_global_spec ON projects USING GIN (global_spec);
CREATE INDEX IF NOT EXISTS idx_projects_shots ON projects USING GIN (shots);
CREATE INDEX IF NOT EXISTS idx_projects_tasks ON projects USING GIN (tasks);

-- 2. change_logs 表（独立变更日志）
CREATE TABLE IF NOT EXISTS change_logs (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS idx_change_logs_project_id ON change_logs(project_id);
CREATE INDEX IF NOT EXISTS idx_change_logs_timestamp ON change_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_change_logs_actor ON change_logs(actor);
CREATE INDEX IF NOT EXISTS idx_change_logs_change_type ON change_logs(change_type);

-- 3. distributed_locks 表（分布式锁）
CREATE TABLE IF NOT EXISTS distributed_locks (
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
CREATE INDEX IF NOT EXISTS idx_locks_project_id ON distributed_locks(project_id);
CREATE INDEX IF NOT EXISTS idx_locks_expires_at ON distributed_locks(expires_at);

-- 自动清理过期锁
CREATE OR REPLACE FUNCTION cleanup_expired_locks()
RETURNS void AS $$
BEGIN
    DELETE FROM distributed_locks WHERE expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- 4. artifacts 表（Artifact 元数据）
CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id VARCHAR(100) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL REFERENCES projects(project_id) ON DELETE CASCADE,
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
CREATE INDEX IF NOT EXISTS idx_artifacts_project_id ON artifacts(project_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_type ON artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS idx_artifacts_created_at ON artifacts(created_at);

-- 5. 创建定时任务清理过期锁（可选）
-- 需要 pg_cron 扩展
-- CREATE EXTENSION IF NOT EXISTS pg_cron;
-- SELECT cron.schedule('cleanup-locks', '*/5 * * * *', 'SELECT cleanup_expired_locks()');

-- 完成
SELECT 'Blackboard schema initialized successfully!' AS status;
