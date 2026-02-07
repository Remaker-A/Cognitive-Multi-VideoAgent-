# Implementation Plan

本实施计划将统一 Agent 系统设计分解为可执行的开发任务，按照 MVP 优先、渐进交付的原则组织。

## Phase 1: 核心基础设施（4 周）

- [ ] 1. 搭建 Shared Blackboard 基础设施
  - 实现 PostgreSQL JSONB 数据库 schema
  - 实现 Redis 缓存层
  - 实现版本控制和变更日志机制
  - 实现锁机制（global_style_lock, shot_locks）
  - 编写 Blackboard 读写 API
  - _Requirements: 1.1, 1.3, 4.5_
  - _Design: Architecture > 1. Shared Blackboard（共享黑板）_

- [x] 2. 搭建 Event Bus 基础设施



  - 选择并配置消息队列（Kafka/Redis Streams/RabbitMQ）
  - 实现事件发布/订阅机制
  - 实现事件持久化和重放功能
  - 实现 causation_id 链路追踪
  - 编写 Event Bus API
  - _Requirements: 1.3, 4.1, 4.2_
  - _Design: Architecture > 2. Event Bus（事件总线）_

- [ ] 3. 实现 Orchestrator 核心功能
  - 实现任务队列（优先级队列）
  - 实现事件到任务的映射逻辑
  - 实现任务调度器（依赖检查、锁获取）
  - 实现任务状态机管理
  - 实现预算检查机制
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 7.2_
  - _Design: Architecture > 3. Task vs Event 关系模型, Components > 13. Orchestrator（基础设施）_

- [ ] 4. 实现 Storage Service
  - 配置 S3 兼容存储
  - 实现 artifact 上传/下载 API
  - 实现 artifact 元数据管理
  - 实现 signed URL 生成
  - 实现缓存复用机制
  - _Requirements: 1.1_
  - _Design: Architecture > 1. Shared Blackboard（artifact_index 部分）_

- [ ] 5. 实现 ModelRouter 基础功能
  - 定义模型注册表 schema
  - 实现模型选择算法（基于质量档位和预算）
  - 实现成本估算功能
  - 实现模型能力查询 API
  - _Requirements: 7.1, 7.2, 7.4_
  - _Design: Components > 14. ModelRouter（基础设施）_

- [ ]* 5.1 编写基础设施单元测试
  - 测试 Blackboard 并发读写
  - 测试 Event Bus 消息顺序
  - 测试 Orchestrator 任务调度
  - 测试 ModelRouter 模型选择
  - _Requirements: 1.1, 1.3, 4.4_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 2: 核心 Agent 实现（4 周）

- [ ] 6. 实现 RequirementParser Agent
  - 实现用户输入解析逻辑
  - 实现 GlobalSpec 生成
  - 实现置信度计算
  - 实现 PROJECT_CREATED 事件发布
  - 集成到 Orchestrator
  - _Requirements: 1.1, 1.2_
  - _Design: Components > 2. RequirementParser Agent_

- [ ] 7. 实现 ChefAgent
  - 实现预算分配算法
  - 实现熔断决策逻辑
  - 实现成本预警机制
  - 实现 HumanGate 触发逻辑
  - 集成到 Orchestrator
  - _Requirements: 7.1, 7.2, 7.3, 10.5_
  - _Design: Components > 1. ChefAgent（总监 Agent）_

- [ ] 8. 实现 ScriptWriter Agent
  - 集成 LLM API（OpenAI/Claude）
  - 实现剧本生成逻辑
  - 实现 shot 分解算法
  - 实现情绪标注
  - 实现 SCENE_WRITTEN 事件发布
  - 实现重写机制（最多 3 次）
  - _Requirements: 1.1, 1.2_
  - _Design: Components > 3. ScriptWriter Agent（包含用户审批处理）_

- [ ] 9. 实现 ShotDirector Agent
  - 实现 shot 规划逻辑
  - 实现 camera language 定义
  - 实现 keyframe 请求生成
  - 实现 preview video 请求生成
  - 实现 SHOT_APPROVED 事件发布
  - _Requirements: 1.1, 1.2, 8.5_
  - _Design: Components > 4. ShotDirector Agent_

