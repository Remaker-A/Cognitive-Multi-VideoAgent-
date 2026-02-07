"""
ChefAgent - 总监 Agent 主类

负责项目全局决策和预算控制，作为系统的"大脑"协调整个视频生成流程

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
"""

import logging
from typing import Dict, Any, Optional, Set
from datetime import datetime

from .config import ChefAgentConfig
from .models import Event, EventType, Money, Budget, FailureReport, UserDecision
from .budget_manager import BudgetManager
from .strategy_adjuster import StrategyAdjuster
from .failure_evaluator import FailureEvaluator
from .human_gate import HumanGate
from .project_validator import ProjectValidator
from .event_manager import EventManager


class ChefAgent:
    """
    ChefAgent - 总监 Agent

    核心职责:
    1. 预算管理: 根据项目规格分配预算，实时监控预算使用情况
    2. 策略调整: 根据预算使用情况动态调整项目策略
    3. 失败评估: 评估任务失败情况，决定是否需要人工介入
    4. 人工决策处理: 处理人工审批结果，恢复或终止项目
    5. 项目完成确认: 验证项目完成，进行成本核算和质量验收

    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7
    """

    def __init__(
        self,
        config: Optional[ChefAgentConfig] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        初始化 ChefAgent

        Args:
            config: ChefAgent 配置（可选，默认从环境变量加载）
            logger: 日志记录器（可选）

        Validates: Requirements 8.1
        """
        # 配置
        self.config = config or ChefAgentConfig()

        # 日志
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info(
            f"Initializing ChefAgent", extra={"config": self.config.to_dict()}
        )

        # 初始化所有组件
        self.budget_manager = BudgetManager(self.config)
        self.strategy_adjuster = StrategyAdjuster()
        self.failure_evaluator = FailureEvaluator()
        self.human_gate = HumanGate(
            timeout_minutes=self.config.human_gate_timeout_minutes
        )
        self.project_validator = ProjectValidator()
        self.event_manager = EventManager(
            agent_name=self.config.agent_name, logger=self.logger
        )

        # 订阅的事件类型 (Requirements 8.1-8.7)
        self.subscribed_events: Set[EventType] = {
            EventType.PROJECT_CREATED,  # 8.1
            EventType.CONSISTENCY_FAILED,  # 8.2
            EventType.COST_OVERRUN_WARNING,  # 8.3
            EventType.USER_APPROVED,  # 8.4
            EventType.USER_REVISION_REQUESTED,  # 8.5
            EventType.USER_REJECTED,  # 8.6
            EventType.PROJECT_FINALIZED,  # 8.7
            # 额外订阅成本相关事件用于预算监控
            EventType.IMAGE_GENERATED,
            EventType.VIDEO_GENERATED,
            EventType.MUSIC_COMPOSED,
            EventType.VOICE_RENDERED,
        }

        # 项目状态缓存（简化版，实际应该从 Blackboard 读取）
        self._project_cache: Dict[str, Dict[str, Any]] = {}

        self.logger.info(
            f"ChefAgent initialized successfully",
            extra={
                "subscribed_events": [e.value for e in self.subscribed_events],
                "components": [
                    "BudgetManager",
                    "StrategyAdjuster",
                    "FailureEvaluator",
                    "HumanGate",
                    "ProjectValidator",
                    "EventManager",
                ],
            },
        )

    def get_subscribed_events(self) -> Set[EventType]:
        """
        获取订阅的事件类型列表

        Returns:
            订阅的事件类型集合

        Validates: Requirements 8.1-8.7
        """
        return self.subscribed_events.copy()

    def is_subscribed(self, event_type: EventType) -> bool:
        """
        检查是否订阅了指定事件类型

        Args:
            event_type: 事件类型

        Returns:
            True 表示已订阅，False 表示未订阅
        """
        return event_type in self.subscribed_events

    async def handle_event(self, event: Event) -> None:
        """
        事件处理入口

        路由不同类型的事件到对应的处理方法

        Args:
            event: 事件对象

        Validates: Requirements 8.1-8.7
        """
        # 检查是否订阅了该事件
        if not self.is_subscribed(event.event_type):
            self.logger.debug(
                f"Ignoring unsubscribed event",
                extra={
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "project_id": event.project_id,
                },
            )
            return

        self.logger.info(
            f"Handling event",
            extra={
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "project_id": event.project_id,
                "actor": event.actor,
            },
        )

        # 定义事件处理函数
        async def handle_event_with_recovery():
            # 路由事件到对应的处理方法
            if event.event_type == EventType.PROJECT_CREATED:
                await self._handle_project_created(event)

            elif event.event_type in [
                EventType.IMAGE_GENERATED,
                EventType.VIDEO_GENERATED,
                EventType.MUSIC_COMPOSED,
                EventType.VOICE_RENDERED,
            ]:
                await self._handle_cost_event(event)

            elif event.event_type == EventType.CONSISTENCY_FAILED:
                await self._handle_consistency_failed(event)

            elif event.event_type == EventType.USER_APPROVED:
                await self._handle_user_approved(event)

            elif event.event_type == EventType.USER_REVISION_REQUESTED:
                await self._handle_user_revision_requested(event)

            elif event.event_type == EventType.USER_REJECTED:
                await self._handle_user_rejected(event)

            elif event.event_type == EventType.PROJECT_FINALIZED:
                await self._handle_project_finalized(event)

            else:
                self.logger.warning(
                    f"No handler for event type",
                    extra={
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                    },
                )

        # 使用三层错误恢复策略
        try:
            # Level 1: 自动重试
            await self.retry_with_backoff(
                func=handle_event_with_recovery,
                context={
                    "event_id": event.event_id,
                    "event_type": event.event_type.value,
                    "project_id": event.project_id,
                },
            )

        except Exception as e:
            # Level 1 失败，尝试 Level 2: 策略降级
            try:
                project_data = self._project_cache.get(event.project_id)
                budget = project_data.get("budget") if project_data else None

                await self.handle_with_fallback(
                    error=e,
                    context={
                        "project_id": event.project_id,
                        "budget": budget,
                        "event_id": event.event_id,
                    },
                )

                # 降级成功，重试事件处理
                await handle_event_with_recovery()

            except Exception as fallback_error:
                # Level 2 失败，升级到 Level 3: 人工介入
                self.logger.error(
                    f"Error handling event after fallback",
                    extra={
                        "event_id": event.event_id,
                        "event_type": event.event_type.value,
                        "project_id": event.project_id,
                        "error": str(fallback_error),
                    },
                    exc_info=True,
                )

                # 发布错误事件 (Requirement 9.2)
                await self._publish_error_event(event, fallback_error)

                # 升级到人工介入
                await self.escalate_to_human(
                    error=fallback_error,
                    context={
                        "project_id": event.project_id,
                        "event_id": event.event_id,
                        "retry_count": self.config.max_retries,
                    },
                )

    async def _handle_project_created(self, event: Event) -> None:
        """
        处理 PROJECT_CREATED 事件

        1. 调用 BudgetManager 分配预算
        2. 写入 Blackboard（简化版：缓存到内存）
        3. 发布 BUDGET_ALLOCATED 事件

        Args:
            event: PROJECT_CREATED 事件

        Validates: Requirements 1.1, 1.5, 1.6
        """
        project_id = event.project_id
        payload = event.payload

        # 从 payload 中提取项目信息
        duration = payload.get("duration", 30.0)  # 默认 30 秒
        quality_tier = payload.get("quality_tier", "balanced")  # 默认 balanced

        self.logger.info(
            f"Processing PROJECT_CREATED event",
            extra={
                "project_id": project_id,
                "duration": duration,
                "quality_tier": quality_tier,
            },
        )

        # 1. 分配预算 (Requirement 1.1)
        budget = self.budget_manager.allocate_budget(
            duration=duration, quality_tier=quality_tier
        )

        self.logger.info(
            f"Budget allocated",
            extra={
                "project_id": project_id,
                "total_budget": budget.total.amount,
                "currency": budget.total.currency,
            },
        )

        # 2. 写入 Blackboard (Requirement 1.6)
        # 简化版：缓存到内存，实际应该调用 Blackboard API
        self._project_cache[project_id] = {
            "project_id": project_id,
            "duration": duration,
            "quality_tier": quality_tier,
            "budget": budget,
            "created_at": datetime.now(),
            "status": "ACTIVE",
        }

        # 3. 发布 BUDGET_ALLOCATED 事件 (Requirement 1.5)
        await self.event_manager.publish_budget_allocated(
            project_id=project_id,
            budget=budget,
            quality_tier=quality_tier,
            duration=duration,
            causation_id=event.event_id,
        )

        self.logger.info(
            f"PROJECT_CREATED event processed successfully",
            extra={"project_id": project_id, "budget_total": budget.total.amount},
        )

    async def _handle_cost_event(self, event: Event) -> None:
        """
        处理成本相关事件（IMAGE_GENERATED, VIDEO_GENERATED 等）

        1. 更新预算使用情况
        2. 检查预算状态并发布警告事件

        Args:
            event: 成本相关事件

        Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.6
        """
        project_id = event.project_id

        # 获取项目预算信息
        project_data = self._project_cache.get(project_id)
        if not project_data:
            self.logger.warning(
                f"Project not found in cache",
                extra={"project_id": project_id, "event_id": event.event_id},
            )
            return

        budget: Budget = project_data["budget"]

        # 1. 获取成本信息 (Requirement 2.1, 2.2)
        if event.cost:
            cost = event.cost
        else:
            # 使用默认成本估算 (Requirement 2.2)
            duration = event.payload.get("duration")
            cost = self.budget_manager.estimate_default_cost(
                event_type=event.event_type, duration=duration
            )
            self.logger.debug(
                f"Using default cost estimation",
                extra={
                    "event_type": event.event_type.value,
                    "estimated_cost": cost.amount,
                },
            )

        # 更新预算 (Requirement 2.1)
        budget = self.budget_manager.update_spent(budget, cost)
        project_data["budget"] = budget

        self.logger.info(
            f"Budget updated",
            extra={
                "project_id": project_id,
                "event_type": event.event_type.value,
                "cost": cost.amount,
                "spent": budget.spent.amount,
                "total": budget.total.amount,
                "usage_rate": (
                    budget.spent.amount / budget.total.amount
                    if budget.total.amount > 0
                    else 0
                ),
            },
        )

        # 2. 检查预算状态 (Requirement 2.3, 2.4)
        budget_status = self.budget_manager.check_budget_status(budget)
        usage_rate = (
            budget.spent.amount / budget.total.amount if budget.total.amount > 0 else 0
        )

        # 发布预警事件
        if budget_status.value == "EXCEEDED":
            # 预算超支 (Requirement 2.4)
            await self.event_manager.publish_budget_exceeded(
                project_id=project_id,
                budget=budget,
                usage_rate=usage_rate,
                causation_id=event.event_id,
            )
            self.logger.error(
                f"Budget exceeded",
                extra={
                    "project_id": project_id,
                    "spent": budget.spent.amount,
                    "total": budget.total.amount,
                },
            )

        elif budget_status.value == "WARNING":
            # 预算预警 (Requirement 2.3)
            await self.event_manager.publish_cost_overrun_warning(
                project_id=project_id,
                budget=budget,
                usage_rate=usage_rate,
                causation_id=event.event_id,
            )
            self.logger.warning(
                f"Budget warning",
                extra={
                    "project_id": project_id,
                    "spent": budget.spent.amount,
                    "total": budget.total.amount,
                    "usage_rate": usage_rate,
                },
            )

        # 3. 写入 Blackboard (Requirement 2.6)
        # 简化版：已经更新了缓存
        self._project_cache[project_id] = project_data

    async def _handle_consistency_failed(self, event: Event) -> None:
        """
        处理 CONSISTENCY_FAILED 事件

        1. 调用 FailureEvaluator 评估失败
        2. 根据决策触发 HUMAN_GATE 或 AUTO_RETRY

        Args:
            event: CONSISTENCY_FAILED 事件

        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7
        """
        project_id = event.project_id
        payload = event.payload

        # 从 payload 中提取失败信息
        task_id = payload.get("task_id", "unknown")
        error_type = payload.get("error_type", "UnknownError")
        error_message = payload.get("error_message", "No error message provided")
        retry_count = payload.get("retry_count", 0)
        cost_impact = payload.get("cost_impact", 0.0)
        severity = payload.get("severity", "medium")

        self.logger.warning(
            f"Processing CONSISTENCY_FAILED event",
            extra={
                "project_id": project_id,
                "task_id": task_id,
                "error_type": error_type,
                "retry_count": retry_count,
                "cost_impact": cost_impact,
                "severity": severity,
            },
        )

        # 1. 创建失败报告
        failure_report = FailureReport(
            task_id=task_id,
            error_type=error_type,
            error_message=error_message,
            retry_count=retry_count,
            cost_impact=cost_impact,
            severity=severity,
            timestamp=datetime.now(),
        )

        # 2. 评估失败 (Requirements 4.1, 4.2, 4.3, 4.4, 4.5)
        decision = self.failure_evaluator.evaluate_failure(failure_report)

        self.logger.info(
            f"Failure evaluation decision",
            extra={
                "project_id": project_id,
                "task_id": task_id,
                "action": decision.action,
                "reason": decision.reason,
                "priority": decision.priority,
            },
        )

        # 3. 根据决策执行操作
        if decision.action == "HUMAN_GATE":
            # 触发人工介入 (Requirements 4.6, 4.7)
            request = self.human_gate.trigger_human_intervention(
                project_id=project_id,
                reason=decision.reason,
                context={
                    "failure_report": failure_report.model_dump(),
                    "decision": decision.model_dump(),
                    "event_id": event.event_id,
                },
            )

            # 发布 HUMAN_GATE_TRIGGERED 事件
            await self.event_manager.publish_human_gate_triggered(
                project_id=project_id, request=request, causation_id=event.event_id
            )

            # 暂停项目（简化版：更新状态）
            project_data = self._project_cache.get(project_id)
            if project_data:
                project_data["status"] = "PAUSED"
                project_data["human_gate_request"] = request
                self._project_cache[project_id] = project_data

            self.logger.warning(
                f"Human intervention triggered",
                extra={
                    "project_id": project_id,
                    "request_id": request.request_id,
                    "reason": decision.reason,
                },
            )

        elif decision.action == "AUTO_RETRY":
            # 自动重试（简化版：记录日志）
            self.logger.info(
                f"Auto retry decision",
                extra={
                    "project_id": project_id,
                    "task_id": task_id,
                    "reason": decision.reason,
                },
            )
            # 实际应该发布 AUTO_RETRY 事件，由 Orchestrator 处理

    async def _handle_user_approved(self, event: Event) -> None:
        """
        处理 USER_APPROVED 事件

        恢复项目执行

        Args:
            event: USER_APPROVED 事件

        Validates: Requirements 5.1
        """
        project_id = event.project_id
        payload = event.payload

        self.logger.info(
            f"Processing USER_APPROVED event",
            extra={
                "project_id": project_id,
                "decided_by": payload.get("decided_by", "unknown"),
                "notes": payload.get("notes"),
            },
        )

        # 创建用户决策对象
        decision = UserDecision(
            action="approve",
            notes=payload.get("notes"),
            decided_at=datetime.fromisoformat(
                payload.get("decided_at", datetime.now().isoformat())
            ),
            decided_by=payload.get("decided_by", "unknown"),
        )

        # 获取人工介入请求
        project_data = self._project_cache.get(project_id)
        if not project_data:
            self.logger.warning(
                f"Project not found in cache", extra={"project_id": project_id}
            )
            return

        request = project_data.get("human_gate_request")
        if not request:
            self.logger.warning(
                f"No human gate request found", extra={"project_id": project_id}
            )
            return

        # 处理用户决策
        action = self.human_gate.handle_user_decision(request, decision)

        # 恢复项目执行 (Requirement 5.1)
        if action.action == "RESUME":
            project_data["status"] = "ACTIVE"
            project_data["human_gate_request"] = None
            self._project_cache[project_id] = project_data

            self.logger.info(
                f"Project resumed",
                extra={
                    "project_id": project_id,
                    "action": action.action,
                    "reason": action.reason,
                },
            )

    async def _handle_user_revision_requested(self, event: Event) -> None:
        """
        处理 USER_REVISION_REQUESTED 事件

        创建修订任务

        Args:
            event: USER_REVISION_REQUESTED 事件

        Validates: Requirements 5.2
        """
        project_id = event.project_id
        payload = event.payload

        self.logger.info(
            f"Processing USER_REVISION_REQUESTED event",
            extra={
                "project_id": project_id,
                "decided_by": payload.get("decided_by", "unknown"),
                "revision_notes": payload.get("notes"),
            },
        )

        # 创建用户决策对象
        decision = UserDecision(
            action="revise",
            notes=payload.get("notes"),
            decided_at=datetime.fromisoformat(
                payload.get("decided_at", datetime.now().isoformat())
            ),
            decided_by=payload.get("decided_by", "unknown"),
        )

        # 获取人工介入请求
        project_data = self._project_cache.get(project_id)
        if not project_data:
            self.logger.warning(
                f"Project not found in cache", extra={"project_id": project_id}
            )
            return

        request = project_data.get("human_gate_request")
        if not request:
            self.logger.warning(
                f"No human gate request found", extra={"project_id": project_id}
            )
            return

        # 处理用户决策
        action = self.human_gate.handle_user_decision(request, decision)

        # 创建修订任务 (Requirement 5.2)
        if action.action == "CREATE_REVISION_TASK":
            project_data["status"] = "REVISION"
            project_data["revision_notes"] = decision.notes
            project_data["human_gate_request"] = None
            self._project_cache[project_id] = project_data

            self.logger.info(
                f"Revision task created",
                extra={
                    "project_id": project_id,
                    "action": action.action,
                    "revision_notes": decision.notes,
                },
            )
            # 实际应该发布 REVISION_TASK_CREATED 事件

    async def _handle_user_rejected(self, event: Event) -> None:
        """
        处理 USER_REJECTED 事件

        标记项目为失败状态

        Args:
            event: USER_REJECTED 事件

        Validates: Requirements 5.3
        """
        project_id = event.project_id
        payload = event.payload

        self.logger.warning(
            f"Processing USER_REJECTED event",
            extra={
                "project_id": project_id,
                "decided_by": payload.get("decided_by", "unknown"),
                "rejection_reason": payload.get("notes"),
            },
        )

        # 创建用户决策对象
        decision = UserDecision(
            action="reject",
            notes=payload.get("notes"),
            decided_at=datetime.fromisoformat(
                payload.get("decided_at", datetime.now().isoformat())
            ),
            decided_by=payload.get("decided_by", "unknown"),
        )

        # 获取人工介入请求
        project_data = self._project_cache.get(project_id)
        if not project_data:
            self.logger.warning(
                f"Project not found in cache", extra={"project_id": project_id}
            )
            return

        request = project_data.get("human_gate_request")
        if not request:
            self.logger.warning(
                f"No human gate request found", extra={"project_id": project_id}
            )
            return

        # 处理用户决策
        action = self.human_gate.handle_user_decision(request, decision)

        # 标记项目为失败 (Requirement 5.3)
        if action.action == "MARK_FAILED":
            project_data["status"] = "FAILED"
            project_data["failure_reason"] = decision.notes
            project_data["human_gate_request"] = None
            self._project_cache[project_id] = project_data

            self.logger.error(
                f"Project marked as failed",
                extra={
                    "project_id": project_id,
                    "action": action.action,
                    "failure_reason": decision.notes,
                },
            )
            # 实际应该发布 PROJECT_FAILED 事件

    async def _handle_project_finalized(self, event: Event) -> None:
        """
        处理 PROJECT_FINALIZED 事件

        1. 验证项目完成
        2. 计算总成本
        3. 生成总结报告
        4. 发布 PROJECT_DELIVERED 事件

        Args:
            event: PROJECT_FINALIZED 事件

        Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5, 6.6
        """
        project_id = event.project_id
        payload = event.payload

        self.logger.info(
            f"Processing PROJECT_FINALIZED event", extra={"project_id": project_id}
        )

        # 获取项目数据
        project_data = self._project_cache.get(project_id)
        if not project_data:
            self.logger.error(
                f"Project not found in cache", extra={"project_id": project_id}
            )
            return

        # 从 payload 构建简化的 Project 对象
        # 实际应该从 Blackboard 读取完整的项目数据
        shots_data = payload.get("shots", {})
        artifacts_data = payload.get("artifacts", {})

        from .project_validator import Shot, Artifact, GlobalSpec, Project

        # 构建 shots
        shots = {
            shot_id: Shot(shot_id=shot_id, status=shot_info.get("status", "UNKNOWN"))
            for shot_id, shot_info in shots_data.items()
        }

        # 构建 artifacts
        artifacts = {
            artifact_id: Artifact(
                artifact_id=artifact_id,
                cost=Money(
                    amount=artifact_info.get("cost", {}).get("amount", 0.0),
                    currency=artifact_info.get("cost", {}).get("currency", "USD"),
                ),
            )
            for artifact_id, artifact_info in artifacts_data.items()
        }

        # 构建 GlobalSpec
        global_spec = GlobalSpec(
            duration=project_data["duration"], quality_tier=project_data["quality_tier"]
        )

        # 构建 Project
        project = Project(
            project_id=project_id,
            shots=shots,
            artifact_index=artifacts,
            budget=project_data["budget"],
            globalSpec=global_spec,
            created_at=project_data["created_at"],
        )

        # 1. 验证项目完成 (Requirement 6.1)
        validation_result = self.project_validator.validate_completion(project)

        if not validation_result.is_valid:
            self.logger.error(
                f"Project validation failed",
                extra={"project_id": project_id, "reason": validation_result.reason},
            )
            return

        self.logger.info(f"Project validation passed", extra={"project_id": project_id})

        # 2. 计算总成本 (Requirement 6.2)
        total_cost = self.project_validator.calculate_total_cost(project)

        self.logger.info(
            f"Total cost calculated",
            extra={
                "project_id": project_id,
                "total_cost": total_cost.amount,
                "currency": total_cost.currency,
            },
        )

        # 3. 检查预算合规性 (Requirements 6.3, 6.4)
        compliance = self.project_validator.check_budget_compliance(project)

        if not compliance.is_compliant:
            self.logger.warning(
                f"Budget overrun detected",
                extra={
                    "project_id": project_id,
                    "overrun_amount": compliance.overrun_amount,
                },
            )

        # 4. 生成总结报告 (Requirement 6.5)
        summary = self.project_validator.generate_summary_report(project)

        self.logger.info(
            f"Project summary generated",
            extra={
                "project_id": project_id,
                "shots_count": summary.shots_count,
                "total_cost": summary.total_cost.amount,
                "budget_compliant": summary.budget_compliance.is_compliant,
            },
        )

        # 5. 发布 PROJECT_DELIVERED 事件 (Requirement 6.6)
        await self.event_manager.publish_project_delivered(
            project_id=project_id, summary=summary, causation_id=event.event_id
        )

        # 更新项目状态
        project_data["status"] = "DELIVERED"
        project_data["summary"] = summary
        self._project_cache[project_id] = project_data

        self.logger.info(
            f"PROJECT_FINALIZED event processed successfully",
            extra={"project_id": project_id, "status": "DELIVERED"},
        )

    async def _publish_error_event(
        self, original_event: Event, error: Exception
    ) -> None:
        """
        发布错误事件

        Args:
            original_event: 触发错误的原始事件
            error: 异常对象
        """
        # 简化版：仅记录日志
        # 实际应该发布 ERROR_OCCURRED 事件
        self.logger.error(
            f"Error occurred while handling event",
            extra={
                "event_id": original_event.event_id,
                "event_type": original_event.event_type.value,
                "project_id": original_event.project_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

    # ========== 三层错误恢复策略 ==========
    # Requirements: 9.1, 9.2, 9.3, 9.4, 9.5

    async def retry_with_backoff(
        self,
        func,
        max_retries: Optional[int] = None,
        initial_delay: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Level 1: 自动重试（指数退避）

        触发条件:
        - 临时网络错误
        - API 超时
        - 可恢复的业务逻辑错误

        Args:
            func: 要重试的函数（可以是同步或异步函数）
            max_retries: 最大重试次数（默认使用配置值）
            initial_delay: 初始延迟（秒，默认使用配置值）
            context: 上下文信息（用于日志记录）

        Returns:
            函数执行结果

        Raises:
            Exception: 达到最大重试次数后仍失败

        Validates: Requirements 9.1, 9.3
        """
        import asyncio
        import inspect

        max_retries = max_retries or self.config.max_retries
        delay = initial_delay or self.config.initial_retry_delay
        context = context or {}

        last_error = None

        for attempt in range(max_retries):
            try:
                # 检查函数是否是协程函数
                if inspect.iscoroutinefunction(func):
                    return await func()
                else:
                    return func()

            except Exception as e:
                last_error = e

                # 记录重试日志 (Requirement 9.1)
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed",
                    extra={
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                        "retry_delay": delay,
                        "context": context,
                    },
                )

                # 如果是最后一次尝试，不再等待
                if attempt == max_retries - 1:
                    self.logger.error(
                        f"All {max_retries} retry attempts failed",
                        extra={
                            "error_type": type(last_error).__name__,
                            "error_message": str(last_error),
                            "context": context,
                        },
                    )
                    break

                # 指数退避 (Requirement 9.3)
                await asyncio.sleep(delay)
                delay *= self.config.retry_backoff_factor

        # 所有重试都失败，抛出最后一个错误
        raise last_error

    async def handle_with_fallback(
        self, error: Exception, context: Dict[str, Any]
    ) -> Any:
        """
        Level 2: 策略降级

        触发条件:
        - Level 1 重试失败
        - 预算不足
        - 质量要求可降低

        Args:
            error: 异常对象
            context: 上下文信息，应包含:
                - project_id: 项目 ID
                - budget: 预算对象
                - global_spec: 全局规格（可选）

        Returns:
            降级处理结果

        Raises:
            Exception: 无法降级时，升级到 Level 3

        Validates: Requirements 9.2, 9.4
        """
        project_id = context.get("project_id")

        self.logger.warning(
            f"Attempting fallback strategy",
            extra={
                "project_id": project_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

        # 检查是否是预算相关错误
        if "budget" in str(error).lower() or "cost" in str(error).lower():
            # 尝试降低质量档位
            budget = context.get("budget")
            project_data = self._project_cache.get(project_id)

            if budget and project_data:
                # 获取当前质量档位
                quality_tier = project_data.get("quality_tier", "balanced")

                # 评估策略调整
                decision = self.strategy_adjuster.evaluate_strategy(
                    budget=budget, quality_tier=quality_tier
                )

                if decision.action == "REDUCE_QUALITY":
                    self.logger.info(
                        f"Applying quality reduction strategy",
                        extra={
                            "project_id": project_id,
                            "current_tier": quality_tier,
                            "target_tier": decision.params.get("target_tier"),
                            "reason": decision.reason,
                        },
                    )

                    # 构建简化的 GlobalSpec 用于应用策略
                    from .project_validator import GlobalSpec

                    global_spec = GlobalSpec(
                        duration=project_data.get("duration", 30.0),
                        quality_tier=quality_tier,
                    )

                    # 应用策略调整
                    updated_spec = self.strategy_adjuster.apply_strategy(
                        decision=decision, global_spec=global_spec
                    )

                    # 更新项目缓存
                    project_data["quality_tier"] = updated_spec.quality_tier
                    self._project_cache[project_id] = project_data

                    # 发布策略更新事件
                    await self.event_manager.publish_strategy_update(
                        project_id=project_id,
                        decision=decision,
                        old_quality_tier=quality_tier,
                        new_quality_tier=updated_spec.quality_tier,
                    )

                    self.logger.info(
                        f"Fallback strategy applied successfully",
                        extra={
                            "project_id": project_id,
                            "new_quality_tier": updated_spec.quality_tier,
                        },
                    )

                    return {
                        "action": "QUALITY_REDUCED",
                        "new_tier": updated_spec.quality_tier,
                        "reason": decision.reason,
                    }

        # 无法降级，记录日志并升级到 Level 3
        self.logger.warning(
            f"Fallback strategy not applicable, escalating to human",
            extra={"project_id": project_id, "error_type": type(error).__name__},
        )

        # 升级到 Level 3
        raise error

    async def escalate_to_human(
        self, error: Exception, context: Dict[str, Any]
    ) -> None:
        """
        Level 3: 人工介入

        触发条件:
        - Level 2 降级失败
        - 关键质量指标不达标
        - 成本影响超过阈值

        Args:
            error: 异常对象
            context: 上下文信息，应包含:
                - project_id: 项目 ID
                - budget: 预算对象（可选）
                - retry_count: 重试次数（可选）
                - task_id: 任务 ID（可选）

        Validates: Requirements 9.4, 9.5
        """
        project_id = context.get("project_id")

        self.logger.error(
            f"Escalating to human intervention",
            extra={
                "project_id": project_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "context": context,
            },
        )

        # 构建人工介入请求
        request = self.human_gate.trigger_human_intervention(
            project_id=project_id,
            reason=f"Error recovery failed: {type(error).__name__}",
            context={
                "error_type": type(error).__name__,
                "error_message": str(error),
                "budget_status": context.get("budget"),
                "retry_count": context.get("retry_count", 0),
                "task_id": context.get("task_id"),
                "escalation_level": "Level 3 - Human Intervention Required",
            },
        )

        # 发布 HUMAN_GATE_TRIGGERED 事件
        await self.event_manager.publish_human_gate_triggered(
            project_id=project_id, request=request, causation_id=context.get("event_id")
        )

        # 暂停项目
        project_data = self._project_cache.get(project_id)
        if project_data:
            project_data["status"] = "PAUSED"
            project_data["human_gate_request"] = request
            self._project_cache[project_id] = project_data

        # 记录错误到 Blackboard (Requirement 9.5)
        # 简化版：记录到日志
        self.logger.error(
            f"Error logged to Blackboard",
            extra={
                "project_id": project_id,
                "request_id": request.request_id,
                "error_type": type(error).__name__,
                "error_message": str(error),
            },
        )

        self.logger.info(
            f"Human intervention triggered successfully",
            extra={"project_id": project_id, "request_id": request.request_id},
        )
