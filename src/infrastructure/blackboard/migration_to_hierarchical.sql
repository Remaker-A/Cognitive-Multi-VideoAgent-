-- Migration脚本：从单层Project到三层架构
-- 用于将现有Project数据迁移到Episode
-- PostgreSQL 14+

BEGIN;

-- =============================================
-- 辅助函数：将Project迁移为Episode
-- =============================================

CREATE OR REPLACE FUNCTION migrate_project_to_episode(
    p_project_id VARCHAR(255),
    p_series_id VARCHAR(255),
    p_episode_number INTEGER
)
RETURNS VARCHAR(255) AS $$
DECLARE
    v_episode_id VARCHAR(255);
    v_project_data RECORD;
BEGIN
    -- 1. 读取Project数据
    SELECT * INTO v_project_data
    FROM projects
    WHERE project_id = p_project_id;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Project % not found', p_project_id;
    END IF;
    
    -- 2. 生成Episode ID
    v_episode_id := p_series_id || '-EP' || LPAD(p_episode_number::TEXT, 3, '0');
    
    -- 3. 创建Episode记录
    INSERT INTO episodes (
        episode_id,
        episode_number,
        series_id,
        version,
        status,
        script,
        episode_budget,
        artifact_index,
        created_at,
        updated_at
    ) VALUES (
        v_episode_id,
        p_episode_number,
        p_series_id,
        v_project_data.version,
        v_project_data.status,
        jsonb_build_object(
            'scenes', '[]'::jsonb,
            'totalDuration', 0,
            'status', 'draft',
            'version', 1
        ),
        v_project_data.budget,
        v_project_data.artifact_index,
        v_project_data.created_at,
        v_project_data.updated_at
    );
    
    -- 4. 迁移Shots数据
    -- 将project.shots (JSONB) 中的每个shot迁移到shots表
    INSERT INTO shots (
        shot_id,
        shot_number,
        episode_id,
        series_id,
        status,
        shot_spec,
        artifacts,
        created_at,
        updated_at
    )
    SELECT 
        key AS shot_id,
        ROW_NUMBER() OVER (ORDER BY key) AS shot_number,
        v_episode_id,
        p_series_id,
        COALESCE(value->>'status', 'planned'),
        COALESCE(value->'shot_spec', '{}'::jsonb),
        COALESCE(value->'artifacts', '{}'::jsonb),
        NOW(),
        NOW()
    FROM jsonb_each(v_project_data.shots);
    
    RETURN v_episode_id;
END;
$$ LANGUAGE plpgsql;

-- =============================================
-- 示例：迁移现有Projects到新Series
-- =============================================

-- 注释掉，仅作为示例，实际使用时取消注释并调整参数

/*
-- 1. 创建一个测试Series
INSERT INTO series (
    series_id,
    status,
    series_spec,
    series_budget
) VALUES (
    'TEST-SERIES-001',
    'in_progress',
    jsonb_build_object(
        'title', '测试剧集',
        'totalEpisodes', 3,
        'platform', 'douyin',
        'aspectRatio', '9:16'
    ),
    jsonb_build_object(
        'totalBudget', 1000.0,
        'usedBudget', 0.0,
        'predictedBudget', 800.0,
        'perEpisodeCap', 333.0,
        'reuseTarget', 0.8,
        'actualReuseRate', 0.0
    )
);

-- 2. 迁移现有Projects（假设有PROJECT-001, PROJECT-002, PROJECT-003）
SELECT migrate_project_to_episode('PROJECT-001', 'TEST-SERIES-001', 1);
SELECT migrate_project_to_episode('PROJECT-002', 'TEST-SERIES-001', 2);
SELECT migrate_project_to_episode('PROJECT-003', 'TEST-SERIES-001', 3);

-- 3. 验证迁移结果
SELECT 
    e.episode_id,
    e.episode_number,
    e.series_id,
    COUNT(s.shot_id) AS total_shots
FROM episodes e
LEFT JOIN shots s ON e.episode_id = s.episode_id
WHERE e.series_id = 'TEST-SERIES-001'
GROUP BY e.episode_id, e.episode_number, e.series_id
ORDER BY e.episode_number;
*/

-- =============================================
-- 回滚脚本（谨慎使用）
-- =============================================

CREATE OR REPLACE FUNCTION rollback_migration(p_series_id VARCHAR(255))
RETURNS void AS $$
BEGIN
    -- 删除该Series下的所有数据（级联删除会自动处理Episodes和Shots）
    DELETE FROM series WHERE series_id = p_series_id;
    
    RAISE NOTICE 'Rolled back migration for series %', p_series_id;
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- 完成
SELECT 'Migration utilities created successfully!' AS status;
