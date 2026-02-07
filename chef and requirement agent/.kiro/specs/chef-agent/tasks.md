# Implementation Plan: ChefAgent

## Overview

本实现计划将 ChefAgent 的设计转化为可执行的代码任务。ChefAgent 作为系统总监，负责预算管理、策略调整、失败评估和人工介入决策。实现将遵循事件驱动架构，使用 Python 和 Pydantic 进行类型安全的开发。

## Tasks

- [x] 1. 设置项目结构和核心配置
  - 创建 `src/agents/chef_agent/` 目录结构
  - 创建 `__init__.py`, `agent.py`, `config.py`, `models.py` 等文件
  - 配置 Pydantic Settings 用于环境变量管理
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 2. 实现数据模型
  - [x] 2.1 实现 Money 和 Budget 模型
    - 定义 Money 类（金额和货币）
    - 定义 Budget 类（总预算、已使用、预计剩余）
    - 添加 Pydantic 验证规则
    - _Requirements: 1.1, 2.1_

  - [ ]* 2.2 编写 Budget 模型的属性测试
    - **Property 2: 预算累加正确性**
    - **Validates: Requirements 2.1**

  - [x] 2.3 实现 FailureReport 和 EscalationDecision 模型
    - 定义 FailureReport 类（任务 ID、错误信息、重试次数、成本影响、严重程度）
    - 定义 EscalationDecision 类（操作、原因、优先级）
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [x] 2.4 实现 StrategyDecision 和 HumanGateRequest 模型
    - 定义 StrategyDecision 类（操作、原因、参数）
    - 定义 HumanGateRequest 类（请求 ID、项目 ID、原因、状态、超时）
    - 定义 UserDecision 类（操作、备注、决策时间）
    - _Requirements: 3.1, 4.6, 5.1, 5.2, 5.3_

  - [x] 2.5 实现 ProjectSummary 和其他辅助模型
    - 定义 ProjectSummary 类（项目总结报告）
    - 定义 BudgetCompliance 类（预算合规性）
    - 定义 ValidationResult 类（验证结果）
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 3. 实现 BudgetManager 组件
  - [x] 3.1 实现预算分配逻辑
    - 实现 `allocate_budget()` 方法
    - 根据时长和质量档位计算预算
    - 应用质量乘数（high: 1.5, balanced: 1.0, fast: 0.6）
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 3.2 编写预算分配的属性测试
    - **Property 1: 预算分配一致性**
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4**

  - [x] 3.3 实现预算更新和监控逻辑
    - 实现 `update_spent()` 方法
    - 实现 `estimate_default_cost()` 方法（默认成本估算）
    - 实现 `check_budget_status()` 方法（检查预算状态）
    - 实现 `predict_final_cost()` 方法（预测最终成本）
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [ ]* 3.4 编写预算监控的属性测试
    - **Property 3: 默认成本估算一致性**
    - **Property 4: 预算阈值触发正确性**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [ ] 4. 实现 StrategyAdjuster 组件
  - [x] 4.1 实现策略评估逻辑
    - 实现 `evaluate_strategy()` 方法
    - 根据预算使用率决定是否降级
    - 实现 `_get_lower_tier()` 辅助方法
    - _Requirements: 3.1, 3.4_

  - [x] 4.2 实现策略应用逻辑
    - 实现 `apply_strategy()` 方法
    - 更新 GlobalSpec 的质量档位
    - _Requirements: 3.2, 3.3_

  - [x] 4.3 编写策略调整的属性测试

    - **Property 5: 策略调整决策正确性**
    - **Property 6: 质量档位降级正确性**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [-] 5. 实现 FailureEvaluator 组件
  - [x] 5.1 实现失败评估逻辑
    - 实现 `evaluate_failure()` 方法
    - 检查重试次数、成本影响和严重程度
    - 决定是否触发 HUMAN_GATE 或 AUTO_RETRY
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ]* 5.2 编写失败评估的属性测试
    - **Property 7: 失败升级决策正确性**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 6. 实现 HumanGate 组件
  - [x] 6.1 实现人工介入触发逻辑
    - 实现 `trigger_human_intervention()` 方法
    - 创建 HumanGateRequest 对象
    - _Requirements: 4.6, 4.7_

  - [x] 6.2 实现人工决策处理逻辑
    - 实现 `handle_user_decision()` 方法
    - 根据用户决策返回项目操作
    - 实现 `check_timeout()` 方法（超时检测）
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 6.3 编写人工决策的属性测试
    - **Property 8: 人工决策处理正确性**
    - **Property 9: 超时检测正确性**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.4**

- [x] 7. 实现 ProjectValidator 组件
  - [x] 7.1 实现项目完成验证逻辑
    - 实现 `validate_completion()` 方法
    - 检查所有 shots 是否完成
    - _Requirements: 6.1_

  - [x] 7.2 实现成本计算和预算合规性检查
    - 实现 `calculate_total_cost()` 方法
    - 实现 `check_budget_compliance()` 方法
    - _Requirements: 6.2, 6.3, 6.4_

  - [x] 7.3 实现项目总结报告生成
    - 实现 `generate_summary_report()` 方法
    - 汇总项目信息、成本和合规性
    - _Requirements: 6.5_

  - [ ]* 7.4 编写项目验证的属性测试
    - **Property 10: 项目完成验证正确性**
    - **Property 11: 成本计算正确性**
    - **Property 12: 预算合规性判断正确性**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.4**

