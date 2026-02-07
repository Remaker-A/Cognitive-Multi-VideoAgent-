# LivingAgentPipeline v2.0 统一设计文档

**版本**: 2.0  
**日期**: 2025-11-16  
**状态**: 已批准

---

## 执行摘要

本文档整合了四份原始设计文档，创建了统一、优化、工程可落地的 LivingAgentPipeline 系统设计。

### 核心优化

1. **统一架构**: 明确 12 个 Agent 的职责和交互方式
2. **Task vs Event**: 清晰区分事件通知和任务执行
3. **Audio Strategy**: 简化音频决策逻辑，支持模型集成音频
4. **DNA Bank**: 多版本管理，支持渐进优化
5. **Editor Agent**: 补充完整的视频剪辑和音频混合设计
6. **跨 Shot 连贯性**: 检测相邻镜头的视觉和时间连贯性
7. **成本控制**: 实时追踪和预测，动态优化
8. **错误恢复**: 三层策略，自动化率 > 90%
9. **用户审批检查点**: 关键阶段支持用户审查和确认，确保生成内容符合预期

### 系统特点

- **事件驱动**: Agent 松耦合，通过事件异步通信
- **单一事实来源**: Shared Blackboard 保证数据一致性
- **可追溯**: 完整的链路追踪和成本核算
- **容错性强**: 多层次自动修复和降级
- **可扩展**: 标准化接口，易于新增 Agent 和模型

---

## 系统架构

### 三层架构

**L1: Interaction Layer** - RequirementParser Agent  
**L2: Cognitive Multi-Agent Layer** - 12 个核心 Agent  
**L3: Infrastructure & Model Runtime** - Orchestrator, Event Bus, Blackboard

### 12 个核心 Agent

| Agent | 职责 | 关键能力 |
|-------|------|---------|
| ChefAgent | 总监，预算控制，熔断决策 | 预算分配、风险评估、人工决策 |
| RequirementParser | 需求解析，生成 GlobalSpec | NLP 解析、置信度计算 |
| ScriptWriter | 编写剧本，分镜，情绪标注 | LLM 生成、shot 分解 |
| ShotDirector | Shot 规划，镜头语言 | Camera 设计、运镜规划 |
| ArtDirector | DNA 管理，特征提取 | Face/Color/Texture 提取、加权合并 |
| PromptEngineer | Prompt 编织，A/B 测试 | 模板管理、DNA token 注入 |
| ImageGen | 图像生成 | ControlNet、Embedding 提取 |
| VideoGen | 视频生成 | 运动注入、时间连贯性 |
| MusicComposer | 音乐生成 | Mood embedding、Markers 标注 |
| VoiceActor | 配音生成 | TTS、Phoneme 对齐 |
| Editor | 视频剪辑，音频混合 | Shot 拼接、Audio ducking |
| ConsistencyGuardian | QA 检测，自动修复 | 多模态检测、动态阈值 |

---

## 核心机制

### Event vs Task

**Event（事件）**: Agent 间的异步通知，表示"某事已发生"  
**Task（任务）**: Orchestrator 分配的工作单元，表示"需要做某事"

**关系流程**:
```
Event 触发 → Orchestrator 创建 Task → Agent 执行 → 发布 Event → 循环
```

### Audio Strategy 决策

| 模型能力 | 用户偏好 | 策略 |
|---------|---------|------|
| audio_integrated=true | keep_model_audio | MODEL_EMBEDDED |
| audio_integrated=true | replace_audio | EXTERNAL_FULL_REPLACE (警告) |
| audio_integrated=true | default | HYBRID_OVERLAY |
| audio_integrated=false | any | EXTERNAL_FULL |

### DNA Bank 管理

**多版本 Embedding**:
```json
{
  "C1_girl": {
    "embeddings": [
      {"version": 1, "weight": 0.2, "confidence": 0.88},
      {"version": 2, "weight": 0.5, "confidence": 0.94},
      {"version": 3, "weight": 0.3, "confidence": 0.91}
    ],
    "merge_strategy": "weighted_average"
  }
}
```

**合并策略**:
- weighted_average: 按置信度加权（默认）
- latest_priority: 最新优先
- confidence_threshold: 仅保留高置信度

### QA 动态阈值

根据质量档位和预算动态调整：

| 指标 | High | Balanced | Fast |
|------|------|----------|------|
| clip_similarity | 0.35 | 0.30 | 0.25 |
| face_identity | 0.80 | 0.75 | 0.70 |
| lip_sync | 0.85 | 0.80 | 0.75 |

**关键指标最低下限**:
- face_identity ≥ 0.70
- lip_sync ≥ 0.75

### 错误恢复策略

**Level 1 (90%)**: Agent 自动重试
- Prompt tuning
- 参数微调
- 指数退避

**Level 2 (9%)**: 模型切换/降级
- 切换备用模型
- 降低分辨率/质量
- 跳过非关键功能

**Level 3 (1%)**: 人工介入
- 手动修复 artifact
- 调整项目策略
- 增加预算
- 终止项目

### 用户审批检查点

**默认审批阶段**:
1. **剧本生成** (SCENE_WRITTEN): 用户审查剧本和分镜
2. **分镜规划** (SHOT_PLANNED): 用户确认镜头设计
3. **关键帧预览** (KEYFRAME_GENERATED): 用户查看关键帧图片
4. **预览视频** (PREVIEW_VIDEO_READY): 用户确认运动效果
5. **最终视频** (FINAL_VIDEO_READY): 用户最终确认

