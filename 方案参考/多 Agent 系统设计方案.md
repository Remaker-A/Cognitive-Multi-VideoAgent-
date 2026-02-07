# 多 Agent 系统设计方案

## 一、核心设计理念 (要点)



* 把模型能力内化为 Agent 的 “感官 / 执行器”，通过 Model-Agent 封装并注册到 Orchestrator。

* 采用事件驱动 + Shared Blackboard 作为信息单一来源，保障 Agent 间数据一致性。

* 遵循 Plan-first Style & DNA 流程，实现多轮感知、自动 / 人工兜底机制。

* 由 2-3 个 Orchestrator 负责能力匹配与成本决策。

* 强化多模态一致性（视觉、音频、语义）检测与自动修复管线，必要时降级并交由 Chief/Chef Agent 处理。

## 二、Agent 架构体系

采用 5+2+Chef+Infrastructure 的架构模式，具体包含 12 类 Agent：

### 核心 5 类 Agent



1. **ChefAgent/ChiefAgent**

* 职责：项目总指挥，负责全局策略、预算控制、最终人工决策入口、风险通报及熔断决策。

* 关联 KPIs：预算执行率、风险响应时效、人工决策占比

1. **ScriptWriter Agent**

* 职责：生成文字剧情、时间轴及情绪标注，输出 Script.json（包含 shot 分解 + 时间戳）。

* KPIs：分镜一致性率

1. **ShotDirector Agent**

* 职责：负责 shot-level 设计、camera language 定义、运镜预演控制，输出 shot.json（包含 camera、duration、visual\_hook）。

* KPIs：preview video pass 率

1. **ArtDirector Agent**

* 职责：管理 DNA 库、提取视觉特征及调整 prompt 权重，实现 DNA bank 更新与 prompt weight adjustments。

* KPIs：identity 漂移率、色彩漂移率

1. **ConsistencyGuardian Agent/Gatekeeper**

* 职责：全链路自动化 QA 检测（视觉 / 音频 / 语义），输出 QA report（包含 scores & recommendations）。

* KPIs：自动化 QA 通过率、问题修复时效

### 两个 Model 执行 Agent



1. **ImageGenAgent**

* 职责：通过 image API 控制 net/pose/depth，输出 keyframes、control maps、embeddings、metadata。

* KPIs：avg latency、cost\_per\_image、CLIP 相似度分布

1. **VideoGenAgent**

* 职责：通过 video API 实现 keyframe→video、frames→video 转换，输出 shot clip、optical flow maps、per-frame embeddings、metadata。

* KPIs：render success rate、avg render time、temporal coherence score

### 新增媒体 Agent



1. **Music-Composer Agent**

* 职责：生成曲目、stems、bpm 及 markers，输出 track.wav/stems/markers/music\_embedding（MIDI-like 格式）。

* KPIs：mood\_match\_score、music\_embedding 相似度、iterations\_to\_accept

1. **Voice-Actor Agent/TTS/voice-clone**

* 职责：实现文字转语音及声音克隆，输出 voice.wav、timestamps（word/phoneme）、voice\_token、voice\_embedding。

* KPIs：lip\_sync\_accuracy\_estimate、voice\_identity\_score

### 基础设施 Agent



1. **Orchestrator**

* 职责：负责事件总线管理、模型选择、任务队列调度、重试策略执行及权限 / 配额管理。

1. **Storage & Artifacts Service**

* 职责：处理 artifact 存储、版本化管理、seed+model\_version 记录及缓存复用库维护。

1. **HumanGate Agent**

* 职责：集成人工审批面板与修复工具，提供人工干预入口。

## 三、Shared Blackboard 结构与规范

Shared Blackboard 作为所有 Agent 的数据交互中心，采用 PostgreSQL JSONB/MongoDB+Redis 缓存 + S3 存储 artifacts 的架构。

### 示例 JSON



```
{

"project\_id":"PROJ-20251115-001",

"status":"SHOT\_PLANNING",

"globalSpec":{

"title":"RainAndWarmth",

"duration":30,

"aspect":"9:16",

"style":{"tone":"warm","palette":\["#2b3a67","#cfa66b"]},

"character\_ids":\["C1"]

},

"budget":{"total":100,"used":23.5,"remaining":76.5},

"dna\_bank":{"C1":{"embedding":"...","conf":0.92,"version":3}},

"shots":{

"S01":{"status":"PENDING","dependencies":\[],"start\_img":"s3://...","end\_img":null}

},

"artifact\_index":{ "s3://.../S01\_start.png":{"seed":1234,"model":"sdxl-1.0","uses":2}},

"error\_log":\[],

"locks":{}

}
```

### 白板规则 (简要)



* Agent 仅可读取全局 spec，仅能写入自身负责的 shots 节点（如 shots.S01）。

* 跨 Agent 操作 globalStyle、dna\_bank 时，需通过 Orchestrator 获取 GlobalStyle 锁。

## 四、Event Bus 规范

采用 Kafka/Redis Streams/RabbitMQ 作为事件总线，消息包含 project\_id、actor、payload、causation\_id 字段。

