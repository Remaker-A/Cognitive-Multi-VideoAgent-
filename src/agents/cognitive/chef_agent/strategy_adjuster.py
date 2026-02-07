"""
StrategyAdjuster - 策略调整器

负责根据预算状况动态调整项目策略

Requirements: 3.1, 3.2, 3.3, 3.4
"""

from typing import Any
from .models import Budget, StrategyDecision


class StrategyAdjuster:
    """
    策略调整器

    根据预算使用情况动态调整项目策略，如降低质量档位以控制成本

    Requirements:
    - 3.1: 评估是否需要降低质量档位
    - 3.2: 发布策略更新事件
    - 3.3: 更新 Blackboard 中的质量档位配置
    - 3.4: 根据预算充足程度维持当前策略
    """

    def evaluate_strategy(self, budget: Budget, quality_tier: str) -> StrategyDecision:
        """
        评估是否需要调整策略

        根据预算使用率决定是否需要降低质量档位：
        - 使用率 >= 80%: 考虑降级
        - 使用率 < 50%: 预算充足，维持当前策略
        - 其他情况: 预算正常，维持当前策略

        Args:
            budget: 当前预算状态
            quality_tier: 当前质量档位（high, balanced, fast）

        Returns:
            StrategyDecision: 策略决策

        Validates: Requirements 3.1, 3.4
        """
        # 计算预算使用率
        usage_rate = (
            budget.spent.amount / budget.total.amount
            if budget.total.amount > 0
            else 0.0
        )

        if usage_rate >= 0.8:
            # 预算紧张，考虑降级
            lower_tier = self._get_lower_tier(quality_tier)
            return StrategyDecision(
                action="REDUCE_QUALITY",
                reason="Budget usage exceeds 80%",
                params={"target_tier": lower_tier},
            )
        elif usage_rate < 0.5:
            # 预算充足，维持当前策略
            return StrategyDecision(action="CONTINUE", reason="Budget is sufficient")
        else:
            # 预算正常，维持当前策略
            return StrategyDecision(action="CONTINUE", reason="Budget usage is normal")

    def _get_lower_tier(self, current_tier: str) -> str:
        """
        获取更低的质量档位

        质量档位顺序: high -> balanced -> fast

        Args:
            current_tier: 当前质量档位

        Returns:
            str: 更低的质量档位，如果已经是最低档位则返回当前档位
        """
        tier_order = ["high", "balanced", "fast"]

        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            # 如果当前档位不在列表中，返回 balanced 作为默认值
            return "balanced"

        # 已经是最低档位，返回当前档位
        return current_tier

    def apply_strategy(self, decision: StrategyDecision, global_spec: Any) -> Any:
        """
        应用策略调整

        根据策略决策更新 GlobalSpec 的质量档位

        Args:
            decision: 策略决策
            global_spec: 当前全局规格（GlobalSpec 对象）

        Returns:
            更新后的全局规格

        Validates: Requirements 3.2, 3.3
        """
        if decision.action == "REDUCE_QUALITY":
            # 更新质量档位
            target_tier = decision.params.get("target_tier")
            if target_tier:
                global_spec.quality_tier = target_tier

        return global_spec