- [x] 8. 实现 EventManager 组件
  - [x] 8.1 实现事件发布方法
    - 实现 `publish_budget_allocated()` 方法
    - 实现 `publish_cost_overrun_warning()` 方法
    - 实现 `publish_budget_exceeded()` 方法
    - 实现 `publish_strategy_update()` 方法
    - 实现 `publish_human_gate_triggered()` 方法
    - 实现 `publish_project_delivered()` 方法
    - _Requirements: 1.5, 2.3, 2.4, 3.2, 4.6, 6.6_

  - [ ]* 8.2 编写事件发布的属性测试
    - **Property 13: 事件因果链完整性**
    - **Property 14: 事件成本信息完整性**
    - **Validates: Requirements 8.8, 8.9**

- [x] 9. 实现 ChefAgent 主类
  - [x] 9.1 实现 Agent 初始化和事件订阅
    - 创建 ChefAgent 类
    - 初始化所有组件
    - 订阅相关事件（PROJECT_CREATED, CONSISTENCY_FAILED 等）
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7_

  - [x] 9.2 实现事件处理入口
    - 实现 `handle_event()` 方法
    - 路由不同类型的事件到对应的处理方法
    - _Requirements: 8.1-8.7_

  - [x] 9.3 实现 PROJECT_CREATED 事件处理
    - 实现 `_handle_project_created()` 方法
    - 调用 BudgetManager 分配预算
    - 写入 Blackboard
    - 发布 BUDGET_ALLOCATED 事件
    - _Requirements: 1.1, 1.5, 1.6_

  - [x] 9.4 实现预算监控事件处理
    - 实现 `_handle_cost_event()` 方法
    - 更新预算使用情况
    - 检查预算状态并发布警告事件
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.6_

  - [x] 9.5 实现失败评估事件处理
    - 实现 `_handle_consistency_failed()` 方法
    - 调用 FailureEvaluator 评估失败
    - 根据决策触发 HUMAN_GATE 或 AUTO_RETRY
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7_

  - [x] 9.6 实现人工决策事件处理
    - 实现 `_handle_user_approved()` 方法
    - 实现 `_handle_user_revision_requested()` 方法
    - 实现 `_handle_user_rejected()` 方法
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [x] 9.7 实现项目完成事件处理
    - 实现 `_handle_project_finalized()` 方法
    - 验证项目完成
    - 计算总成本
    - 生成总结报告
    - 发布 PROJECT_DELIVERED 事件
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_

- [x] 10. 实现错误处理和恢复
  - [x] 10.1 实现三层错误恢复策略
    - 实现 `retry_with_backoff()` 方法（Level 1）
    - 实现 `handle_with_fallback()` 方法（Level 2）
    - 实现 `escalate_to_human()` 方法（Level 3）
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ]* 10.2 编写错误恢复的属性测试
    - **Property 15: 错误重试指数退避**
    - **Validates: Requirements 9.3**

- [x] 11. 实现 MetricsCollector 组件
  - [x] 11.1 实现指标收集方法
    - 实现 `record_budget_allocation()` 方法
    - 实现 `record_cost_overrun()` 方法
    - 实现 `record_human_intervention()` 方法
    - 实现 `record_project_completion()` 方法
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7_

- [x] 12. 实现 Admin CLI 工具
  - [x] 12.1 创建 CLI 工具结构
    - 创建 `tools/admin_cli.py` 文件
    - 实现命令行参数解析
    - _Requirements: 11.1_

  - [x] 12.2 实现人工决策命令
    - 实现 `approve` 命令
    - 实现 `reject` 命令
    - 实现 `revise` 命令
    - 发布相应的用户决策事件
    - _Requirements: 11.2, 11.3, 11.4_

  - [x] 12.3 实现项目状态查询命令
    - 实现 `list` 命令（显示待审批项目）
    - 实现 `status` 命令（显示项目详情）
    - _Requirements: 11.5, 11.6_

- [x] 13. Checkpoint - 确保所有测试通过
  - 运行所有单元测试
  - 运行所有属性基测试
  - 确保测试覆盖率达到 80% 以上
  - 如有问题，请向用户报告

- [x] 14. 集成测试和文档
  - [x] 14.1 编写集成测试
    - 测试完整的预算管理流程
    - 测试失败评估和人工介入流程
    - 测试项目完成验证流程

  - [x] 14.2 编写 README 文档
    - 说明 ChefAgent 的职责和功能
    - 提供配置示例
    - 提供使用示例
    - 说明 Admin CLI 工具的使用方法

- [x] 15. Final Checkpoint - 最终验证
  - 确保所有测试通过
  - 确保代码符合开发规范（Black + Flake8 + mypy）
  - 确保文档完整
  - 向用户报告完成情况

## Notes

- 标记为 `*` 的任务是可选的属性基测试任务，可以根据时间安排决定是否实现
- 每个任务都引用了相关的需求编号，便于追溯
- Checkpoint 任务确保增量验证，及时发现问题
- 属性基测试使用 Hypothesis 库，每个测试运行 100 次迭代
- 单元测试和属性基测试是互补的，都需要实现以确保代码质量
