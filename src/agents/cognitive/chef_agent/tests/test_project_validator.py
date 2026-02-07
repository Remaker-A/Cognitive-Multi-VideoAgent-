"""
ProjectValidator 单元测试

Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import pytest
from datetime import datetime
from src.agents.cognitive.chef_agent.project_validator import (
    ProjectValidator,
    Project,
    Shot,
    Artifact,
    GlobalSpec,
)
from src.agents.cognitive.chef_agent.models import Money, Budget


@pytest.fixture
def project_validator():
    """创建 ProjectValidator 实例"""
    return ProjectValidator()


@pytest.fixture
def sample_budget():
    """创建示例预算"""
    return Budget(
        total=Money(amount=100.0, currency="USD"),
        spent=Money(amount=0.0, currency="USD"),
        estimated_remaining=Money(amount=100.0, currency="USD"),
    )


@pytest.fixture
def sample_global_spec():
    """创建示例全局规格"""
    return GlobalSpec(duration=30.0, quality_tier="balanced")


class TestValidateCompletion:
    """测试项目完成验证功能"""

    def test_validate_completion_all_shots_complete(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试所有镜头完成的情况 (Requirements 6.1)"""
        shots = {
            "shot_001": Shot("shot_001", "FINAL_RENDERED"),
            "shot_002": Shot("shot_002", "FINAL_RENDERED"),
            "shot_003": Shot("shot_003", "FINAL_RENDERED"),
        }

        project = Project(
            project_id="proj_001",
            shots=shots,
            artifact_index={},
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        result = project_validator.validate_completion(project)

        assert result.is_valid is True
        assert result.reason is None

    def test_validate_completion_some_shots_incomplete(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试部分镜头未完成的情况 (Requirements 6.1)"""
        shots = {
            "shot_001": Shot("shot_001", "FINAL_RENDERED"),
            "shot_002": Shot("shot_002", "IN_PROGRESS"),
            "shot_003": Shot("shot_003", "FINAL_RENDERED"),
        }

        project = Project(
            project_id="proj_001",
            shots=shots,
            artifact_index={},
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        result = project_validator.validate_completion(project)

        assert result.is_valid is False
        assert "shot_002" in result.reason

    def test_validate_completion_all_shots_incomplete(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试所有镜头未完成的情况 (Requirements 6.1)"""
        shots = {
            "shot_001": Shot("shot_001", "PENDING"),
            "shot_002": Shot("shot_002", "IN_PROGRESS"),
            "shot_003": Shot("shot_003", "FAILED"),
        }

        project = Project(
            project_id="proj_001",
            shots=shots,
            artifact_index={},
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        result = project_validator.validate_completion(project)

        assert result.is_valid is False
        assert "shot_001" in result.reason
        assert "shot_002" in result.reason
        assert "shot_003" in result.reason

    def test_validate_completion_empty_shots(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试空镜头列表的情况 (Requirements 6.1)"""
        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index={},
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        result = project_validator.validate_completion(project)

        # 空镜头列表应该被视为完成
        assert result.is_valid is True


class TestCalculateTotalCost:
    """测试成本计算功能"""

    def test_calculate_total_cost_single_artifact(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试单个制品的成本计算 (Requirements 6.2)"""
        artifacts = {
            "artifact_001": Artifact("artifact_001", Money(amount=25.0, currency="USD"))
        }

        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index=artifacts,
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        total_cost = project_validator.calculate_total_cost(project)

        assert total_cost.amount == 25.0
        assert total_cost.currency == "USD"

    def test_calculate_total_cost_multiple_artifacts(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试多个制品的成本计算 (Requirements 6.2)"""
        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=10.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=15.0, currency="USD")
            ),
            "artifact_003": Artifact(
                "artifact_003", Money(amount=20.0, currency="USD")
            ),
        }

        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index=artifacts,
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        total_cost = project_validator.calculate_total_cost(project)

        assert total_cost.amount == 45.0

    def test_calculate_total_cost_empty_artifacts(
        self, project_validator, sample_budget, sample_global_spec
    ):
        """测试空制品列表的成本计算 (Requirements 6.2)"""
        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index={},
            budget=sample_budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        total_cost = project_validator.calculate_total_cost(project)

        assert total_cost.amount == 0.0


class TestCheckBudgetCompliance:
    """测试预算合规性检查功能"""

    def test_check_budget_compliance_within_budget(
        self, project_validator, sample_global_spec
    ):
        """测试成本在预算内的情况 (Requirements 6.3)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=30.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=40.0, currency="USD")
            ),
        }

        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index=artifacts,
            budget=budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        compliance = project_validator.check_budget_compliance(project)

        assert compliance.is_compliant is True
        assert compliance.overrun_amount == 0.0

    def test_check_budget_compliance_exceeds_budget(
        self, project_validator, sample_global_spec
    ):
        """测试成本超出预算的情况 (Requirements 6.4)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=60.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=70.0, currency="USD")
            ),
        }

        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index=artifacts,
            budget=budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        compliance = project_validator.check_budget_compliance(project)

        assert compliance.is_compliant is False
        assert compliance.overrun_amount == 30.0  # 130 - 100

    def test_check_budget_compliance_exactly_at_budget(
        self, project_validator, sample_global_spec
    ):
        """测试成本刚好等于预算的情况 (Requirements 6.3)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=50.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=50.0, currency="USD")
            ),
        }

        project = Project(
            project_id="proj_001",
            shots={},
            artifact_index=artifacts,
            budget=budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        compliance = project_validator.check_budget_compliance(project)

        assert compliance.is_compliant is True
        assert compliance.overrun_amount == 0.0


class TestGenerateSummaryReport:
    """测试项目总结报告生成功能"""

    def test_generate_summary_report_complete_project(
        self, project_validator, sample_global_spec
    ):
        """测试完整项目的总结报告生成 (Requirements 6.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        shots = {
            "shot_001": Shot("shot_001", "FINAL_RENDERED"),
            "shot_002": Shot("shot_002", "FINAL_RENDERED"),
        }

        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=30.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=40.0, currency="USD")
            ),
        }

        created_at = datetime(2024, 1, 1, 12, 0, 0)

        project = Project(
            project_id="proj_001",
            shots=shots,
            artifact_index=artifacts,
            budget=budget,
            globalSpec=sample_global_spec,
            created_at=created_at,
        )

        summary = project_validator.generate_summary_report(project)

        assert summary.project_id == "proj_001"
        assert summary.total_cost.amount == 70.0
        assert summary.budget_total.amount == 100.0
        assert summary.budget_compliance.is_compliant is True
        assert summary.shots_count == 2
        assert summary.duration == 30.0
        assert summary.quality_tier == "balanced"
        assert summary.created_at == created_at
        assert summary.completed_at is not None

    def test_generate_summary_report_over_budget_project(
        self, project_validator, sample_global_spec
    ):
        """测试超预算项目的总结报告生成 (Requirements 6.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        artifacts = {
            "artifact_001": Artifact(
                "artifact_001", Money(amount=80.0, currency="USD")
            ),
            "artifact_002": Artifact(
                "artifact_002", Money(amount=50.0, currency="USD")
            ),
        }

        project = Project(
            project_id="proj_002",
            shots={},
            artifact_index=artifacts,
            budget=budget,
            globalSpec=sample_global_spec,
            created_at=datetime.now(),
        )

        summary = project_validator.generate_summary_report(project)

        assert summary.project_id == "proj_002"
        assert summary.total_cost.amount == 130.0
        assert summary.budget_compliance.is_compliant is False
        assert summary.budget_compliance.overrun_amount == 30.0
