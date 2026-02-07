-- 三层黑板架构 Schema
-- 从单一Project级别迁移到Series/Episode/Shot三层架构
-- PostgreSQL 14+

-- =============================================
-- 1. Series表（系列级黑板）
-- =============================================

CREATE TABLE IF NOT EXISTS series (
    series_id VARCHAR(255) PRIMARY KEY,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL,
    
    -- Series规格
    series_spec JSONB NOT NULL,
    -- {
    --   "title": "剧集标题",
    --   "totalEpisodes": 10,
    --   "episodeDurationRange": {"min": 60, "max": 120},
    --   "platform": "douyin",
    --   "aspectRatio": "9:16",
    --   "targetQuality": "preview_then_final"
    -- }
    
    -- Series Bible（剧集圣经）
    show_bible JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "worldRules": ["规则1", "规则2"],
    --   "characters": [{...}],
    --   "relationships": {...},
    --   "taboos": ["禁忌1"],
    --   "themes": ["主题1"],
    --   "toneGuidelines": "轻松幽默",
    --   "locked": false
    -- }
    
    -- Asset Registry（资产注册表）
    asset_registry JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "characters": {"char-001": {...}},
    --   "scenes": {"scene-001": {...}},
    --   "shots": {"shot-001": {...}},
    --   "audio": {"audio-001": {...}},
    --   "lockedAssets": ["char-001"]
    -- }
    
    -- Continuity Ledger（连续性账本）
    continuity_ledger JSONB NOT NULL DEFAULT '[]',
    
    -- Series Budget（系列预算）
    series_budget JSONB NOT NULL,
    -- {
    --   "totalBudget": 1000.0,
    --   "usedBudget": 350.5,
    --   "predictedBudget": 800.0,
    --   "perEpisodeCap": 100.0,
    --   "reuseTarget": 0.8,
    --   "actualReuseRate": 0.75
    -- }
    
    -- Change Log（变更日志）
    change_log JSONB NOT NULL DEFAULT '[]',
    
    -- Collaborators（协作者）
    collaborators JSONB NOT NULL DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_series_status ON series(status);
CREATE INDEX IF NOT EXISTS idx_series_created_at ON series(created_at);
CREATE INDEX IF NOT EXISTS idx_series_updated_at ON series(updated_at);

-- JSONB索引
CREATE INDEX IF NOT EXISTS idx_series_spec ON series USING GIN (series_spec);
CREATE INDEX IF NOT EXISTS idx_series_bible ON series USING GIN (show_bible);
CREATE INDEX IF NOT EXISTS idx_series_asset_registry ON series USING GIN (asset_registry);

-- =============================================
-- 2. Episodes表（单集级黑板）
-- =============================================