### 关键事件样例



* SCENE\_WRITTEN：ScriptWriter → ShotDirector

* KEYFRAME\_REQUESTED：ShotDirector → ImageGenAgent

* IMAGE\_GENERATED：ImageGenAgent → EventBus

* PREVIEW\_VIDEO\_READY：VideoGenAgent → 相关 Agent

* QA\_REPORT：ConsistencyGuardian → 相关 Agent

* CONSISTENCY\_FAILED：ConsistencyGuardian → ChefAgent/HumanGate

* MUSIC\_COMPOSED：Music-Composer Agent → EventBus

* VOICE\_RENDERED：Voice-Actor Agent → EventBus

* SHOT\_APPROVED：ShotDirector/ShotLeader → EventBus

### 事件处理原则



* Agent 不直接调用另一个 Agent，通过事件总线异步通信。

* 使用 causation\_id 实现全链路可追溯。

* 每个事件需同步写入 Shared Blackboard，包含 pointer/artifact id。

## 五、标准微循环流程

将三次微循环模型化为标准流程，各循环均设自动化判定阈值与修复策略：

### 微循环 A：Script Visual Feasibility



1. ScriptWriter 编写 scene 并发布 SCENE\_WRITTEN 事件。

2. ShotDirector 触发 KEYFRAME\_REQUESTED 事件至 ImageGenAgent。

3. ImageGenAgent 返回 keyframe artifact 并发布 IMAGE\_GENERATED 事件。

4. ArtDirector 提取 real\_features 更新 DNA，ConsistencyGuardian 执行快速 CLIP similarity 检测。

5. 若 visual\_score < T\_script（CLIP score < 0.28），则 ScriptWriter 自动重写或触发 REWRITE\_SCENE 事件，ChefAgent 记录重写次数与成本影响。

### 微循环 B：Shot Pre-visual / Motion Preview



1. ShotDirector 基于 keyframe 发布 PREVIEW\_VIDEO\_REQUEST 事件，指定 256px 分辨率至 VideoGenAgent。

2. VideoGenAgent 返回 PREVIEW\_VIDEO\_READY 事件及 motion metrics（含 optical flow smoothness）。

3. ShotDirector/ConsistencyGuardian 验证 motion\_score ≥ T\_motion（flow smoothness > 0.85）。

4. 若不达标，自动切换为 static shot/slower dolly，或标记为 high-risk 并通知 ChefAgent。

### 微循环 C：ArtDirector DNA 更新



1. ArtDirector 接收 IMAGE\_GENERATED 事件后，提取 face、palette、texture 等特征。

2. 按旧特征 0.7、新特征 0.3 的权重合并更新 DNA 库，写入 Shared Blackboard。

3. PromptEngineer 根据 DNA 更新 prompt weights，通过 PROMPT\_UPDATE 事件驱动下一轮生成。

4. 注意：为避免漂移，合并时记录 confidence 与版本，若 conf < 0.6 则需 manual confirmation。

## 六、QA 标准与自动修复策略

### QA 检测标准

#### 视觉维度



* CLIP similarity to global\_ref：pass = ≥0.30，warn = 0.28-0.29

* Face identity consistency（cosine sim）：pass ≥ 0.75，warn = 0.7-0.74

* Palette histogram distance（Earth Mover’s Distance）：pass ≤0.12

* Optical flow smoothness：pass ≥0.85

* Frame-to-frame embedding drift：pass ≤0.2

#### 音频维度



* Music mood match（music\_embedding vs target\_mood）：pass ≥0.7

* Voice-to-text semantic match（ASR of generated voice vs script）：WER ≤ 0.12

* Lip-sync estimate（phoneme timestamps vs frame timestamps）：pass ≥0.8

### 自动修复策略 (按优先级)



1. Prompt Tuning & Re-generate（低成本）：PromptEngineer 调整权重 / 加强 DNA token / 增加 negative prompt，ImageGenAgent/VideoGenAgent 重试 N1=2 次。

2. Model Swap / Quality-Up：切换更高质量模型，重试 N2=1 次。

3. Degrade UX：将 shot 改为 image→subtle motion→crossfade slideshow，以尽快交付预览。

4. HumanGate / ChefAgent：当自动流程无法修复或成本骤增时触发，记录决策与费用影响。

## 七、熔断策略



* Level 1（90%）：Agent prompt 重试、参数 tweak。

* Level 2（9%）：ArtDirector 更新 DNA + ScriptWriter 简化描述 + 重新生成。

* Level 3（1%）：ChefAgent 执行策略变更或人工录音 / 干预。

## 八、音乐与配音 Agent 深度融合

### Music-Composer Agent



* 输入：globalSpec 中的 mood、tempo\_hint、instruments，shots 中的 markers（可选）。

* 输出：track.wav（full mix）、stems（piano、strings、percussion）、music\_metadata（bpm、key、markers、music\_embedding）。

* 协作：在 shot planning 阶段提供 cue\_points，render 前提供 stem 供 Editor 做 ducking/mixing；通过 midi\_like Editor 做 beat-snap。

