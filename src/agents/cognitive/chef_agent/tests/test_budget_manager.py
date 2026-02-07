"""
BudgetManager 单元测试

Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5
"""

import pytest
from src.agents.cognitive.chef_agent.budget_manager import BudgetManager
from src.agents.cognitive.chef_agent.models import Money, Budget, BudgetStatus, EventType
from src.agents.cognitive.chef_agent.config import ChefAgentConfig


@pytest.fixture
def config():
    """创建测试配置"""
    return ChefAgentConfig()


@pytest.fixture
def budget_manager(config):
    """创建 BudgetManager 实例"""
    return BudgetManager(config)


class TestAllocateBudget:
    """测试预算分配功能"""

    def test_allocate_budget_high_quality(self, budget_manager):
        """测试高质量档位的预算分配 (Requirements 1.1, 1.2)"""
        duration = 30.0
        quality_tier = "high"

        budget = budget_manager.allocate_budget(duration, quality_tier)

        # 30秒 * $3/秒 * 1.5 = $135
        expected_total = 30.0 * 3.0 * 1.5
        assert budget.total.amount == expected_total
        assert budget.spent.amount == 0.0
        assert budget.estimated_remaining.amount == expected_total
        assert budget.total.currency == "USD"

    def test_allocate_budget_balanced_quality(self, budget_manager):
        """测试平衡档位的预算分配 (Requirements 1.1, 1.3)"""
        duration = 60.0
        quality_tier = "balanced"

        budget = budget_manager.allocate_budget(duration, quality_tier)

        # 60秒 * $3/秒 * 1.0 = $180
        expected_total = 60.0 * 3.0 * 1.0
        assert budget.total.amount == expected_total
        assert budget.spent.amount == 0.0

    def test_allocate_budget_fast_quality(self, budget_manager):
        """测试快速档位的预算分配 (Requirements 1.1, 1.4)"""
        duration = 45.0
        quality_tier = "fast"

        budget = budget_manager.allocate_budget(duration, quality_tier)

        # 45秒 * $3/秒 * 0.6 = $81
        expected_total = 45.0 * 3.0 * 0.6
        assert budget.total.amount == expected_total


class TestUpdateSpent:
    """测试预算更新功能"""

    def test_update_spent_single_cost(self, budget_manager):
        """测试单次成本更新 (Requirements 2.1)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        cost = Money(amount=25.0, currency="USD")
        updated_budget = budget_manager.update_spent(budget, cost)

        assert updated_budget.spent.amount == 25.0
        assert updated_budget.estimated_remaining.amount == 75.0

    def test_update_spent_multiple_costs(self, budget_manager):
        """测试多次成本累加 (Requirements 2.1)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        costs = [10.0, 15.0, 20.0, 5.0]
        for cost_amount in costs:
            cost = Money(amount=cost_amount, currency="USD")
            budget = budget_manager.update_spent(budget, cost)

        assert budget.spent.amount == 50.0
        assert budget.estimated_remaining.amount == 50.0


class TestEstimateDefaultCost:
    """测试默认成本估算功能"""

    def test_estimate_image_cost(self, budget_manager):
        """测试图像生成成本估算 (Requirements 2.2)"""
        cost = budget_manager.estimate_default_cost(EventType.IMAGE_GENERATED)

        assert cost.amount == 0.05
        assert cost.currency == "USD"

    def test_estimate_video_cost_with_duration(self, budget_manager):
        """测试视频生成成本估算（带时长） (Requirements 2.2)"""
        duration = 10.0
        cost = budget_manager.estimate_default_cost(EventType.VIDEO_GENERATED, duration)

        # $0.50/秒 * 10秒 = $5.00
        assert cost.amount == 5.0

    def test_estimate_music_cost_with_duration(self, budget_manager):
        """测试音乐生成成本估算（带时长） (Requirements 2.2)"""
        duration = 30.0
        cost = budget_manager.estimate_default_cost(EventType.MUSIC_COMPOSED, duration)

        # $0.02/秒 * 30秒 = $0.60
        assert cost.amount == 0.6

    def test_estimate_voice_cost_with_duration(self, budget_manager):
        """测试语音生成成本估算（带时长） (Requirements 2.2)"""
        duration = 15.0
        cost = budget_manager.estimate_default_cost(EventType.VOICE_RENDERED, duration)

        # $0.02/秒 * 15秒 = $0.30
        assert cost.amount == 0.3


class TestCheckBudgetStatus:
    """测试预算状态检查功能"""

    def test_budget_status_ok(self, budget_manager):
        """测试预算状态正常 (Requirements 2.3)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=50.0, currency="USD"),
            estimated_remaining=Money(amount=50.0, currency="USD"),
        )

        status = budget_manager.check_budget_status(budget)
        assert status == BudgetStatus.OK

    def test_budget_status_warning(self, budget_manager):
        """测试预算预警状态 (Requirements 2.3)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=85.0, currency="USD"),
            estimated_remaining=Money(amount=15.0, currency="USD"),
        )

        status = budget_manager.check_budget_status(budget)
        assert status == BudgetStatus.WARNING

    def test_budget_status_exceeded(self, budget_manager):
        """测试预算超支状态 (Requirements 2.4)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=105.0, currency="USD"),
            estimated_remaining=Money(amount=0.0, currency="USD"),  # 不能为负数
        )

        status = budget_manager.check_budget_status(budget)
        assert status == BudgetStatus.EXCEEDED

    def test_budget_status_at_warning_threshold(self, budget_manager):
        """测试预算刚好达到预警阈值 (Requirements 2.3)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=80.0, currency="USD"),
            estimated_remaining=Money(amount=20.0, currency="USD"),
        )

        status = budget_manager.check_budget_status(budget)
        assert status == BudgetStatus.WARNING


class TestPredictFinalCost:
    """测试最终成本预测功能"""

    def test_predict_final_cost_half_progress(self, budget_manager):
        """测试进度50%时的成本预测 (Requirements 2.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=60.0, currency="USD"),
            estimated_remaining=Money(amount=40.0, currency="USD"),
        )

        predicted = budget_manager.predict_final_cost(budget, progress=0.5)

        # 已花费 $60，进度 50%，预测总成本 = $60 / 0.5 = $120
        assert predicted.amount == 120.0

    def test_predict_final_cost_quarter_progress(self, budget_manager):
        """测试进度25%时的成本预测 (Requirements 2.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=30.0, currency="USD"),
            estimated_remaining=Money(amount=70.0, currency="USD"),
        )

        predicted = budget_manager.predict_final_cost(budget, progress=0.25)

        # 已花费 $30，进度 25%，预测总成本 = $30 / 0.25 = $120
        assert predicted.amount == 120.0

    def test_predict_final_cost_zero_progress(self, budget_manager):
        """测试进度为0时的成本预测 (Requirements 2.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=100.0, currency="USD"),
        )

        predicted = budget_manager.predict_final_cost(budget, progress=0.0)

        # 进度为0时，返回总预算作为预测
        assert predicted.amount == 100.0

    def test_predict_final_cost_near_completion(self, budget_manager):
        """测试接近完成时的成本预测 (Requirements 2.5)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=95.0, currency="USD"),
            estimated_remaining=Money(amount=5.0, currency="USD"),
        )

        predicted = budget_manager.predict_final_cost(budget, progress=0.9)

        # 已花费 $95，进度 90%，预测总成本 = $95 / 0.9 ≈ $105.56
        assert abs(predicted.amount - 105.56) < 0.01