CREATE TABLE IF NOT EXISTS episodes (
    episode_id VARCHAR(255) PRIMARY KEY,
    episode_number INTEGER NOT NULL,
    series_id VARCHAR(255) NOT NULL REFERENCES series(series_id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL,
    
    -- Outline（大纲）
    outline JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "coreConflict": "核心冲突",
    --   "plotPoints": [...],
    --   "characterArcs": {...},
    --   "emotionalBeats": [...],
    --   "status": "draft",
    --   "version": 1
    -- }
    
    -- Script（剧本）
    script JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "scenes": [...],
    --   "totalDuration": 90,
    --   "status": "draft",
    --   "version": 1
    -- }
    
    -- Storyboard（分镜）
    storyboard JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "shots": [...],
    --   "totalShots": 20,
    --   "totalDuration": 90,
    --   "status": "draft",
    --   "version": 1
    -- }
    
    -- Episode Budget（单集预算）
    episode_budget JSONB NOT NULL,
    -- {
    --   "allocated": 100.0,
    --   "used": 45.5,
    --   "predicted": 95.0,
    --   "breakdown": {
    --     "keyframes": 20.0,
    --     "videos": 60.0,
    --     "audio": 10.0,
    --     "qa": 5.0,
    --     "retries": 0.5
    --   }
    -- }
    
    -- QA Report（质量报告）
    qa_report JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "overallScore": 0.85,
    --   "passedShots": 18,
    --   "failedShots": 2,
    --   "manualReviewShots": 0,
    --   "issueBreakdown": {...},
    --   "autoFixSuccessRate": 0.9,
    --   "generatedAt": "2026-01-08T10:00:00Z"
    -- }
    
    -- Assembled Video（剪辑视频）
    assembled_video JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "previewUrl": "s3://...",
    --   "finalUrl": "s3://...",
    --   "subtitlesUrl": "s3://...",
    --   "duration": 90,
    --   "resolution": "1080x1920",
    --   "fileSize": 52428800
    -- }
    
    -- Approval State（审批状态）
    approval_state JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "SCENE_WRITTEN": false,
    --   "PREVIEW_VIDEO_READY": false,
    --   "FINAL_VIDEO_READY": false
    -- }
    
    -- Change Log（变更日志）
    change_log JSONB NOT NULL DEFAULT '[]',
    
    -- Artifact Index（产物索引）
    artifact_index JSONB NOT NULL DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 约束：同一系列内Episode编号唯一
    UNIQUE(series_id, episode_number)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_episodes_series_id ON episodes(series_id);
CREATE INDEX IF NOT EXISTS idx_episodes_status ON episodes(status);
CREATE INDEX IF NOT EXISTS idx_episodes_episode_number ON episodes(episode_number);
CREATE INDEX IF NOT EXISTS idx_episodes_created_at ON episodes(created_at);

-- JSONB索引
CREATE INDEX IF NOT EXISTS idx_episodes_outline ON episodes USING GIN (outline);
CREATE INDEX IF NOT EXISTS idx_episodes_script ON episodes USING GIN (script);
CREATE INDEX IF NOT EXISTS idx_episodes_storyboard ON episodes USING GIN (storyboard);

-- =============================================
-- 3. Shots表（镜头级黑板 - 重构）
-- =============================================

CREATE TABLE IF NOT EXISTS shots (
    shot_id VARCHAR(255) PRIMARY KEY,
    shot_number INTEGER NOT NULL,
    scene_id VARCHAR(255),
    episode_id VARCHAR(255) NOT NULL REFERENCES episodes(episode_id) ON DELETE CASCADE,
    series_id VARCHAR(255) NOT NULL REFERENCES series(series_id) ON DELETE CASCADE,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL,
    
    -- Shot Spec（镜头规格）
    shot_spec JSONB NOT NULL,
    -- {
    --   "duration": 5,
    --   "camera": {
    --     "shotType": "medium",
    --     "lens": "35mm",
    --     "movement": "static",
    --     "angle": "eye_level"
    --   },
    --   "actors": ["char-001"],
    --   "scene": "scene-001",
    --   "action": "角色走进房间",
    --   "dialogue": {...},
    --   "styleTags": ["realistic", "moody"],
    --   "constraints": {
    --     "mustKeep": ["角色服装"],
    --     "mustAvoid": ["暴力内容"]
    --   }
    -- }
    
    -- Referenced Assets（引用的资产）
    referenced_assets JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "characterDNA": ["char-001"],
    --   "sceneDNA": "scene-001",
    --   "shotDNA": null,
    --   "audioDNA": null
    -- }
    
    -- Prompt Pack（提示词包）
    prompt_pack JSONB,
    
    -- Generation Plan（生成计划）
    generation_plan JSONB,
    
    -- Artifacts（产物）
    artifacts JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "keyframes": [...],
    --   "previewVideo": {...},
    --   "finalVideo": {...},
    --   "audio": {...}
    -- }
    
    -- QA Results（质量检查结果）
    qa_results JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "faceIdentityScore": 0.92,
    --   "paletteConsistencyScore": 0.88,
    --   "crossShotContinuityScore": 0.85,
    --   "lipSyncScore": null,
    --   "issues": [...],
    --   "autoFixAttempts": 1,
    --   "status": "passed"
    -- }
    
    -- Cost Ledger（成本账本）
    cost_ledger JSONB NOT NULL DEFAULT '{}',
    -- {
    --   "keyframeGeneration": 0.05,
    --   "videoGeneration": 0.25,
    --   "audioGeneration": 0.0,
    --   "qaAndFix": 0.02,
    --   "retries": 0.03,
    --   "total": 0.35
    -- }
    
    -- Artifact Index（产物索引）
    artifact_index JSONB NOT NULL DEFAULT '[]',
    
    -- Change History（变更历史）
    change_history JSONB NOT NULL DEFAULT '[]',
    
    -- Metadata
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    -- 约束：同一Episode内Shot编号唯一
    UNIQUE(episode_id, shot_number)
);

