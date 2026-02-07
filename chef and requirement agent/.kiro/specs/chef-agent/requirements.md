# Requirements Document

## Introduction

ChefAgent 是 LivingAgentPipeline 系统的总监 Agent，作为项目的总指挥，负责预算分配与控制、策略调整、熔断决策以及人工介入的决策入口。ChefAgent 确保项目在预算范围内高质量完成，并在必要时触发人工审核。

## Glossary

- **ChefAgent**: 总监 Agent，负责项目全局决策和预算控制
- **GlobalSpec**: 全局项目规格，包含项目的所有配置信息
- **Budget**: 预算对象，包含总预算、已使用预算和预测最终成本
- **QualityTier**: 质量档位，包括 high（高质量）、balanced（平衡）、fast（快速）
- **HumanGate**: 人工介入机制，当自动处理失败时触发
- **Orchestrator**: 任务编排器，负责任务调度和事件路由
- **Blackboard**: 共享黑板，存储项目全局状态
- **EventBus**: 事件总线，用于 Agent 间异步通信
- **FailureReport**: 失败报告，包含错误信息、重试次数和成本影响
- **BudgetStatus**: 预算状态，包含已用预算、剩余预算和预测成本

## Requirements

### Requirement 1: 预算分配

**User Story:** 作为项目总监，我希望根据项目规格自动分配预算，以便合理控制项目成本。

#### Acceptance Criteria

1. WHEN 接收到 PROJECT_CREATED 事件 THEN ChefAgent SHALL 根据项目时长和质量档位计算总预算
2. WHEN 质量档位为 high THEN ChefAgent SHALL 将基准预算乘以 1.5 倍
3. WHEN 质量档位为 balanced THEN ChefAgent SHALL 使用基准预算（每秒 $3）
4. WHEN 质量档位为 fast THEN ChefAgent SHALL 将基准预算乘以 0.6 倍
5. WHEN 预算分配完成 THEN ChefAgent SHALL 发布 BUDGET_ALLOCATED 事件
6. WHEN 预算分配完成 THEN ChefAgent SHALL 将预算信息写入 Blackboard

### Requirement 2: 预算监控

**User Story:** 作为项目总监，我希望实时监控预算使用情况，以便及时发现预算超支风险。

#### Acceptance Criteria

1. WHEN 接收到任何包含成本信息的事件 THEN ChefAgent SHALL 更新项目已使用预算
2. WHEN 事件不包含成本信息 THEN ChefAgent SHALL 使用默认成本估算（图像生成: $0.05, 视频生成: $0.50/秒, 音频生成: $0.02/秒）
3. WHEN 已使用预算超过总预算的 80% THEN ChefAgent SHALL 发布 COST_OVERRUN_WARNING 事件
4. WHEN 已使用预算超过总预算的 100% THEN ChefAgent SHALL 发布 BUDGET_EXCEEDED 事件
5. WHEN 预测最终成本超过总预算的 120% THEN ChefAgent SHALL 触发预算调整策略
6. WHEN 预算状态更新 THEN ChefAgent SHALL 将最新预算信息写入 Blackboard

### Requirement 3: 策略调整

**User Story:** 作为项目总监，我希望根据预算使用情况动态调整项目策略，以便在预算范围内完成项目。

#### Acceptance Criteria

1. WHEN 已使用预算超过总预算的 80% THEN ChefAgent SHALL 评估是否需要降低质量档位
2. WHEN 决定降低质量 THEN ChefAgent SHALL 发布 STRATEGY_UPDATE 事件，指示切换到更便宜的模型
3. WHEN 决定降低质量 THEN ChefAgent SHALL 更新 Blackboard 中的质量档位配置
4. WHEN 预算充足（使用率低于 50%）THEN ChefAgent SHALL 维持当前策略
5. WHEN 策略调整完成 THEN ChefAgent SHALL 记录策略变更到 Blackboard 的 change_log

### Requirement 4: 失败评估与熔断

**User Story:** 作为项目总监，我希望评估任务失败情况并决定是否需要人工介入，以便确保项目质量。

#### Acceptance Criteria

1. WHEN 接收到 CONSISTENCY_FAILED 事件 THEN ChefAgent SHALL 评估失败严重程度
2. WHEN 任务重试次数达到 3 次 THEN ChefAgent SHALL 触发 HUMAN_GATE
3. WHEN 单次失败的成本影响超过 $20 THEN ChefAgent SHALL 触发 HUMAN_GATE
4. WHEN 失败严重程度为 critical THEN ChefAgent SHALL 立即触发 HUMAN_GATE
5. WHEN 失败可自动恢复 THEN ChefAgent SHALL 发布 AUTO_RETRY 指令
6. WHEN 触发 HUMAN_GATE THEN ChefAgent SHALL 发布 HUMAN_GATE_TRIGGERED 事件
7. WHEN 触发 HUMAN_GATE THEN ChefAgent SHALL 暂停项目相关任务

### Requirement 5: 人工决策处理

**User Story:** 作为项目总监，我希望处理人工决策结果，以便根据人工指示继续或终止项目。

#### Acceptance Criteria

