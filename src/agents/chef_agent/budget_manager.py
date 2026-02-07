"""
BudgetManager - 预算管理器

负责预算分配、监控和预测

Requirements: 1.1, 1.2, 1.3, 1.4, 2.1, 2.2, 2.3, 2.4, 2.5
"""

from typing import Optional
from .models import Money, Budget, BudgetStatus, EventType
from .config import ChefAgentConfig


class BudgetManager:
    """
    预算管理器

    职责:
    - 根据项目规格分配预算
    - 更新已使用预算
    - 估算默认成本
    - 检查预算状态
    - 预测最终成本
    """

    def __init__(self, config: ChefAgentConfig):
        """
        初始化预算管理器

        Args:
            config: ChefAgent 配置
        """
        self.config = config

    def allocate_budget(self, duration: float, quality_tier: str) -> Budget:
        """
        根据项目规格分配预算

        公式:
        - 基准预算 = duration * base_budget_per_second
        - 质量乘数: high=1.5, balanced=1.0, fast=0.6
        - 总预算 = 基准预算 * 质量乘数

        Args:
            duration: 视频时长（秒）
            quality_tier: 质量档位（high, balanced, fast）

        Returns:
            Budget: 预算对象

        Validates: Requirements 1.1, 1.2, 1.3, 1.4
        """
        # 计算基准预算
        base_budget = duration * self.config.base_budget_per_second

        # 获取质量乘数
        quality_multiplier = self.config.get_quality_multiplier(quality_tier)

        # 计算总预算
        total_amount = base_budget * quality_multiplier

        return Budget(
            total=Money(amount=total_amount, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=total_amount, currency="USD"),
        )

    def update_spent(self, budget: Budget, cost: Money) -> Budget:
        """
        更新已使用预算

        Args:
            budget: 当前预算对象
            cost: 新增成本

        Returns:
            Budget: 更新后的预算对象

        Validates: Requirements 2.1
        """
        # 更新已使用预算
        budget.spent.amount += cost.amount

        # 更新预计剩余预算
        budget.estimated_remaining.amount = budget.total.amount - budget.spent.amount

        return budget

    def estimate_default_cost(
        self, event_type: EventType, duration: Optional[float] = None
    ) -> Money:
        """
        估算默认成本（当事件不包含成本信息时）

        Args:
            event_type: 事件类型
            duration: 时长（秒），用于视频、音频等按时长计费的事件

        Returns:
            Money: 估算成本

        Validates: Requirements 2.2
        """
        # 获取基础成本
        base_cost = self.config.get_default_cost(event_type.value)

        # 如果是按时长计费的事件，乘以时长
        if duration is not None and event_type in [
            EventType.VIDEO_GENERATED,
            EventType.MUSIC_COMPOSED,
            EventType.VOICE_RENDERED,
        ]:
            amount = base_cost * duration
        else:
            amount = base_cost

        return Money(amount=amount, currency="USD")

    def check_budget_status(self, budget: Budget) -> BudgetStatus:
        """
        检查预算状态

        Args:
            budget: 当前预算对象

        Returns:
            BudgetStatus: 预算状态（OK, WARNING, EXCEEDED）

        Validates: Requirements 2.3, 2.4
        """
        # 避免除以零
        if budget.total.amount == 0:
            return BudgetStatus.EXCEEDED

        # 计算使用率
        usage_rate = budget.spent.amount / budget.total.amount

        # 判断状态
        if usage_rate >= self.config.budget_exceeded_threshold:
            return BudgetStatus.EXCEEDED
        elif usage_rate >= self.config.budget_warning_threshold:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.OK

    def predict_final_cost(self, budget: Budget, progress: float) -> Money:
        """
        预测最终成本

        Args:
            budget: 当前预算
            progress: 项目进度（0.0-1.0）

        Returns:
            Money: 预测的最终成本

        Validates: Requirements 2.5
        """
        # 如果进度为 0，返回总预算作为预测
        if progress == 0 or progress < 0.01:
            return Money(amount=budget.total.amount, currency="USD")

        # 根据当前进度预测最终成本
        predicted_amount = budget.spent.amount / progress

        return Money(amount=predicted_amount, currency="USD")