- [ ] 10. 实现 PromptEngineer Agent
  - 设计 prompt 模板库 schema
  - 实现模板加载和管理
  - 实现 prompt 组合逻辑
  - 实现 DNA token 注入
  - 实现 negative prompt 管理
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  - _Design: Components > 6. PromptEngineer Agent（包含模板库结构）_10. 实现 PromptEngineer Agent
  - 设计 prompt 模板库 schema
  - 实现模板加载和管理
  - 实现 prompt 组合逻辑
  - 实现 DNA token 注入
  - 实现 negative prompt 管理
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  - _Design: Components > 6. PromptEngineer Agent（包含模板库结构）_

- [ ]* 10.1 编写核心 Agent 单元测试
  - 测试 ScriptWriter shot 分解
  - 测试 ShotDirector 规划逻辑
  - 测试 PromptEngineer 模板替换
  - _Requirements: 1.1, 9.5_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 3: 生成 Agent 与 Adapter（4 周）

- [ ] 11. 实现 Adapter 基础接口
  - 定义 ImageModelAdapter 接口
  - 定义 VideoModelAdapter 接口
  - 定义 VoiceModelAdapter 接口
  - 定义 MusicModelAdapter 接口
  - 定义统一的输出 schema
  - _Requirements: 1.1, 1.2_
  - _Design: Components > 14. ModelRouter（Adapter 接口定义部分）_

- [ ] 12. 实现 ImageGen Agent + SDXL Adapter
  - 实现 SDXL API 调用
  - 实现 Adapter 标准化输出
  - 实现 embedding 提取
  - 实现 CLIP similarity 计算
  - 实现 IMAGE_GENERATED 事件发布
  - 实现失败重试机制
  - _Requirements: 1.1, 10.1, 10.2_
  - _Design: Components > 7. ImageGen Agent_

- [ ] 13. 实现 VideoGen Agent + Runway Adapter
  - 实现 Runway API 调用
  - 实现 Adapter 标准化输出
  - 实现 temporal coherence 计算
  - 实现 optical flow 分析
  - 实现 frame embeddings 提取
  - 实现 PREVIEW_VIDEO_READY 事件发布
  - _Requirements: 1.1, 2.1, 2.2, 10.1_
  - _Design: Components > 8. VideoGen Agent_

- [ ] 14. 实现 Audio Strategy 决策逻辑
  - 实现 audio_integrated 检测
  - 实现用户偏好解析
  - 实现策略决策函数
  - 实现风险警告生成
  - 集成到 VideoGen Agent
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  - _Design: Components > 8. VideoGen Agent（Audio Strategy 决策表）_

- [ ] 15. 实现 MusicComposer Agent + Tunee Adapter
  - 实现 Tunee API 调用
  - 实现 mood embedding 生成
  - 实现 markers 标注
  - 实现 stems 分离
  - 实现 MUSIC_COMPOSED 事件发布
  - _Requirements: 2.1, 2.4_
  - _Design: Components > 9. MusicComposer Agent_

- [ ] 16. 实现 VoiceActor Agent + MiniMax Adapter
  - 实现 MiniMax TTS API 调用
  - 实现 phoneme 时间对齐
  - 实现 voice embedding 提取
  - 实现 WER 计算
  - 实现 consent 验证机制
  - 实现 VOICE_RENDERED 事件发布
  - _Requirements: 2.1, 2.4_
  - _Design: Components > 10. VoiceActor Agent_

- [ ]* 16.1 编写生成 Agent 单元测试
  - 测试 ImageGen Adapter 输出格式
  - 测试 VideoGen Audio Strategy 决策
  - 测试 MusicComposer markers 生成
  - 测试 VoiceActor phoneme 对齐
  - _Requirements: 2.5, 10.1_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 4: QA 与一致性管理（4 周）

- [ ] 17. 实现 ArtDirector Agent
  - 实现特征提取（face, palette, texture）
  - 实现 DNA Bank 更新逻辑
  - 实现多版本 embedding 管理
  - 实现加权合并算法
  - 实现置信度计算
  - 实现 DNA_BANK_UPDATED 事件发布
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - _Design: Components > 5. ArtDirector Agent（包含 DNA 合并策略）_

- [ ] 18. 实现 ConsistencyGuardian Agent - 视觉检测
  - 实现 CLIP similarity 检测
  - 实现 face identity 检测
  - 实现 palette consistency 检测
  - 实现 optical flow smoothness 检测
  - 实现动态阈值调整逻辑
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_
  - _Design: Components > 12. ConsistencyGuardian Agent（run_qa_checks, get_dynamic_thresholds）_

