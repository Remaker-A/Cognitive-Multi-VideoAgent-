-- Orchestrator 数据库 Schema
-- PostgreSQL 14+

-- 1. tasks 表（任务存储）
CREATE TABLE IF NOT EXISTS tasks (
    task_id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    assigned_to VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL,
    priority INTEGER NOT NULL,
    
    -- 输入输出
    input JSONB NOT NULL DEFAULT '{}',
    output JSONB,
    
    -- 依赖和锁
    dependencies JSONB DEFAULT '[]',
    requires_lock BOOLEAN DEFAULT FALSE,
    lock_key VARCHAR(200),
    
    -- 预算和成本
    estimated_cost DECIMAL(10, 4) DEFAULT 0,
    actual_cost DECIMAL(10, 4) DEFAULT 0,
    
    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- 链路追踪
    causation_event_id VARCHAR(50),
    
    -- 重试
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    -- 错误信息
    error_message TEXT,
    
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_type ON tasks(task_type);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned_to ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at);

-- JSONB 字段索引
CREATE INDEX IF NOT EXISTS idx_tasks_input ON tasks USING GIN (input);
CREATE INDEX IF NOT EXISTS idx_tasks_output ON tasks USING GIN (output);
CREATE INDEX IF NOT EXISTS idx_tasks_dependencies ON tasks USING GIN (dependencies);

-- 2. task_dependencies 表（任务依赖关系）
CREATE TABLE IF NOT EXISTS task_dependencies (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(50) NOT NULL,
    depends_on VARCHAR(50) NOT NULL,
    dependency_type VARCHAR(50) DEFAULT 'COMPLETION',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(task_id, depends_on)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_task_deps_task_id ON task_dependencies(task_id);
CREATE INDEX IF NOT EXISTS idx_task_deps_depends_on ON task_dependencies(depends_on);

-- 3. approval_requests 表（审批请求）
CREATE TABLE IF NOT EXISTS approval_requests (
    approval_id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    stage VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    
    -- 审批内容
    content JSONB NOT NULL,
    options JSONB DEFAULT '["approve", "revise", "reject"]',
    
    -- 用户决策
    user_decision JSONB,
    
    -- 时间戳
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMP,
    timeout_minutes INTEGER DEFAULT 60,
    
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_approval_project_id ON approval_requests(project_id);
CREATE INDEX IF NOT EXISTS idx_approval_status ON approval_requests(status);
CREATE INDEX IF NOT EXISTS idx_approval_created_at ON approval_requests(created_at);

-- 4. task_metrics 表（任务指标）
CREATE TABLE IF NOT EXISTS task_metrics (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    
    -- 统计指标
    task_count INTEGER NOT NULL DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    avg_duration_seconds INTEGER DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(project_id, task_type, metric_date)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_task_metrics_project_date ON task_metrics(project_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_task_metrics_type ON task_metrics(task_type);

-- 5. 创建视图：项目任务统计
CREATE OR REPLACE VIEW project_task_stats AS
SELECT 
    project_id,
    task_type,
    status,
    COUNT(*) as task_count,
    AVG(actual_cost) as avg_cost,
    AVG(EXTRACT(EPOCH FROM (completed_at - started_at))) as avg_duration_seconds,
    MIN(created_at) as first_task_at,
    MAX(completed_at) as last_completed_at
FROM tasks
WHERE started_at IS NOT NULL
GROUP BY project_id, task_type, status;

-- 6. 创建函数：更新任务指标
CREATE OR REPLACE FUNCTION update_task_metrics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO task_metrics (
        project_id,
        task_type,
        metric_date,
        task_count,
        completed_count,
        failed_count,
        total_cost
    )
    VALUES (
        NEW.project_id,
        NEW.task_type,
        DATE(NEW.created_at),
        1,
        CASE WHEN NEW.status = 'COMPLETED' THEN 1 ELSE 0 END,
        CASE WHEN NEW.status = 'FAILED' THEN 1 ELSE 0 END,
        COALESCE(NEW.actual_cost, 0)
    )
    ON CONFLICT (project_id, task_type, metric_date)
    DO UPDATE SET
        task_count = task_metrics.task_count + 1,
        completed_count = task_metrics.completed_count + 
            CASE WHEN NEW.status = 'COMPLETED' THEN 1 ELSE 0 END,
        failed_count = task_metrics.failed_count + 
            CASE WHEN NEW.status = 'FAILED' THEN 1 ELSE 0 END,
        total_cost = task_metrics.total_cost + COALESCE(NEW.actual_cost, 0),
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_task_metrics ON tasks;
CREATE TRIGGER trigger_update_task_metrics
    AFTER INSERT OR UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_task_metrics();

-- 7. 创建函数：清理过期任务
CREATE OR REPLACE FUNCTION cleanup_old_tasks(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM tasks
    WHERE completed_at < NOW() - (retention_days || ' days')::INTERVAL
    AND status IN ('COMPLETED', 'CANCELLED');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 完成
SELECT 'Orchestrator schema initialized successfully!' AS status;
