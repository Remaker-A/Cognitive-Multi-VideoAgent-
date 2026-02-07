"""
StrategyAdjuster 单元测试和属性基测试

Requirements: 3.1, 3.2, 3.3, 3.4
"""

import pytest
from dataclasses import dataclass
from hypothesis import given, strategies as st, assume
from src.agents.chef_agent.strategy_adjuster import StrategyAdjuster
from src.agents.chef_agent.models import Money, Budget, StrategyDecision


@dataclass
class MockGlobalSpec:
    """模拟 GlobalSpec 对象用于测试"""

    quality_tier: str


@pytest.fixture
def strategy_adjuster():
    """创建 StrategyAdjuster 实例"""
    return StrategyAdjuster()


class TestEvaluateStrategy:
    """测试策略评估功能"""

    def test_evaluate_strategy_high_usage_triggers_reduction(self, strategy_adjuster):
        """测试高预算使用率触发降级 (Requirements 3.1)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=85.0, currency="USD"),
            estimated_remaining=Money(amount=15.0, currency="USD"),
        )
        quality_tier = "high"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        assert decision.action == "REDUCE_QUALITY"
        assert decision.reason == "Budget usage exceeds 80%"
        assert decision.params["target_tier"] == "balanced"

    def test_evaluate_strategy_at_80_percent_triggers_reduction(
        self, strategy_adjuster
    ):
        """测试预算使用率刚好80%触发降级 (Requirements 3.1)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=80.0, currency="USD"),
            estimated_remaining=Money(amount=20.0, currency="USD"),
        )
        quality_tier = "balanced"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        assert decision.action == "REDUCE_QUALITY"
        assert decision.params["target_tier"] == "fast"

    def test_evaluate_strategy_low_usage_continues(self, strategy_adjuster):
        """测试低预算使用率维持策略 (Requirements 3.4)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=30.0, currency="USD"),
            estimated_remaining=Money(amount=70.0, currency="USD"),
        )
        quality_tier = "high"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        assert decision.action == "CONTINUE"
        assert decision.reason == "Budget is sufficient"

    def test_evaluate_strategy_normal_usage_continues(self, strategy_adjuster):
        """测试正常预算使用率维持策略 (Requirements 3.4)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=60.0, currency="USD"),
            estimated_remaining=Money(amount=40.0, currency="USD"),
        )
        quality_tier = "balanced"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        assert decision.action == "CONTINUE"
        assert decision.reason == "Budget usage is normal"

    def test_evaluate_strategy_just_below_50_percent(self, strategy_adjuster):
        """测试预算使用率刚好低于50% (Requirements 3.4)"""
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=49.0, currency="USD"),
            estimated_remaining=Money(amount=51.0, currency="USD"),
        )
        quality_tier = "high"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        assert decision.action == "CONTINUE"
        assert decision.reason == "Budget is sufficient"

    def test_evaluate_strategy_zero_budget(self, strategy_adjuster):
        """测试零预算情况 (边界情况)"""
        budget = Budget(
            total=Money(amount=0.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=0.0, currency="USD"),
        )
        quality_tier = "balanced"

        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        # 使用率为 0/0，应该被处理为 0
        assert decision.action == "CONTINUE"


class TestGetLowerTier:
    """测试质量档位降级功能"""

    def test_get_lower_tier_from_high(self, strategy_adjuster):
        """测试从 high 降级到 balanced (Requirements 3.2, 3.3)"""
        lower_tier = strategy_adjuster._get_lower_tier("high")
        assert lower_tier == "balanced"

    def test_get_lower_tier_from_balanced(self, strategy_adjuster):
        """测试从 balanced 降级到 fast (Requirements 3.2, 3.3)"""
        lower_tier = strategy_adjuster._get_lower_tier("balanced")
        assert lower_tier == "fast"

    def test_get_lower_tier_from_fast(self, strategy_adjuster):
        """测试从 fast 无法继续降级 (Requirements 3.2, 3.3)"""
        lower_tier = strategy_adjuster._get_lower_tier("fast")
        assert lower_tier == "fast"

    def test_get_lower_tier_invalid_tier(self, strategy_adjuster):
        """测试无效档位返回默认值"""
        lower_tier = strategy_adjuster._get_lower_tier("invalid")
        assert lower_tier == "balanced"