- [ ] 19. 实现 ConsistencyGuardian Agent - 跨 Shot 连贯性
  - 实现相邻 shot 视觉相似度检测
  - 实现光照突变检测
  - 实现颜色跳变检测
  - 实现位置跳变检测
  - 实现连贯性评分算法
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  - _Design: Components > 12. ConsistencyGuardian Agent（check_shot_continuity）_

- [ ] 20. 实现 ConsistencyGuardian Agent - 音频检测
  - 实现 lip sync 检测
  - 实现 WER 检测
  - 实现 music mood match 检测
  - 实现 QA_REPORT 事件发布
  - 实现 CONSISTENCY_FAILED 事件发布
  - _Requirements: 5.1, 5.2, 5.3, 5.4_
  - _Design: Components > 12. ConsistencyGuardian Agent（音频检测部分）_

- [ ] 21. 实现自动修复策略
  - 实现 Level 1 prompt tuning 逻辑
  - 实现 Level 2 模型切换逻辑
  - 实现 Level 2 质量降级逻辑
  - 实现 Level 3 HumanGate 触发
  - 实现 AUTO_FIX_REQUEST 事件发布
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_
  - _Design: Components > 12. ConsistencyGuardian Agent（auto_fix）, Error Handling > 三层错误恢复策略_

- [ ] 22. 实现 ErrorCorrectionAgent - 错误检测
  - 实现人物姿态检测（OpenPose 集成）
  - 实现手部质量检测（手指数量、形态）
  - 实现面部质量检测（五官、表情）
  - 实现物理规律违背检测
  - 实现文字错误检测
  - 实现错误严重程度分级
  - _Requirements: 13.1, 13.2, 13.3_
  - _Design: Components > 13. ErrorCorrectionAgent（detect_errors）_

- [ ] 23. 实现 ErrorCorrectionAgent - 智能修复
  - 实现 Level 1 局部 inpainting 修复
  - 实现 Level 2 ControlNet 控制重生成
  - 实现 Level 3 完全重新生成
  - 实现 Level 4 人工介入触发
  - 实现修复效果验证
  - 实现修复策略选择逻辑
  - _Requirements: 13.4, 13.5, 13.6, 13.7_
  - _Design: Components > 13. ErrorCorrectionAgent（correct_error）_

- [ ] 24. 实现用户错误标注功能
  - 实现错误标注 UI（圈选区域）
  - 实现错误类型选择界面
  - 实现错误描述输入
  - 实现标注数据模型（ErrorAnnotation）
  - 集成到用户审批流程
  - _Requirements: 13.4, 13.8, 13.9_
  - _Design: Components > 13. ErrorCorrectionAgent（handle_user_error_report）_

- [ ]* 24.1 编写 ErrorCorrection Agent 单元测试
  - 测试姿态检测准确率
  - 测试手部检测准确率
  - 测试修复策略选择
  - 测试修复效果验证
  - _Requirements: 13.1, 13.2, 13.10_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

- [ ]* 24.2 编写 QA Agent 单元测试
  - 测试动态阈值调整
  - 测试跨 Shot 连贯性检测
  - 测试自动修复策略选择
  - _Requirements: 5.5, 8.5, 10.5_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 5: 图像编辑与优化（3 周）

- [ ] 25. 实现 ImageEditAgent 基础功能
  - 定义 ImageEditAgent 接口
  - 实现编辑请求处理逻辑
  - 实现编辑质量评估
  - 实现编辑历史管理
  - 实现 IMAGE_EDITED 事件发布
  - _Requirements: 12.1, 12.6, 12.7, 12.9_
  - _Design: Components > 12. ImageEditAgent_

- [ ] 26. 集成图像编辑模型 Adapter
  - 实现 QwenImageEditAdapter（视角调整）
  - 实现 ControlNetInpaintAdapter（局部修复）
  - 实现 InstructPix2PixAdapter（通用编辑）
  - 实现 Adapter 选择逻辑
  - 实现编辑参数优化
  - _Requirements: 12.2, 12.3, 12.10_
  - _Design: Components > 12. ImageEditAgent（select_adapter）_

- [ ] 27. 实现编辑功能集成
  - 在用户审批界面添加"编辑"按钮
  - 实现编辑指令输入界面
  - 实现编辑预览功能
  - 实现编辑撤销功能
  - 集成到 Orchestrator 审批流程
  - _Requirements: 12.4, 12.5, 12.7_
  - _Design: Components > 12. ImageEditAgent, Components > 13. Orchestrator（审批流程）_