-- 索引
CREATE INDEX IF NOT EXISTS idx_shots_episode_id ON shots(episode_id);
CREATE INDEX IF NOT EXISTS idx_shots_series_id ON shots(series_id);
CREATE INDEX IF NOT EXISTS idx_shots_status ON shots(status);
CREATE INDEX IF NOT EXISTS idx_shots_shot_number ON shots(shot_number);
CREATE INDEX IF NOT EXISTS idx_shots_created_at ON shots(created_at);

-- JSONB索引
CREATE INDEX IF NOT EXISTS idx_shots_spec ON shots USING GIN (shot_spec);
CREATE INDEX IF NOT EXISTS idx_shots_artifacts ON shots USING GIN (artifacts);
CREATE INDEX IF NOT EXISTS idx_shots_qa_results ON shots USING GIN (qa_results);

-- =============================================
-- 4. 视图：便捷查询
-- =============================================

-- 视图：获取完整的Shot上下文（包含Series和Episode信息）
CREATE OR REPLACE VIEW shot_full_context AS
SELECT 
    s.shot_id,
    s.shot_number,
    s.status AS shot_status,
    s.shot_spec,
    s.artifacts,
    s.qa_results,
    e.episode_id,
    e.episode_number,
    e.status AS episode_status,
    e.script,
    ser.series_id,
    ser.series_spec,
    ser.show_bible,
    ser.asset_registry
FROM shots s
JOIN episodes e ON s.episode_id = e.episode_id
JOIN series ser ON e.series_id = ser.series_id;

-- 视图：Series统计信息
CREATE OR REPLACE VIEW series_statistics AS
SELECT 
    s.series_id,
    s.series_spec->>'title' AS title,
    s.status,
    COUNT(DISTINCT e.episode_id) AS total_episodes_created,
    COUNT(DISTINCT sh.shot_id) AS total_shots_created,
    s.series_budget->>'totalBudget' AS total_budget,
    s.series_budget->>'usedBudget' AS used_budget,
    s.series_budget->>'actualReuseRate' AS actual_reuse_rate,
    s.created_at,
    s.updated_at
FROM series s
LEFT JOIN episodes e ON s.series_id = e.series_id
LEFT JOIN shots sh ON e.episode_id = sh.episode_id
GROUP BY s.series_id;

-- =============================================
-- 5. 触发器：自动更新updated_at
-- =============================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_series_updated_at
    BEFORE UPDATE ON series
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_episodes_updated_at
    BEFORE UPDATE ON episodes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_shots_updated_at
    BEFORE UPDATE ON shots
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- 6. 向后兼容：保留projects表（可选）
-- =============================================
-- 注意：现有的projects表保持不变，用于向后兼容
-- 新功能使用series/episodes/shots三层表

-- 完成
SELECT 'Three-tier Blackboard schema created successfully!' AS status,
       'Series, Episodes, and Shots tables are ready.' AS details;