class TestApplyStrategy:
    """测试策略应用功能"""

    def test_apply_strategy_reduce_quality(self, strategy_adjuster):
        """测试应用降级策略 (Requirements 3.2, 3.3)"""
        decision = StrategyDecision(
            action="REDUCE_QUALITY",
            reason="Budget usage exceeds 80%",
            params={"target_tier": "balanced"},
        )
        global_spec = MockGlobalSpec(quality_tier="high")

        updated_spec = strategy_adjuster.apply_strategy(decision, global_spec)

        assert updated_spec.quality_tier == "balanced"

    def test_apply_strategy_continue(self, strategy_adjuster):
        """测试应用维持策略 (Requirements 3.2, 3.3)"""
        decision = StrategyDecision(action="CONTINUE", reason="Budget is sufficient")
        global_spec = MockGlobalSpec(quality_tier="high")

        updated_spec = strategy_adjuster.apply_strategy(decision, global_spec)

        # 质量档位不应改变
        assert updated_spec.quality_tier == "high"

    def test_apply_strategy_reduce_quality_without_target(self, strategy_adjuster):
        """测试降级策略但没有目标档位 (边界情况)"""
        decision = StrategyDecision(
            action="REDUCE_QUALITY",
            reason="Budget usage exceeds 80%",
            params={},  # 没有 target_tier
        )
        global_spec = MockGlobalSpec(quality_tier="high")

        updated_spec = strategy_adjuster.apply_strategy(decision, global_spec)

        # 质量档位不应改变（因为没有目标档位）
        assert updated_spec.quality_tier == "high"

    def test_apply_strategy_full_workflow(self, strategy_adjuster):
        """测试完整的策略评估和应用流程 (Requirements 3.1, 3.2, 3.3)"""
        # 1. 创建高预算使用率场景
        budget = Budget(
            total=Money(amount=100.0, currency="USD"),
            spent=Money(amount=90.0, currency="USD"),
            estimated_remaining=Money(amount=10.0, currency="USD"),
        )
        global_spec = MockGlobalSpec(quality_tier="high")

        # 2. 评估策略
        decision = strategy_adjuster.evaluate_strategy(budget, global_spec.quality_tier)

        # 3. 应用策略
        updated_spec = strategy_adjuster.apply_strategy(decision, global_spec)

        # 4. 验证结果
        assert decision.action == "REDUCE_QUALITY"
        assert updated_spec.quality_tier == "balanced"


# ============================================================================
# 属性基测试 (Property-Based Tests)
# ============================================================================