- [ ] 28. 实现 DNA 一致性保持
  - 实现编辑时的 DNA token 注入
  - 实现编辑后的特征验证
  - 实现身份一致性检测
  - 实现不一致时的自动调整
  - _Requirements: 12.5, 12.8_
  - _Design: Components > 12. ImageEditAgent（preserve_identity）, Components > 5. ArtDirector Agent_

- [ ]* 28.1 编写 ImageEdit Agent 单元测试
  - 测试编辑指令解析
  - 测试 Adapter 选择逻辑
  - 测试编辑质量评估
  - 测试 DNA 一致性保持
  - _Requirements: 12.8, 12.10_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 6: Editor 与最终输出（2 周）

- [ ] 29. 实现 Editor Agent - 视频拼接
  - 实现多 shot 按序拼接
  - 实现转场效果（crossfade）
  - 实现时间轴管理
  - _Requirements: 6.1, 6.2_
  - _Design: Components > 11. Editor Agent（assemble_final_video）_

- [ ] 30. 实现 Editor Agent - 音频混合
  - 实现音频轨道混合
  - 实现 audio ducking
  - 实现淡入淡出效果
  - 实现基于 markers 的节拍对齐
  - 实现基于 phoneme timestamps 的口型同步
  - _Requirements: 2.4, 6.2, 6.3, 6.4_
  - _Design: Components > 11. Editor Agent（mix_audio, sync_audio_to_video）_

- [ ] 31. 实现 Editor Agent - 最终输出
  - 实现视频编码和导出
  - 实现元数据生成
  - 实现 PROJECT_FINALIZED 事件发布
  - _Requirements: 6.5_
  - _Design: Components > 11. Editor Agent（assemble_final_video 返回值）_

- [ ]* 31.1 编写 Editor Agent 单元测试
  - 测试 shot 拼接顺序
  - 测试音频混合质量
  - 测试 markers 对齐
  - _Requirements: 6.2, 6.3, 6.4_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 7: 用户审批与监控（3 周）

- [ ] 32. 实现用户审批机制
  - 实现 ApprovalRequest 数据模型
  - 实现审批检查点配置
  - 实现 Orchestrator 审批流程控制
  - 实现项目暂停/恢复机制
  - 实现审批超时提醒
  - _Requirements: 11.1, 11.2, 11.3, 11.6, 11.9_
  - _Design: Data Models > ApprovalRequest（审批请求）, Components > 13. Orchestrator（check_approval_required, request_user_approval, handle_user_decision）_

- [ ] 33. 实现 Agent 审批处理能力
  - 为 ScriptWriter 添加修改处理
  - 为 ShotDirector 添加修改处理
  - 为 ImageGen 添加重新生成能力
  - 为 VideoGen 添加重新生成能力
  - 实现修改意见解析和应用
  - _Requirements: 11.4, 11.5, 11.6_
  - _Design: Components > 3. ScriptWriter Agent（handle_user_revision）_

- [ ] 34. 实现审批 UI
  - 实现审批请求通知
  - 实现内容预览界面（剧本/图片/视频）
  - 实现审批决策按钮（批准/修改/拒绝）
  - 实现修改意见输入框
  - 实现审批历史查看
  - _Requirements: 11.3, 11.4, 11.10_
  - _Design: Data Models > ApprovalRequest（审批请求）, Architecture > 2. Event Bus（USER_APPROVAL_REQUIRED 等事件）_

- [ ] 35. 实现自动模式切换
  - 实现自动模式配置
  - 实现审批检查点自定义
  - 实现模式切换 UI
  - 实现模式状态持久化
  - _Requirements: 11.7, 11.8_
  - _Design: Data Models > Project 扩展（user_options.auto_mode, approval_checkpoints）_

- [ ]* 35.1 编写审批机制单元测试
  - 测试审批流程控制
  - 测试修改意见处理
  - 测试超时提醒
  - _Requirements: 11.6, 11.9_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

- [ ] 36. 实现 HumanGate Agent
  - 实现人工审核任务队列
  - 实现任务优先级排序
  - 实现人工决策接口
  - 实现手动 artifact 上传
  - 实现 HUMAN_DECISION 事件发布
  - _Requirements: 10.5_
  - _Design: Error Handling > Level 3: 人工介入_

- [ ] 37. 实现成本控制与预测
  - 实现实时成本追踪
  - 实现成本预测算法
  - 实现预算预警机制
  - 实现成本优化建议生成
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - _Design: Components > 1. ChefAgent（allocate_budget, adjust_strategy）, Architecture > 1. Shared Blackboard（budget 字段）_