* QA：music\_embedding 与 global\_mood\_embedding 相似度 < 0.7 则重作。

### Voice-Actor Agent



* 输入：带时间窗口的 script dialogue lines、voice\_token（角色声音）、voice reference samples。

* 输出：voice.wav、timestamps（word/phoneme）、voice\_embedding（用于 identity match）。

* 协作：生成语音后由 ConsistencyGuardian 进行 lip-sync check，通过 phoneme timestamps 对齐 frames；voice-clone 需有 consent 流程和 UI（符合 legal & privacy 要求）。

* 异常处理：若偏差 > threshold，调整 voice tempo/stretch，仍不达标则请求人工录音。

### 同步策略 (关键)



* 所有时间戳采用统一 timebase，Editor 使用 markers 对齐 audio & video。

* Music 提供 markers（strong beats），Editor 可在这些点裁切转场或触发视觉特效。

* Voice 提供 phoneme timestamps，用于 lip-sync timestretch。

## 九、模型精选策略 (用户可见与后台)



* 用户界面仅暴露 2-3 类模型选项：

1. Cinematic (High)：Veo 3.1 / Sora2（高质量）

2. Balanced：Sora2 Balanced（性价比 / 稳定性折中）

3. Fast & Cheap：1.x（快速预览 / 低成本）

* 后台 Orchestrator 可基于 shot 类型（如 close-up）强制启用 high package，UI 中显示成本差异与建议。

## 十、版本化、可复现性与审计



* 每个生成的 artifact 记录 model\_version、prompt、seed、controlmaps、time、cost。

* 提供 “回放” 功能（基于 seed + model\_version），模型升级时提供不可重现告警。

* 每次修改 globalStyle 或 dna\_bank 均记录 version 与 author，支持 undo 操作。

## 十一、核心 KPIs 指标

按 agent/pipeline 维度统计：



* 成本类：avg\_cost\_per\_project、cost\_per\_second

* 时效类：avg\_time\_user\_input→preview、avg\_render\_time\_per\_shot

* 质量类：auto\_pass\_rate（ConsistencyGuardian）、human\_intervention\_rate、identity\_drift\_rate

* 系统类：model\_error\_rate、retry\_rate、cache\_hit\_rate

* 体验类：UX first\_time\_accept\_rate

## 十二、示例事件流 (从用户需求到成片)



1. User 提交 requirement→Requirement Parser 写入 GlobalSpec 到 Blackboard→发布 PROJECT\_CREATED 事件。

2. ChefAgent 分配预算 & 配置文件→Planner Agent 生成 shot list→发布 SCENE\_WRITTEN 事件。

3. ScriptWriter 编写 shots→ShotDirector 发布 KEYFRAME\_REQUESTED→ImageGenAgent 返回低成本 keyframes→发布 IMAGE\_GENERATED 事件。

4. ArtDirector 提取特征→更新 DNA→PromptEngineer 调整 prompt weights→发布 PROMPT\_UPDATED 事件。

5. ShotDirector 发布 PREVIEW\_VIDEO\_REQUEST→VideoGenAgent 返回低分辨率预览→ConsistencyGuardian 执行 QA→通过则 ShotDirector 标记 shot 为 APPROVED，失败则重跑或调整。

6. Music-Composer 创作曲目（返回 markers）→Voice-Actor 合成语音→分别发布 MUSIC\_COMPOSED/VOICE\_RENDERED 事件。

7. 所有 shots 批准后→VideoGenAgent 生成高质量最终 shots→ConsistencyGuardian 最终 QA→Editor 合成最终视频 + 混音→交付 artifact。

8. ChefAgent 向用户提交最终成本 & 总结；若存在致命错误，HumanGate 创建工单。

## 十三、开发与 MVP 规划

### 短期 MVP（4-6 周）



1. 实现 Shared Blackboard + Event Bus + Orchestrator 基本骨架。

2. 完成 ScriptWriter→ShotDirector→ImageGenAgent→ArtDirector DNA 提取→ConsistencyGuardian CLIP 检测链路，实现 keyframe preview。

3. 集成 Music-Composer 简单 TTS / 循环音、Voice-Actor TTS 基础功能，实现基本同步。

4. 开发 UI，支持 shot 的 keyframe\&preview 展示及人工审批按钮。

### 后续迭代



1. 接入高质量 VideoGenAgent（Sora2/Veo）、Editor、stems、voice cloning、自动修复功能。

2. 实现完整 QA 自动化与熔断机制、DNA bank 版本化、成本控制策略。

## 十四、交付物 (可直接生成)



1. Agent Manifest JSON：包含 Agent 的 capability manifest + 示例 HTTP/RPC 接口定义。

2. Shared Blackboard Schema + Event Catalog：包含 JSON schema 及 payloads 定义。

3. 示例 Project RunDemo：30s 生成完整的 GlobalSpec、Plan、3 个 shot 的 shot.json、每个 shot 的 prompt、示例 music request 与 voice request。

要不要我帮你生成一份**完整的 markdown 文件**，包含上述所有结构化内容，可直接交付给工程团队使用？

> （注：文档部分内容可能由 AI 生成）