1. WHEN 接收到 USER_APPROVED 事件 THEN ChefAgent SHALL 恢复项目执行
2. WHEN 接收到 USER_REVISION_REQUESTED 事件 THEN ChefAgent SHALL 创建修订任务
3. WHEN 接收到 USER_REJECTED 事件 THEN ChefAgent SHALL 标记项目为失败状态
4. WHEN 人工决策超时（60分钟无响应）THEN ChefAgent SHALL 发布 APPROVAL_TIMEOUT 事件
5. WHEN 处理人工决策 THEN ChefAgent SHALL 记录决策结果到 Blackboard
6. WHEN 开发环境无 Web 前端 THEN ChefAgent SHALL 支持通过 CLI 工具接收人工决策事件

### Requirement 11: 开发工具支持

**User Story:** 作为开发者，我希望在没有 Web 前端的情况下也能测试人工决策流程，以便独立开发和测试 ChefAgent。

#### Acceptance Criteria

1. THE 系统 SHALL 提供 Admin CLI 工具用于模拟人工决策
2. WHEN 在 CLI 中输入 approve THEN Admin CLI SHALL 发布 USER_APPROVED 事件
3. WHEN 在 CLI 中输入 reject THEN Admin CLI SHALL 发布 USER_REJECTED 事件
4. WHEN 在 CLI 中输入 revise THEN Admin CLI SHALL 发布 USER_REVISION_REQUESTED 事件
5. THE Admin CLI SHALL 显示当前待审批的项目列表
6. THE Admin CLI SHALL 显示项目的预算使用情况和失败原因

### Requirement 6: 项目完成确认

**User Story:** 作为项目总监，我希望确认项目最终完成，以便进行成本核算和质量验收。

#### Acceptance Criteria

1. WHEN 接收到 PROJECT_FINALIZED 事件 THEN ChefAgent SHALL 验证所有 shots 已完成
2. WHEN 所有 shots 完成 THEN ChefAgent SHALL 计算项目总成本
3. WHEN 总成本在预算范围内 THEN ChefAgent SHALL 标记项目为 DELIVERED 状态
4. WHEN 总成本超出预算 THEN ChefAgent SHALL 记录预算超支信息
5. WHEN 项目完成 THEN ChefAgent SHALL 生成项目总结报告
6. WHEN 项目完成 THEN ChefAgent SHALL 发布 PROJECT_DELIVERED 事件

### Requirement 7: 配置管理

**User Story:** 作为开发者，我希望通过环境变量配置 ChefAgent，以便在不同环境中灵活部署。

#### Acceptance Criteria

1. WHEN ChefAgent 启动 THEN 系统 SHALL 从环境变量读取配置
2. WHEN 必需配置缺失 THEN 系统 SHALL 抛出 ConfigurationError 并提供修复建议
3. WHEN 配置值无效 THEN 系统 SHALL 抛出 ConfigurationError 并提供有效值范围
4. WHEN 配置加载成功 THEN 系统 SHALL 记录配置摘要到日志
5. THE 系统 SHALL 支持配置预算基准值（默认每秒 $3）
6. THE 系统 SHALL 支持配置质量档位乘数（high: 1.5, balanced: 1.0, fast: 0.6）
7. THE 系统 SHALL 支持配置预算预警阈值（默认 80%）

### Requirement 8: 事件订阅与发布

**User Story:** 作为系统组件，ChefAgent 需要订阅相关事件并发布决策事件，以便与其他 Agent 协作。

#### Acceptance Criteria

1. THE ChefAgent SHALL 订阅 PROJECT_CREATED 事件
2. THE ChefAgent SHALL 订阅 CONSISTENCY_FAILED 事件
3. THE ChefAgent SHALL 订阅 COST_OVERRUN_WARNING 事件
4. THE ChefAgent SHALL 订阅 USER_APPROVED 事件
5. THE ChefAgent SHALL 订阅 USER_REVISION_REQUESTED 事件
6. THE ChefAgent SHALL 订阅 USER_REJECTED 事件
7. THE ChefAgent SHALL 订阅 PROJECT_FINALIZED 事件
8. WHEN 发布事件 THEN ChefAgent SHALL 包含完整的因果链信息（causation_id）
9. WHEN 发布事件 THEN ChefAgent SHALL 包含成本和延迟信息

### Requirement 9: 错误处理与恢复

**User Story:** 作为系统组件，ChefAgent 需要实现三层错误恢复策略，以便提高系统可靠性。

#### Acceptance Criteria

1. WHEN 处理事件失败 THEN ChefAgent SHALL 记录错误到日志
2. WHEN 处理事件失败 THEN ChefAgent SHALL 发布 ERROR_OCCURRED 事件
3. WHEN 错误可重试 THEN ChefAgent SHALL 使用指数退避策略重试（最多 3 次）
4. WHEN 重试失败 THEN ChefAgent SHALL 触发 HUMAN_GATE
5. WHEN 发生严重错误 THEN ChefAgent SHALL 记录错误到 Blackboard 的 error_log

### Requirement 10: 指标收集

**User Story:** 作为系统运维人员，我希望收集 ChefAgent 的运行指标，以便监控系统性能和成本。

#### Acceptance Criteria

1. THE ChefAgent SHALL 记录每个项目的预算分配时间
2. THE ChefAgent SHALL 记录预算超支率（cost_overrun_rate）
3. THE ChefAgent SHALL 记录人工介入率（human_intervention_rate）
4. THE ChefAgent SHALL 记录项目完成率（project_completion_rate）
5. THE ChefAgent SHALL 记录平均决策延迟（avg_decision_latency）
6. WHEN 项目完成 THEN ChefAgent SHALL 记录项目总成本和总时长
7. WHEN 触发 HUMAN_GATE THEN ChefAgent SHALL 记录触发原因和上下文