- [ ] 38. 实现监控与可观测性
  - 实现 KPI 指标收集
  - 实现链路追踪（基于 causation_id）
  - 实现错误日志聚合
  - 实现性能监控（延迟、吞吐量）
  - 实现成本监控仪表板
  - _Requirements: 7.5, 10.4_
  - _Design: Architecture > 2. Event Bus（causation_id 链路追踪）, Error Handling > 错误日志与追溯_

- [ ]* 38.1 编写监控单元测试
  - 测试 KPI 计算准确性
  - 测试链路追踪完整性
  - 测试成本追踪准确性
  - _Requirements: 7.5_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 8: 集成测试与优化（3 周）

- [ ] 39. 端到端集成测试
  - 编写完整项目生成测试（30秒视频）
  - 编写用户审批流程测试
  - 编写图像编辑流程测试
  - 编写错误检测和修复测试
  - 编写错误恢复流程测试
  - 编写预算控制测试
  - 编写跨 Shot 连贯性测试
  - 编写 Audio Strategy 测试
  - _Requirements: 1.1, 2.5, 7.5, 8.5, 10.5, 11.10, 12.6, 13.6_
  - _Design: Testing Strategy > 2. 集成测试（Integration Tests）, 3. 端到端测试（E2E Tests）_

- [ ] 40. 性能优化
  - 优化 Orchestrator 任务调度延迟
  - 优化 Blackboard 读写性能
  - 优化 Event Bus 吞吐量
  - 优化 DNA Bank 查询性能
  - 实现 Redis 缓存策略
  - _Requirements: 1.1, 1.3, 3.5_
  - _Design: Testing Strategy > 4. 性能测试（Performance Tests）_

- [ ] 41. 成本优化
  - 优化模型选择策略
  - 实现 artifact 缓存复用
  - 优化 QA 检测频率
  - 实现批量任务处理
  - 优化图像编辑成本
  - _Requirements: 7.4, 7.5, 12.9_
  - _Design: Testing Strategy > 5. 成本测试（Cost Tests）, Components > 14. ModelRouter（select_model）_

- [ ]* 41.1 编写性能测试
  - 测试单 shot 生成时间
  - 测试完整项目生成时间
  - 测试 Orchestrator 调度延迟
  - 测试 Event Bus 吞吐量
  - 测试图像编辑延迟
  - 测试错误检测延迟
  - _Requirements: 1.1, 1.3, 12.8, 13.2_
  - _Design: Testing Strategy > 4. 性能测试（Performance Tests）_

## Phase 9: 高级 Adapter 与模型集成（2 周）

- [ ] 42. 实现 Sora2 Adapter（高质量视频）
  - 实现 Sora2 API 调用
  - 实现 audio_integrated 标记
  - 实现 audio_info 提取
  - 集成到 VideoGen Agent
  - _Requirements: 2.1, 2.2_
  - _Design: Components > 8. VideoGen Agent（determine_audio_strategy）, Components > 14. ModelRouter（模型注册表示例）_

- [ ] 43. 实现 Veo3.1 Adapter（高质量视频）
  - 实现 Veo3.1 API 调用
  - 实现 audio_integrated 标记
  - 集成到 VideoGen Agent
  - _Requirements: 2.1, 2.2_
  - _Design: Components > 8. VideoGen Agent（determine_audio_strategy）, Components > 14. ModelRouter（模型注册表示例）_

- [ ] 44. 实现 Midjourney Adapter（高质量图像）
  - 实现 Midjourney API 调用
  - 实现 Adapter 标准化输出
  - 集成到 ImageGen Agent
  - _Requirements: 1.1_
  - _Design: Components > 7. ImageGen Agent（adapters 字典）_

- [ ]* 44.1 编写高级 Adapter 测试
  - 测试 Sora2 audio_integrated 检测
  - 测试 Veo3.1 audio_info 提取
  - 测试 Midjourney 输出格式
  - _Requirements: 2.1, 2.2_
  - _Design: Testing Strategy > 1. 单元测试（Unit Tests）_

## Phase 10: UI 与用户体验（3 周）

- [ ] 45. 实现项目创建 UI
  - 实现需求输入表单
  - 实现参考文件上传
  - 实现质量档位选择
  - 实现预算设置
  - 实现审批模式选择（自动/手动）
  - 实现审批检查点自定义
  - _Requirements: 1.1, 11.7, 11.8_
  - _Design: Components > 2. RequirementParser Agent, Data Models > GlobalSpec（全局规格）_