**用户决策选项**:
- **批准 (Approve)**: 继续执行下一阶段
- **修改 (Revise)**: 提供修改意见，Agent 重新生成
- **拒绝 (Reject)**: 完全重做该阶段

**模式切换**:
- **手动模式**: 在所有检查点暂停等待审批（默认）
- **自动模式**: 跳过所有审批，直接执行到完成
- **自定义模式**: 用户选择需要审批的检查点

---

## 数据模型

### Project（项目）
```typescript
interface Project {
  project_id: string;
  version: number;
  status: ProjectStatus;
  globalSpec: GlobalSpec;
  budget: Budget;
  dna_bank: Record<string, DNAEntry>;
  shots: Record<string, Shot>;
  tasks: Record<string, Task>;
  artifact_index: Record<string, ArtifactMetadata>;
  error_log: ErrorEntry[];
  change_log: ChangeLogEntry[];
}
```

### Shot（镜头）
```typescript
interface Shot {
  shot_id: string;
  status: ShotStatus;
  duration: number;
  script: {
    description: string;
    mood_tags: string[];
    voice_lines: VoiceLine[];
  };
  keyframes: {
    start?: string;
    mid?: string;
    end?: string;
  };
  preview_video?: string;
  final_video?: string;
  audio: {
    strategy: AudioStrategy;
    music?: string;
    voice?: string;
  };
  qa_results?: QAResults;
}
```

---

## 系统流程

### 完整项目生成流程

```
1. User 提交需求
2. RequirementParser 生成 GlobalSpec
3. ChefAgent 分配预算
4. ScriptWriter 编写剧本和分镜
5. 对每个 Shot:
   a. ShotDirector 规划镜头
   b. ImageGen 生成关键帧
   c. ArtDirector 提取特征，更新 DNA
   d. PromptEngineer 调整 prompt
   e. VideoGen 生成预览视频
   f. ConsistencyGuardian QA 检测
   g. 通过后生成最终视频
6. 并行生成音乐和配音
7. Editor 拼接视频，混合音频
8. 交付最终视频
```

### 三次微循环

**微循环 1: Script Visual Feasibility**
- ScriptWriter 生成 → ImageGen 预览 → ArtDirector 检测 → 通过/重写

**微循环 2: Shot Previsual / Motion Preview**
- ShotDirector 规划 → VideoGen 预览 → ConsistencyGuardian 检测 → 通过/调整

**微循环 3: Final Render + Audio Strategy**
- 选择模型 → 决定音频策略 → 最终渲染 → 跨模态 QA → 签字确认

---

## 技术选型

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| Blackboard | PostgreSQL JSONB + Redis | ACID 保证 + 灵活 schema |
| Event Bus | Kafka / Redis Streams | 高吞吐 + 持久化 |
| Storage | S3 兼容存储 | 成本低 + 可扩展 |
| Agent Runtime | Python / Node.js | 生态丰富 + AI 库支持 |
| Monitoring | Prometheus + Grafana | 开源 + 可定制 |

---

## MVP 规划

### Phase 1 (4 周): 核心基础设施
- Shared Blackboard
- Event Bus
- Orchestrator
- Storage Service
- ModelRouter

### Phase 2 (4 周): 核心 Agent
- RequirementParser
- ChefAgent
- ScriptWriter
- ShotDirector
- PromptEngineer

### Phase 3 (4 周): 生成 Agent
- ImageGen + SDXL Adapter
- VideoGen + Runway Adapter
- Audio Strategy
- MusicComposer + Tunee Adapter
- VoiceActor + MiniMax Adapter

### Phase 4 (3 周): QA 与一致性
- ArtDirector
- ConsistencyGuardian (视觉/音频/跨 Shot)
- 自动修复策略

### Phase 5 (2 周): Editor 与输出
- Editor Agent (拼接/混合/输出)

### Phase 6 (3 周): 用户审批与监控
- 用户审批机制
- Agent 审批处理能力
- 审批 UI
- 自动模式切换
- HumanGate Agent
- 成本控制
- 监控仪表板

**总计**: 20 周（约 5 个月）MVP 交付

---

## 关键指标

### 性能指标
- 单 shot 生成时间 < 5 分钟
- 30 秒视频完整生成 < 15 分钟
- Orchestrator 调度延迟 < 100ms
- Event Bus 吞吐量 > 1000 events/sec

### 质量指标
- 自动 QA 通过率 > 85%
- 人工介入率 < 5%
- Identity drift rate < 10%
- Lip sync score > 0.80

### 成本指标
- 30 秒视频成本 < $100 (balanced)
- 成本估算误差 < 20%
- 预算超支率 < 5%

---

## 附录

### 完整文档链接

- 需求文档: `.kiro/specs/unified-agent-system-design/requirements.md`
- 设计文档: `.kiro/specs/unified-agent-system-design/design.md`
- 任务列表: `.kiro/specs/unified-agent-system-design/tasks.md`

### 参考资料

- 原始设计文档 1: `-.md`
- 原始设计文档 2: `主题：LivingAgentPipeline_v1 工程规范文档.md`
- 原始设计文档 3: `多 Agent 系统设计方案.md`
- 原始设计文档 4: `工程级超细化版本 v3.5.md`

---

**文档结束**
