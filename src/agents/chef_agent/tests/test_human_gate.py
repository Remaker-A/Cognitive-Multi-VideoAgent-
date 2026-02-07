"""
HumanGate 组件单元测试

Requirements: 4.6, 4.7, 5.1, 5.2, 5.3, 5.4
"""

from datetime import datetime, timedelta

from ..human_gate import HumanGate
from ..models import HumanGateRequest, UserDecision


class TestHumanGate:
    """HumanGate 组件测试"""

    def test_trigger_human_intervention(self):
        """测试触发人工介入 - Requirements 4.6, 4.7"""
        gate = HumanGate(timeout_minutes=60)

        request = gate.trigger_human_intervention(
            project_id="proj_123",
            reason="Max retries exceeded",
            context={"error_type": "APIError", "retry_count": 3, "cost_impact": 15.0},
        )

        assert request.project_id == "proj_123"
        assert request.reason == "Max retries exceeded"
        assert request.status == "PENDING"
        assert request.timeout_minutes == 60
        assert "error_type" in request.context
        assert request.context["retry_count"] == 3
        assert request.request_id.startswith("req_")

    def test_handle_user_decision_approve(self):
        """测试处理用户批准决策 - Requirements 5.1"""
        gate = HumanGate()

        request = HumanGateRequest(
            request_id="req_123",
            project_id="proj_123",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60,
        )

        decision = UserDecision(
            action="approve",
            notes="Looks good",
            decided_at=datetime.now(),
            decided_by="admin",
        )

        action = gate.handle_user_decision(request, decision)

        assert action.action == "RESUME"
        assert action.reason == "User approved"
        assert action.params["decided_by"] == "admin"
        assert action.params["notes"] == "Looks good"

    def test_handle_user_decision_revise(self):
        """测试处理用户修订请求 - Requirements 5.2"""
        gate = HumanGate()

        request = HumanGateRequest(
            request_id="req_456",
            project_id="proj_456",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60,
        )

        decision = UserDecision(
            action="revise",
            notes="Please adjust the quality",
            decided_at=datetime.now(),
            decided_by="admin",
        )

        action = gate.handle_user_decision(request, decision)

        assert action.action == "CREATE_REVISION_TASK"
        assert action.reason == "User requested revision"
        assert action.params["revision_notes"] == "Please adjust the quality"
        assert action.params["decided_by"] == "admin"

    def test_handle_user_decision_reject(self):
        """测试处理用户拒绝决策 - Requirements 5.3"""
        gate = HumanGate()

        request = HumanGateRequest(
            request_id="req_789",
            project_id="proj_789",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60,
        )

        decision = UserDecision(
            action="reject",
            notes="Quality not acceptable",
            decided_at=datetime.now(),
            decided_by="admin",
        )

        action = gate.handle_user_decision(request, decision)

        assert action.action == "MARK_FAILED"
        assert action.reason == "User rejected"
        assert action.params["rejection_reason"] == "Quality not acceptable"
        assert action.params["decided_by"] == "admin"

    def test_check_timeout_not_expired(self):
        """测试超时检测 - 未超时 - Requirements 5.4"""
        gate = HumanGate(timeout_minutes=60)

        request = HumanGateRequest(
            request_id="req_123",
            project_id="proj_123",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60,
        )

        assert gate.check_timeout(request) is False

    def test_check_timeout_expired(self):
        """测试超时检测 - 已超时 - Requirements 5.4"""
        gate = HumanGate(timeout_minutes=60)

        # 创建一个 2 小时前的请求
        request = HumanGateRequest(
            request_id="req_123",
            project_id="proj_123",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now() - timedelta(hours=2),
            timeout_minutes=60,
        )

        assert gate.check_timeout(request) is True

    def test_check_timeout_edge_case(self):
        """测试超时检测 - 边界情况"""
        gate = HumanGate(timeout_minutes=60)

        # 创建一个刚好 60 分钟前的请求
        request = HumanGateRequest(
            request_id="req_123",
            project_id="proj_123",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now() - timedelta(minutes=60, seconds=1),
            timeout_minutes=60,
        )

        assert gate.check_timeout(request) is True

    def test_handle_unknown_action(self):
        """测试处理未知用户操作"""
        gate = HumanGate()

        request = HumanGateRequest(
            request_id="req_999",
            project_id="proj_999",
            reason="Test",
            context={},
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60,
        )

        decision = UserDecision(
            action="unknown_action",
            notes="Test",
            decided_at=datetime.now(),
            decided_by="admin",
        )

        action = gate.handle_user_decision(request, decision)

        # 未知操作应该默认拒绝
        assert action.action == "MARK_FAILED"
        assert "Unknown user action" in action.reason
