-- Event Bus 数据库 Schema
-- PostgreSQL 14+

-- 1. events 表（事件存储）
CREATE TABLE IF NOT EXISTS events (
    event_id VARCHAR(50) PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    actor VARCHAR(100) NOT NULL,
    causation_id VARCHAR(50),
    timestamp TIMESTAMP NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    blackboard_pointer VARCHAR(500),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_events_project_id ON events(project_id);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_actor ON events(actor);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
CREATE INDEX IF NOT EXISTS idx_events_causation_id ON events(causation_id);

-- JSONB 字段索引
CREATE INDEX IF NOT EXISTS idx_events_payload ON events USING GIN (payload);
CREATE INDEX IF NOT EXISTS idx_events_metadata ON events USING GIN (metadata);

-- 2. event_subscriptions 表（订阅关系）
CREATE TABLE IF NOT EXISTS event_subscriptions (
    id SERIAL PRIMARY KEY,
    subscriber_name VARCHAR(100) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(subscriber_name, event_type)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_subscriptions_subscriber ON event_subscriptions(subscriber_name);
CREATE INDEX IF NOT EXISTS idx_subscriptions_type ON event_subscriptions(event_type);
CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON event_subscriptions(is_active);

-- 3. event_metrics 表（事件指标）
CREATE TABLE IF NOT EXISTS event_metrics (
    id SERIAL PRIMARY KEY,
    project_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    metric_date DATE NOT NULL,
    
    -- 统计指标
    event_count INTEGER NOT NULL DEFAULT 0,
    total_cost DECIMAL(10, 4) DEFAULT 0,
    avg_latency_ms INTEGER DEFAULT 0,
    error_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(project_id, event_type, metric_date)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_metrics_project_date ON event_metrics(project_id, metric_date);
CREATE INDEX IF NOT EXISTS idx_metrics_type ON event_metrics(event_type);

-- 4. causation_chains 表（链路追踪缓存）
CREATE TABLE IF NOT EXISTS causation_chains (
    chain_id SERIAL PRIMARY KEY,
    root_event_id VARCHAR(50) NOT NULL,
    leaf_event_id VARCHAR(50) NOT NULL,
    project_id VARCHAR(50) NOT NULL,
    chain_length INTEGER NOT NULL,
    chain_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    UNIQUE(leaf_event_id)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_chains_root ON causation_chains(root_event_id);
CREATE INDEX IF NOT EXISTS idx_chains_leaf ON causation_chains(leaf_event_id);
CREATE INDEX IF NOT EXISTS idx_chains_project ON causation_chains(project_id);

-- 5. 创建视图：项目事件统计
CREATE OR REPLACE VIEW project_event_stats AS
SELECT 
    project_id,
    event_type,
    COUNT(*) as total_events,
    COUNT(DISTINCT actor) as unique_actors,
    AVG((metadata->>'cost')::numeric) as avg_cost,
    AVG((metadata->>'latency_ms')::numeric) as avg_latency_ms,
    MIN(timestamp) as first_event_at,
    MAX(timestamp) as last_event_at
FROM events
GROUP BY project_id, event_type;

-- 6. 创建函数：更新事件指标
CREATE OR REPLACE FUNCTION update_event_metrics()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO event_metrics (
        project_id,
        event_type,
        metric_date,
        event_count,
        total_cost,
        avg_latency_ms
    )
    VALUES (
        NEW.project_id,
        NEW.event_type,
        DATE(NEW.timestamp),
        1,
        COALESCE((NEW.metadata->>'cost')::numeric, 0),
        COALESCE((NEW.metadata->>'latency_ms')::integer, 0)
    )
    ON CONFLICT (project_id, event_type, metric_date)
    DO UPDATE SET
        event_count = event_metrics.event_count + 1,
        total_cost = event_metrics.total_cost + COALESCE((NEW.metadata->>'cost')::numeric, 0),
        avg_latency_ms = (
            event_metrics.avg_latency_ms * event_metrics.event_count + 
            COALESCE((NEW.metadata->>'latency_ms')::integer, 0)
        ) / (event_metrics.event_count + 1),
        updated_at = NOW();
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 创建触发器
DROP TRIGGER IF EXISTS trigger_update_event_metrics ON events;
CREATE TRIGGER trigger_update_event_metrics
    AFTER INSERT ON events
    FOR EACH ROW
    EXECUTE FUNCTION update_event_metrics();

-- 7. 创建函数：清理过期事件
CREATE OR REPLACE FUNCTION cleanup_old_events(retention_days INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM events
    WHERE timestamp < NOW() - (retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- 完成
SELECT 'Event Bus schema initialized successfully!' AS status;