class TestStrategyAdjusterProperties:
    """策略调整器的属性基测试"""

    @given(
        total_budget=st.floats(min_value=1.0, max_value=10000.0),
        spent_budget=st.floats(min_value=0.0, max_value=10000.0),
        quality_tier=st.sampled_from(["high", "balanced", "fast"]),
    )
    def test_property_strategy_decision_correctness(
        self, total_budget: float, spent_budget: float, quality_tier: str
    ):
        """
        Property 5: 策略调整决策正确性

        对于任何预算状态和项目规格，当预算使用率超过 80% 时，应该决定降低质量档位；
        当使用率低于 50% 时，应该维持当前策略。

        Feature: chef-agent, Property 5: 策略调整决策正确性
        Validates: Requirements 3.1, 3.4
        """
        # 确保 spent 不超过 total
        assume(spent_budget <= total_budget)

        # 创建预算对象
        budget = Budget(
            total=Money(amount=total_budget, currency="USD"),
            spent=Money(amount=spent_budget, currency="USD"),
            estimated_remaining=Money(
                amount=total_budget - spent_budget, currency="USD"
            ),
        )

        # 创建策略调整器
        strategy_adjuster = StrategyAdjuster()

        # 评估策略
        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        # 计算使用率
        usage_rate = spent_budget / total_budget if total_budget > 0 else 0.0

        # 验证决策正确性
        if usage_rate >= 0.8:
            # 预算使用率超过 80%，应该降低质量
            assert (
                decision.action == "REDUCE_QUALITY"
            ), f"Usage rate {usage_rate:.2%} >= 80%, should REDUCE_QUALITY"
            assert decision.reason == "Budget usage exceeds 80%"
            assert "target_tier" in decision.params
        elif usage_rate < 0.5:
            # 预算使用率低于 50%，应该维持策略
            assert (
                decision.action == "CONTINUE"
            ), f"Usage rate {usage_rate:.2%} < 50%, should CONTINUE"
            assert decision.reason == "Budget is sufficient"
        else:
            # 预算使用率在 50%-80% 之间，应该维持策略
            assert (
                decision.action == "CONTINUE"
            ), f"Usage rate {usage_rate:.2%} in [50%, 80%), should CONTINUE"
            assert decision.reason == "Budget usage is normal"

    @given(quality_tier=st.sampled_from(["high", "balanced", "fast"]))
    def test_property_quality_tier_downgrade_correctness(self, quality_tier: str):
        """
        Property 6: 质量档位降级正确性

        对于任何质量档位，降级后的档位应该在质量顺序中位于原档位之后
        (high → balanced → fast)。

        Feature: chef-agent, Property 6: 质量档位降级正确性
        Validates: Requirements 3.2, 3.3
        """
        # 定义质量档位顺序
        tier_order = ["high", "balanced", "fast"]

        # 创建策略调整器
        strategy_adjuster = StrategyAdjuster()

        # 获取降级后的档位
        lower_tier = strategy_adjuster._get_lower_tier(quality_tier)

        # 验证降级正确性
        current_index = tier_order.index(quality_tier)

        if current_index < len(tier_order) - 1:
            # 不是最低档位，应该降级到下一个档位
            expected_lower_tier = tier_order[current_index + 1]
            assert (
                lower_tier == expected_lower_tier
            ), f"Tier {quality_tier} should downgrade to {expected_lower_tier}, got {lower_tier}"
        else:
            # 已经是最低档位，应该保持不变
            assert lower_tier == quality_tier, (
                f"Tier {quality_tier} is already lowest, "
                f"should stay {quality_tier}, got {lower_tier}"
            )

    @given(
        total_budget=st.floats(min_value=1.0, max_value=10000.0),
        spent_budget=st.floats(min_value=0.0, max_value=10000.0),
        quality_tier=st.sampled_from(["high", "balanced", "fast"]),
    )
    def test_property_strategy_application_consistency(
        self, total_budget: float, spent_budget: float, quality_tier: str
    ):
        """
        Property: 策略应用一致性

        对于任何策略决策，应用策略后的质量档位应该与决策中的目标档位一致。

        Feature: chef-agent, Property: 策略应用一致性
        Validates: Requirements 3.2, 3.3
        """
        # 确保 spent 不超过 total
        assume(spent_budget <= total_budget)

        # 创建预算对象
        budget = Budget(
            total=Money(amount=total_budget, currency="USD"),
            spent=Money(amount=spent_budget, currency="USD"),
            estimated_remaining=Money(
                amount=total_budget - spent_budget, currency="USD"
            ),
        )

        # 创建策略调整器和模拟 GlobalSpec
        strategy_adjuster = StrategyAdjuster()
        global_spec = MockGlobalSpec(quality_tier=quality_tier)

        # 评估策略
        decision = strategy_adjuster.evaluate_strategy(budget, quality_tier)

        # 应用策略
        updated_spec = strategy_adjuster.apply_strategy(decision, global_spec)

        # 验证应用一致性
        if decision.action == "REDUCE_QUALITY":
            # 如果决策是降级，质量档位应该改变为目标档位
            target_tier = decision.params.get("target_tier")
            if target_tier:
                assert updated_spec.quality_tier == target_tier, (
                    f"After REDUCE_QUALITY, tier should be {target_tier}, "
                    f"got {updated_spec.quality_tier}"
                )
        elif decision.action == "CONTINUE":
            # 如果决策是维持，质量档位应该保持不变
            assert (
                updated_spec.quality_tier == quality_tier
            ), f"After CONTINUE, tier should stay {quality_tier}, got {updated_spec.quality_tier}"

    @given(
        total_budget=st.floats(min_value=1.0, max_value=10000.0),
        usage_rate=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_property_budget_threshold_boundaries(
        self, total_budget: float, usage_rate: float
    ):
        """
        Property: 预算阈值边界正确性

        验证预算使用率在阈值边界（50%, 80%）附近的决策正确性。

        Feature: chef-agent, Property: 预算阈值边界正确性
        Validates: Requirements 3.1, 3.4
        """
        # 计算 spent 预算
        spent_budget = total_budget * usage_rate

        # 创建预算对象
        budget = Budget(
            total=Money(amount=total_budget, currency="USD"),
            spent=Money(amount=spent_budget, currency="USD"),
            estimated_remaining=Money(
                amount=total_budget - spent_budget, currency="USD"
            ),
        )

        # 创建策略调整器
        strategy_adjuster = StrategyAdjuster()

        # 评估策略
        decision = strategy_adjuster.evaluate_strategy(budget, "balanced")

        # 验证阈值边界
        if usage_rate >= 0.8:
            assert decision.action == "REDUCE_QUALITY"
        elif usage_rate < 0.5:
            assert decision.action == "CONTINUE"
            assert decision.reason == "Budget is sufficient"
        else:
            assert decision.action == "CONTINUE"
            assert decision.reason == "Budget usage is normal"
