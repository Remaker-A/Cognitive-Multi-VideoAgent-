# Requirements Document

## Introduction

本需求文档旨在整合现有的四份 Agent 系统设计文档，创建一份统一、优化、工程可落地的 LivingAgentPipeline 系统设计规范。该系统是一个基于事件驱动架构的多 Agent AI 视频生成平台，支持从用户需求到最终视频交付的全流程自动化。

## Glossary

- **Agent**: 具有特定职责和能力的自治软件组件，通过事件总线进行协作
- **Shared Blackboard**: 所有 Agent 共享的中央数据存储，作为单一事实来源
- **Event Bus**: 事件驱动的消息总线，用于 Agent 间异步通信
- **ModelRouter**: 模型路由器，负责根据需求选择和调度不同的 AI 模型
- **Adapter**: 适配器层，封装不同 AI 模型的 API 调用，提供统一接口
- **DNA Bank**: 视觉特征库，存储角色、场景的视觉一致性特征
- **Shot**: 镜头，视频的基本组成单元
- **Orchestrator**: 编排器，负责任务调度、资源分配和流程控制
- **ChefAgent**: 总监 Agent，负责项目级决策和质量把控
- **ConsistencyGuardian**: 一致性守护者，负责质量检测和自动修复

## Requirements

### Requirement 1: 文档统一与架构清晰

**User Story:** 作为系统架构师，我希望有一份统一的设计文档，以便团队成员能够清晰理解系统架构和各组件职责。

#### Acceptance Criteria

1. WHEN 团队成员查阅设计文档时，THE System SHALL 提供单一、权威的架构设计文档
2. THE System SHALL 明确定义 12 个核心 Agent 的职责边界，避免功能重叠
3. THE System SHALL 清晰区分事件（Event）和任务（Task）的概念及其关系
4. THE System SHALL 提供完整的数据流图，展示从用户输入到视频输出的全流程
5. WHERE 存在多个设计版本时，THE System SHALL 标注版本号和适用场景

### Requirement 2: Audio Strategy 简化与优化

**User Story:** 作为开发工程师，我希望 Audio Strategy 的决策逻辑清晰简单，以便快速实现和维护。

#### Acceptance Criteria

1. THE System SHALL 提供统一的音频策略决策函数，输入为模型能力和用户偏好
2. WHEN 视频模型支持集成音频时，THE System SHALL 默认使用模型音频
3. IF 用户选择覆盖模型音频，THEN THE System SHALL 显示风险警告和成本影响
4. THE System SHALL 支持三种音频模式：MODEL_EMBEDDED、EXTERNAL_FULL、HYBRID_OVERLAY
5. THE System SHALL 在 Shared Blackboard 中记录每个 shot 的音频策略决策

### Requirement 3: DNA Bank 增强管理

**User Story:** 作为 ArtDirector Agent，我希望 DNA Bank 能够智能管理多版本特征，以便保持视觉一致性。

#### Acceptance Criteria

1. THE System SHALL 为每个角色维护多版本 embedding 历史记录
2. THE System SHALL 支持加权平均、最新优先、置信度筛选等多种合并策略
3. WHEN 新特征置信度低于 0.6 时，THE System SHALL 触发人工审核
4. THE System SHALL 记录每个 embedding 的来源 shot 和提取时间
5. THE System SHALL 支持 DNA 版本回滚和对比功能

### Requirement 4: 任务调度机制明确化

**User Story:** 作为 Orchestrator，我希望有清晰的任务调度规则，以便高效分配和追踪工作。

#### Acceptance Criteria

1. THE System SHALL 定义任务（Task）为 Orchestrator 分配给 Agent 的工作单元
2. THE System SHALL 定义事件（Event）为 Agent 间的异步通知机制
3. WHEN Agent 完成任务时，THE System SHALL 发布对应的完成事件
4. THE System SHALL 支持任务优先级（1-5 级）和依赖关系定义
5. THE System SHALL 在 Shared Blackboard 中维护任务状态机（PENDING/IN_PROGRESS/COMPLETED/FAILED）

### Requirement 5: QA 阈值动态调整

**User Story:** 作为 ConsistencyGuardian，我希望根据项目预算和质量要求动态调整 QA 阈值，以便平衡质量和成本。

#### Acceptance Criteria

1. THE System SHALL 根据用户选择的质量档位（High/Balanced/Fast）调整 QA 阈值
2. WHEN 项目预算紧张时，THE System SHALL 适当降低非关键指标的阈值
3. THE System SHALL 为关键指标（如 face_identity）设置最低阈值下限
4. THE System SHALL 记录每次 QA 检测的实际阈值和通过情况
5. THE System SHALL 支持 ChefAgent 手动调整项目级 QA 策略

### Requirement 6: Editor Agent 详细设计

**User Story:** 作为系统设计者，我希望补充 Editor Agent 的详细设计，以便完成视频最终合成。

#### Acceptance Criteria

1. THE System SHALL 定义 Editor Agent 负责多 shot 拼接、音频混合、转场效果
2. THE System SHALL 支持基于 music markers 的节拍对齐剪辑
3. THE System SHALL 支持基于 phoneme timestamps 的口型同步
4. THE System SHALL 提供音频 ducking、淡入淡出等基础混音功能
5. THE System SHALL 输出最终视频文件和元数据（包含所有 shot 信息）

### Requirement 7: 成本控制与预测

**User Story:** 作为 ChefAgent，我希望实时监控项目成本并预测最终开销，以便做出预算决策。

#### Acceptance Criteria

