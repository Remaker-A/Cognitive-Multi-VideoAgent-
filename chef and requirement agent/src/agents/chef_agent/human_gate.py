"""
HumanGate 组件 - 人工介入管理器

负责管理人工介入流程，包括触发人工介入和处理用户决策。

Requirements: 4.6, 4.7, 5.1, 5.2, 5.3, 5.4
"""

from datetime import datetime
from typing import Dict, Any
import uuid

from .models import HumanGateRequest, UserDecision, ProjectAction


class HumanGate:
    """
    人工介入管理器

    职责:
    - 触发人工介入请求
    - 处理用户决策
    - 检测超时

    Requirements: 4.6, 4.7, 5.1, 5.2, 5.3, 5.4
    """

    def __init__(self, timeout_minutes: int = 60):
        """
        初始化 HumanGate

        Args:
            timeout_minutes: 超时时间（分钟），默认 60 分钟
        """
        self.timeout_minutes = timeout_minutes

    def trigger_human_intervention(
        self, project_id: str, reason: str, context: Dict[str, Any]
    ) -> HumanGateRequest:
        """
        触发人工介入

        创建一个人工介入请求，等待用户决策。

        Args:
            project_id: 项目 ID
            reason: 触发原因（例如："Max retries exceeded", "Cost impact exceeds $20"）
            context: 上下文信息（例如：错误详情、预算状态、重试历史等）

        Returns:
            HumanGateRequest: 人工介入请求对象

        Validates: Requirements 4.6, 4.7

        Example:
            >>> gate = HumanGate()
            >>> request = gate.trigger_human_intervention(
            ...     project_id="proj_123",
            ...     reason="Max retries exceeded",
            ...     context={
            ...         "error_type": "APIError",
            ...         "retry_count": 3,
            ...         "cost_impact": 15.0
            ...     }
            ... )
            >>> request.status
            'PENDING'
        """
        request = HumanGateRequest(
            request_id=self._generate_id(),
            project_id=project_id,
            reason=reason,
            context=context,
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=self.timeout_minutes,
            decision=None,
        )

        return request

    def handle_user_decision(
        self, request: HumanGateRequest, decision: UserDecision
    ) -> ProjectAction:
        """
        处理用户决策

        根据用户的决策（approve/revise/reject）返回相应的项目操作。

        Args:
            request: 人工介入请求
            decision: 用户决策

        Returns:
            ProjectAction: 项目操作指令

        Validates: Requirements 5.1, 5.2, 5.3

        Example:
            >>> gate = HumanGate()
            >>> request = HumanGateRequest(
            ...     request_id="req_123",
            ...     project_id="proj_123",
            ...     reason="Test",
            ...     context={},
            ...     status="PENDING",
            ...     created_at=datetime.now(),
            ...     timeout_minutes=60
            ... )
            >>> decision = UserDecision(
            ...     action="approve",
            ...     notes="Looks good",
            ...     decided_at=datetime.now(),
            ...     decided_by="admin"
            ... )
            >>> action = gate.handle_user_decision(request, decision)
            >>> action.action
            'RESUME'
        """
        if decision.action == "approve":
            return ProjectAction(
                action="RESUME",
                reason="User approved",
                params={
                    "request_id": request.request_id,
                    "decided_by": decision.decided_by,
                    "decided_at": decision.decided_at.isoformat(),
                    "notes": decision.notes,
                },
            )
        elif decision.action == "revise":
            return ProjectAction(
                action="CREATE_REVISION_TASK",
                reason="User requested revision",
                params={
                    "request_id": request.request_id,
                    "revision_notes": decision.notes,
                    "decided_by": decision.decided_by,
                    "decided_at": decision.decided_at.isoformat(),
                },
            )
        elif decision.action == "reject":
            return ProjectAction(
                action="MARK_FAILED",
                reason="User rejected",
                params={
                    "request_id": request.request_id,
                    "decided_by": decision.decided_by,
                    "decided_at": decision.decided_at.isoformat(),
                    "rejection_reason": decision.notes,
                },
            )
        else:
            # 未知操作，默认拒绝
            return ProjectAction(
                action="MARK_FAILED",
                reason=f"Unknown user action: {decision.action}",
                params={
                    "request_id": request.request_id,
                    "decided_by": decision.decided_by,
                    "decided_at": decision.decided_at.isoformat(),
                },
            )

    def check_timeout(self, request: HumanGateRequest) -> bool:
        """
        检查人工介入请求是否超时

        Args:
            request: 人工介入请求

        Returns:
            bool: True 表示已超时，False 表示未超时

        Validates: Requirements 5.4

        Example:
            >>> gate = HumanGate(timeout_minutes=60)
            >>> request = HumanGateRequest(
            ...     request_id="req_123",
            ...     project_id="proj_123",
            ...     reason="Test",
            ...     context={},
            ...     status="PENDING",
            ...     created_at=datetime.now() - timedelta(hours=2),
            ...     timeout_minutes=60
            ... )
            >>> gate.check_timeout(request)
            True
        """
        elapsed = datetime.now() - request.created_at
        timeout_seconds = request.timeout_minutes * 60
        return elapsed.total_seconds() > timeout_seconds

    def _generate_id(self) -> str:
        """
        生成唯一 ID

        Returns:
            str: UUID 字符串
        """
        return f"req_{uuid.uuid4().hex[:12]}"
