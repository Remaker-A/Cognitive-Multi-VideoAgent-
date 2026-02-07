"""
ProjectValidator - 项目验证器

负责验证项目完成状态、计算成本和生成总结报告

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

from typing import Dict
from datetime import datetime
from .models import Money, Budget, ValidationResult, BudgetCompliance, ProjectSummary


class Shot:
    """镜头对象（简化版）"""

    def __init__(self, shot_id: str, status: str):
        self.shot_id = shot_id
        self.status = status


class Artifact:
    """制品对象（简化版）"""

    def __init__(self, artifact_id: str, cost: Money):
        self.artifact_id = artifact_id
        self.cost = cost


class GlobalSpec:
    """全局规格对象（简化版）"""

    def __init__(self, duration: float, quality_tier: str):
        self.duration = duration
        self.quality_tier = quality_tier


class Project:
    """项目对象（简化版）"""

    def __init__(
        self,
        project_id: str,
        shots: Dict[str, Shot],
        artifact_index: Dict[str, Artifact],
        budget: Budget,
        globalSpec: GlobalSpec,
        created_at: datetime,
    ):
        self.project_id = project_id
        self.shots = shots
        self.artifact_index = artifact_index
        self.budget = budget
        self.globalSpec = globalSpec
        self.created_at = created_at


class ProjectValidator:
    """
    项目验证器

    负责验证项目完成状态、计算成本和生成总结报告

    Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
    """

    def validate_completion(self, project: Project) -> ValidationResult:
        """
        验证项目是否完成

        检查所有 shots 是否都处于 FINAL_RENDERED 状态

        Args:
            project: 项目对象

        Returns:
            ValidationResult: 验证结果

        Validates: Requirements 6.1
        """
        incomplete_shots = [
            shot_id
            for shot_id, shot in project.shots.items()
            if shot.status != "FINAL_RENDERED"
        ]

        if incomplete_shots:
            return ValidationResult(
                is_valid=False, reason=f"Incomplete shots: {incomplete_shots}"
            )

        return ValidationResult(is_valid=True)

    def calculate_total_cost(self, project: Project) -> Money:
        """
        计算项目总成本

        汇总所有 artifacts 的成本

        Args:
            project: 项目对象

        Returns:
            Money: 总成本

        Validates: Requirements 6.2
        """
        total = sum(
            artifact.cost.amount
            for artifact in project.artifact_index.values()
            if artifact.cost
        )
        return Money(amount=total, currency="USD")

    def check_budget_compliance(self, project: Project) -> BudgetCompliance:
        """
        检查预算合规性

        比较总成本与预算总额，判断是否超支

        Args:
            project: 项目对象

        Returns:
            BudgetCompliance: 预算合规性

        Validates: Requirements 6.3, 6.4
        """
        total_cost = self.calculate_total_cost(project)
        budget = project.budget

        if total_cost.amount <= budget.total.amount:
            return BudgetCompliance(is_compliant=True, overrun_amount=0.0)
        else:
            return BudgetCompliance(
                is_compliant=False,
                overrun_amount=total_cost.amount - budget.total.amount,
            )

    def generate_summary_report(self, project: Project) -> ProjectSummary:
        """
        生成项目总结报告

        汇总项目信息、成本和合规性

        Args:
            project: 项目对象

        Returns:
            ProjectSummary: 项目总结

        Validates: Requirements 6.5
        """
        total_cost = self.calculate_total_cost(project)
        compliance = self.check_budget_compliance(project)

        return ProjectSummary(
            project_id=project.project_id,
            total_cost=total_cost,
            budget_total=project.budget.total,
            budget_compliance=compliance,
            shots_count=len(project.shots),
            duration=project.globalSpec.duration,
            quality_tier=project.globalSpec.quality_tier,
            created_at=project.created_at,
            completed_at=datetime.now(),
        )