- [ ] 46. 实现项目监控 UI
  - 实现实时进度展示
  - 实现 shot 状态可视化
  - 实现成本追踪展示
  - 实现错误日志查看
  - 实现审批状态展示
  - 实现错误检测结果展示
  - _Requirements: 7.5, 11.10, 13.9_
  - _Design: Architecture > 1. Shared Blackboard（status, budget, error_log）, Data Models > ApprovalRequest_

- [ ] 47. 实现 HumanGate UI
  - 实现人工审核任务列表
  - 实现 artifact 预览
  - 实现决策按钮（修复/调整/接受/终止）
  - 实现手动 artifact 上传
  - _Requirements: 10.5_
  - _Design: Error Handling > Level 3: 人工介入（人工决策选项）_

- [ ] 48. 实现预览与交付 UI
  - 实现 keyframe 预览
  - 实现 preview video 播放
  - 实现最终视频播放
  - 实现下载功能
  - _Requirements: 1.1_
  - _Design: Data Models > Shot（镜头）, Components > 11. Editor Agent（最终输出）_

- [ ]* 48.1 编写 UI 集成测试
  - 测试项目创建流程
  - 测试实时进度更新
  - 测试审批流程交互
  - 测试图像编辑交互
  - 测试错误标注交互
  - 测试 HumanGate 交互
  - _Requirements: 1.1, 10.5, 11.10, 12.4, 13.4_
  - _Design: Testing Strategy > 2. 集成测试（Integration Tests）_

## Phase 11: 文档与部署（2 周）

- [ ] 49. 编写技术文档
  - 编写系统架构文档
  - 编写 API 文档
  - 编写 Agent 开发指南
  - 编写 Adapter 开发指南
  - 编写图像编辑功能文档
  - 编写错误检测和修复文档
  - 编写运维手册
  - _Requirements: 1.1, 1.2, 12.1, 13.1_
  - _Design: Overview（核心设计原则）, Architecture（系统分层架构）, Components（所有 Agent 详细设计）_

- [ ] 50. 编写用户文档
  - 编写用户使用指南
  - 编写质量档位说明
  - 编写 Audio Strategy 说明
  - 编写审批模式使用指南
  - 编写图像编辑使用指南
  - 编写错误标注使用指南
  - 编写成本估算说明
  - 编写常见问题解答
  - _Requirements: 1.1, 2.5, 7.5, 11.7, 12.4, 13.4_
  - _Design: Components > 8. VideoGen Agent（Audio Strategy 决策表）, Components > 1. ChefAgent（allocate_budget）, Components > 12. ImageEditAgent, Components > 13. ErrorCorrectionAgent_

- [ ] 51. 部署与上线
  - 配置生产环境（PostgreSQL, Redis, Kafka, S3）
  - 部署所有 Agent 服务（包含 ImageEditAgent 和 ErrorCorrectionAgent）
  - 配置监控和告警
  - 执行压力测试
  - 执行灰度发布
  - _Requirements: 1.1_
  - _Design: Architecture > 1. Shared Blackboard（技术选型）, Architecture > 2. Event Bus（技术选型）_

- [ ]* 51.1 编写部署文档
  - 编写环境配置指南
  - 编写服务部署指南
  - 编写监控配置指南
  - 编写故障排查指南
  - 编写图像编辑模型部署指南
  - 编写错误检测模型部署指南
  - _Requirements: 1.1, 12.10, 13.1_
  - _Design: Architecture（所有基础设施组件）, Error Handling（错误日志与追溯）_

---

**任务总数**: 51 个主任务（含可选测试任务）  
**预计工期**: 32 周（约 7.5 个月）  
**更新内容**: 
- Phase 4 增加了 ErrorCorrectionAgent（4 个任务）
- Phase 5 新增图像编辑功能（4 个任务）
- 总工期从 28 周增加到 32 周

**新增 Agent**:
- ImageEditAgent: 图像编辑和视角调整
- ErrorCorrectionAgent: 错误检测和智能修复

**设计文档引用说明**:
- 每个任务现在都包含 `_Design:` 行，指向 design.md 中的具体章节
- 引用格式：`章节名 > 子章节名（具体内容）`
- 开发人员可以直接查找对应章节获取详细的实现指导和代码示例
