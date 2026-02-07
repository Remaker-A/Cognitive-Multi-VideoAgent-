"""
MetricsCollector 使用示例

演示如何使用 MetricsCollector 收集和分析 ChefAgent 的运行指标
"""

from datetime import datetime, timedelta
from src.agents.chef_agent import MetricsCollector
from src.agents.chef_agent.models import (
    Money,
    Budget,
    ProjectSummary,
    BudgetCompliance,
    HumanGateRequest
)


def main():
    """主函数"""
    print("=" * 60)
    print("MetricsCollector 使用示例")
    print("=" * 60)
    
    # 创建 MetricsCollector 实例
    metrics_collector = MetricsCollector()
    print("\n✓ MetricsCollector 初始化成功")
    
    # 模拟项目 1: 正常完成
    print("\n--- 项目 1: 正常完成 ---")
    
    budget_1 = Budget(
        total=Money(amount=100.0, currency="USD"),
        spent=Money(amount=85.0, currency="USD"),
        estimated_remaining=Money(amount=15.0, currency="USD")
    )
    
    # 记录预算分配
    metrics_collector.record_budget_allocation(
        project_id="proj_001",
        allocated_budget=budget_1,
        quality_tier="balanced",
        duration=30.0,
        allocation_time_ms=12.5
    )
    print("  ✓ 预算分配: $100.00 (balanced, 30秒)")
    
    # 记录决策延迟
    metrics_collector.record_decision_latency(
        project_id="proj_001",
        decision_type="budget_allocation",
        latency_ms=12.5
    )
    
    # 记录项目完成
    summary_1 = ProjectSummary(
        project_id="proj_001",
        total_cost=Money(amount=85.0, currency="USD"),
        budget_total=Money(amount=100.0, currency="USD"),
        budget_compliance=BudgetCompliance(
            is_compliant=True,
            overrun_amount=0.0
        ),
        shots_count=5,
        duration=30.0,
        quality_tier="balanced",
        created_at=datetime.now() - timedelta(hours=2),
        completed_at=datetime.now()
    )
    
    metrics_collector.record_project_completion(
        project_id="proj_001",
        summary=summary_1,
        project_start_time=datetime.now() - timedelta(hours=2)
    )
    print("  ✓ 项目完成: 总成本 $85.00, 符合预算")
    
    # 模拟项目 2: 预算超支
    print("\n--- 项目 2: 预算超支 ---")
    
    budget_2 = Budget(
        total=Money(amount=150.0, currency="USD"),
        spent=Money(amount=180.0, currency="USD"),
        estimated_remaining=Money(amount=0.0, currency="USD")
    )
    
    # 记录预算分配
    metrics_collector.record_budget_allocation(
        project_id="proj_002",
        allocated_budget=Budget(
            total=Money(amount=150.0, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=150.0, currency="USD")
        ),
        quality_tier="high",
        duration=60.0,
        allocation_time_ms=18.3
    )
    print("  ✓ 预算分配: $150.00 (high, 60秒)")
    
    # 记录预算超支
    metrics_collector.record_cost_overrun(
        project_id="proj_002",
        budget=budget_2
    )
    print("  ⚠ 预算超支: 已使用 $180.00 / 总预算 $150.00")
    
    # 记录项目完成
    summary_2 = ProjectSummary(
        project_id="proj_002",
        total_cost=Money(amount=180.0, currency="USD"),
        budget_total=Money(amount=150.0, currency="USD"),
        budget_compliance=BudgetCompliance(
            is_compliant=False,
            overrun_amount=30.0
        ),
        shots_count=8,
        duration=60.0,
        quality_tier="high",
        created_at=datetime.now() - timedelta(hours=3),
        completed_at=datetime.now()
    )
    
    metrics_collector.record_project_completion(
        project_id="proj_002",
        summary=summary_2,
        project_start_time=datetime.now() - timedelta(hours=3)
    )
    print("  ✓ 项目完成: 总成本 $180.00, 超支 $30.00")
    
    # 模拟项目 3: 需要人工介入
    print("\n--- 项目 3: 需要人工介入 ---")
    
    budget_3 = Budget(
        total=Money(amount=200.0, currency="USD"),
        spent=Money(amount=120.0, currency="USD"),
        estimated_remaining=Money(amount=80.0, currency="USD")
    )
    
    # 记录预算分配
    metrics_collector.record_budget_allocation(
        project_id="proj_003",
        allocated_budget=budget_3,
        quality_tier="high",
        duration=90.0,
        allocation_time_ms=15.7
    )
    print("  ✓ 预算分配: $200.00 (high, 90秒)")
    
    # 记录人工介入
    human_gate_request = HumanGateRequest(
        request_id="req_001",
        project_id="proj_003",
        reason="Max retries exceeded",
        context={
            "error_type": "APITimeout",
            "retry_count": 3,
            "cost_impact": 25.0
        },
        status="PENDING",
        created_at=datetime.now(),
        timeout_minutes=60
    )
    
    metrics_collector.record_human_intervention(
        project_id="proj_003",
        request=human_gate_request
    )
    print("  ⚠ 触发人工介入: Max retries exceeded")
    
    # 记录决策延迟
    metrics_collector.record_decision_latency(
        project_id="proj_003",
        decision_type="failure_evaluation",
        latency_ms=45.2
    )
    
    # 记录项目完成
    summary_3 = ProjectSummary(
        project_id="proj_003",
        total_cost=Money(amount=195.0, currency="USD"),
        budget_total=Money(amount=200.0, currency="USD"),
        budget_compliance=BudgetCompliance(
            is_compliant=True,
            overrun_amount=0.0
        ),
        shots_count=10,
        duration=90.0,
        quality_tier="high",
        created_at=datetime.now() - timedelta(hours=4),
        completed_at=datetime.now()
    )
    
    metrics_collector.record_project_completion(
        project_id="proj_003",
        summary=summary_3,
        project_start_time=datetime.now() - timedelta(hours=4)
    )
    print("  ✓ 项目完成: 总成本 $195.00, 符合预算")
    
    # 获取指标摘要
    print("\n" + "=" * 60)
    print("指标摘要")
    print("=" * 60)
    
    summary = metrics_collector.get_metrics_summary()
    
    print(f"\n总项目数: {summary['total_projects']}")
    print(f"预算分配次数: {summary['total_budget_allocations']}")
    print(f"预算超支次数: {summary['total_cost_overruns']}")
    print(f"人工介入次数: {summary['total_human_interventions']}")
    print(f"项目完成次数: {summary['total_project_completions']}")
    print(f"决策延迟记录数: {summary['total_decision_latencies']}")
    
    print(f"\n预算超支率: {summary['cost_overrun_rate']:.1%}")
    print(f"人工介入率: {summary['human_intervention_rate']:.1%}")
    print(f"项目完成率: {summary['project_completion_rate']:.1%}")
    print(f"平均决策延迟: {summary['avg_decision_latency_ms']:.2f} ms")
    
    # 按决策类型统计延迟
    print("\n按决策类型统计延迟:")
    print(f"  - 预算分配: {metrics_collector.get_avg_decision_latency('budget_allocation'):.2f} ms")
    print(f"  - 失败评估: {metrics_collector.get_avg_decision_latency('failure_evaluation'):.2f} ms")
    
    print("\n" + "=" * 60)
    print("示例完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
