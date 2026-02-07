"""
FailureEvaluator - 失败评估器

负责评估任务失败情况，决定恢复策略

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

from .models import FailureReport, EscalationDecision


class FailureEvaluator:
    """
    失败评估器

    评估任务失败情况，决定是否需要人工介入
    """

    def evaluate_failure(self, failure_report: FailureReport) -> EscalationDecision:
        """
        评估失败情况，决定是否需要人工介入

        根据以下条件决定是否触发 HUMAN_GATE：
        1. 重试次数达到 3 次
        2. 成本影响超过 $20
        3. 严重程度为 critical

        Args:
            failure_report: 失败报告

        Returns:
            EscalationDecision: 升级决策

        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        """
        # 检查重试次数 (Requirement 4.2)
        if failure_report.retry_count >= 3:
            return EscalationDecision(
                action="HUMAN_GATE", reason="Max retries exceeded", priority="high"
            )

        # 检查成本影响 (Requirement 4.3)
        if failure_report.cost_impact > 20.0:
            return EscalationDecision(
                action="HUMAN_GATE", reason="Cost impact exceeds $20", priority="high"
            )

        # 检查严重程度 (Requirement 4.4)
        if failure_report.severity == "critical":
            return EscalationDecision(
                action="HUMAN_GATE", reason="Critical failure", priority="critical"
            )

        # 可自动恢复 (Requirement 4.5)
        return EscalationDecision(
            action="AUTO_RETRY", reason="Failure is recoverable", priority="low"
        )