1. THE System SHALL 为每个模型调用记录实际成本
2. THE System SHALL 在任务分配前预估任务成本
3. WHEN 项目已用预算超过 80% 时，THE System SHALL 发出预警
4. THE System SHALL 提供成本优化建议（如切换更便宜的模型）
5. THE System SHALL 在 Shared Blackboard 中实时更新预算使用情况

### Requirement 8: 跨 Shot 时间连贯性

**User Story:** 作为 ConsistencyGuardian，我希望检测相邻 shot 之间的视觉和时间连贯性，以便保证观看体验。

#### Acceptance Criteria

1. THE System SHALL 比较相邻 shot 的结束帧和开始帧的视觉相似度
2. WHEN 相邻 shot 的 embedding 差异大于 0.3 时，THE System SHALL 标记为不连贯
3. THE System SHALL 检测时间轴上的逻辑跳跃（如光照突变、角色位置跳变）
4. THE System SHALL 建议添加转场效果或调整 shot 顺序
5. THE System SHALL 支持 ShotDirector 手动标记允许的不连贯点（如场景切换）

### Requirement 9: PromptEngineer 模板库

**User Story:** 作为 PromptEngineer Agent，我希望有结构化的 prompt 模板库，以便快速生成高质量 prompt。

#### Acceptance Criteria

1. THE System SHALL 维护分类的 prompt 模板库（角色、场景、动作、风格）
2. THE System SHALL 支持模板变量替换（如 {character_name}、{mood}）
3. THE System SHALL 根据 DNA Bank 自动注入视觉一致性 token
4. THE System SHALL 支持 negative prompt 管理和自动应用
5. THE System SHALL 记录每个 prompt 的生成历史和效果评分

### Requirement 10: 错误恢复与降级策略

**User Story:** 作为系统运维人员，我希望系统具备自动错误恢复能力，以便提高可用性。

#### Acceptance Criteria

1. WHEN Agent 任务失败时，THE System SHALL 自动重试最多 3 次
2. IF 重试失败，THEN THE System SHALL 尝试切换备用模型
3. IF 模型切换失败，THEN THE System SHALL 降级为低质量输出（如静态图片）
4. THE System SHALL 记录所有失败和降级事件到 error_log
5. WHEN 关键任务失败时，THE System SHALL 触发 HumanGate 人工介入

### Requirement 11: 用户审批检查点

**User Story:** 作为用户，我希望在关键阶段能够审查和确认 Agent 的输出结果，以便确保生成内容符合我的预期。

#### Acceptance Criteria

1. THE System SHALL 在关键 Agent 完成工作后暂停流程，等待用户审批
2. THE System SHALL 支持可配置的审批检查点（用户可选择哪些阶段需要审批）
3. WHEN Agent 输出等待审批时，THE System SHALL 通知用户并展示结果预览
4. THE System SHALL 支持三种用户决策：批准（Approve）、修改后重试（Revise）、拒绝重做（Reject）
5. WHEN 用户选择修改时，THE System SHALL 允许用户提供修改意见并触发 Agent 重新执行
6. THE System SHALL 记录所有用户审批决策和修改意见到 Blackboard
7. THE System SHALL 支持"自动模式"，跳过所有审批检查点直接执行到完成
8. THE System SHALL 为以下关键阶段提供默认审批检查点：剧本生成、分镜规划、关键帧预览、预览视频、最终视频
9. WHEN 用户长时间未响应审批请求时，THE System SHALL 发送提醒通知
10. THE System SHALL 在 UI 中清晰展示当前等待审批的内容和历史审批记录

### Requirement 12: 图像编辑与精细调整

**User Story:** 作为用户，我希望能够对生成的图像进行精细编辑（如调整视角、修正细节），而不是完全重新生成，以便节省时间和成本。

#### Acceptance Criteria

1. THE System SHALL 支持基于文本指令的图像编辑功能
2. THE System SHALL 支持视角调整（如"改为侧面 45 度视角"）
3. THE System SHALL 支持局部修改（如"修改人物表情"、"调整手部姿态"）
4. WHEN 用户在审批时选择"编辑"时，THE System SHALL 提供编辑指令输入界面
5. THE System SHALL 在编辑时保持人物身份一致性（基于 DNA Bank）
6. THE System SHALL 支持多轮迭代编辑
7. THE System SHALL 保留编辑历史，支持撤销操作
8. THE System SHALL 评估编辑质量，若质量不达标则尝试其他编辑策略
9. THE System SHALL 记录编辑成本，纳入项目预算管理
10. THE System SHALL 支持以下编辑模型：Qwen-Image-Edit、ControlNet Inpaint、InstructPix2Pix

### Requirement 13: 智能错误检测与修正

**User Story:** 作为系统，我希望能够自动检测生成内容中的常见错误（如人物动作错误、手部缺陷），并提供修正方案，以便提高输出质量。

#### Acceptance Criteria

1. THE System SHALL 自动检测以下类型的视觉错误：人物姿态错误、手部缺陷、面部错误、物理规律违背、文字错误
2. THE System SHALL 为每个检测到的错误分配严重程度（critical/medium/minor）
3. WHEN 检测到严重错误时，THE System SHALL 自动尝试修复
4. THE System SHALL 支持用户在审批时标注错误区域和类型
5. THE System SHALL 根据错误类型选择合适的修复策略（inpainting/face restoration/pose control/重新生成）
6. THE System SHALL 优先使用局部修复而非完全重新生成
7. WHEN 自动修复失败时，THE System SHALL 升级到人工介入
8. THE System SHALL 记录所有错误检测和修复历史
9. THE System SHALL 在用户审批界面显示检测到的错误和修复建议
10. THE System SHALL 支持用户提供错误反馈，用于优化检测模型
