# Design Document

## Overview

ChefAgent 是 LivingAgentPipeline 系统的总监 Agent，负责项目全局决策和预算控制。作为系统的"大脑"，ChefAgent 协调整个视频生成流程，确保项目在预算范围内高质量完成。

### 核心职责

1. **预算管理**: 根据项目规格分配预算，实时监控预算使用情况
2. **策略调整**: 根据预算使用情况动态调整项目策略（如降低质量档位）
3. **失败评估**: 评估任务失败情况，决定是否需要人工介入
4. **人工决策处理**: 处理人工审批结果，恢复或终止项目
5. **项目完成确认**: 验证项目完成，进行成本核算和质量验收

### 设计原则

1. **事件驱动**: 通过订阅和发布事件与其他 Agent 通信，不直接调用
2. **预算优先**: 所有决策都考虑预算约束，避免成本失控
3. **渐进式降级**: 优先尝试自动恢复，必要时才触发人工介入
4. **可观测性**: 所有决策和状态变更都记录到 Blackboard 和日志

## Architecture

### 组件架构

```
┌─────────────────────────────────────────────────────────┐
│                      ChefAgent                          │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Budget       │  │ Strategy     │  │ Failure      │  │
│  │ Manager      │  │ Adjuster     │  │ Evaluator    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Human        │  │ Project      │  │ Metrics      │  │
│  │ Gate         │  │ Validator    │  │ Collector    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Event        │  │ Config       │                    │
│  │ Manager      │  │ Manager      │                    │
│  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────┘
           ↓                    ↓                    ↓
    ┌──────────┐        ┌──────────┐        ┌──────────┐
    │ Event    │        │ Shared   │        │ Metrics  │
    │ Bus      │        │Blackboard│        │ Store    │
    └──────────┘        └──────────┘        └──────────┘
```


## Components and Interfaces

### 1. BudgetManager（预算管理器）

**职责**: 预算分配、监控和预测

**核心方法**:

```python
class BudgetManager:
    def allocate_budget(self, global_spec: GlobalSpec) -> Budget:
        """
        根据项目规格分配预算
        
        公式: 
        - 基准预算 = duration * $3/秒
        - 质量乘数: high=1.5, balanced=1.0, fast=0.6
        - 总预算 = 基准预算 * 质量乘数
        
        Args:
            global_spec: 全局项目规格
            
        Returns:
            Budget: 预算对象
            
        Validates: Requirements 1.1, 1.2, 1.3, 1.4
        """
        base_budget = global_spec.duration * 3.0
        quality_multiplier = {
            "high": 1.5,
            "balanced": 1.0,
            "fast": 0.6
        }
        total = base_budget * quality_multiplier[global_spec.quality_tier]
        
        return Budget(
            total=Money(amount=total, currency="USD"),
            spent=Money(amount=0.0, currency="USD"),
            estimated_remaining=Money(amount=total, currency="USD")
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
        budget.spent.amount += cost.amount
        budget.estimated_remaining.amount = budget.total.amount - budget.spent.amount
        return budget
    
    def estimate_default_cost(self, event_type: EventType) -> Money:
        """
        估算默认成本（当事件不包含成本信息时）
        
        Args:
            event_type: 事件类型
            
        Returns:
            Money: 估算成本
            
        Validates: Requirements 2.2
        """
        default_costs = {
            EventType.IMAGE_GENERATED: 0.05,
            EventType.VIDEO_GENERATED: 0.50,  # 每秒
            EventType.MUSIC_COMPOSED: 0.02,   # 每秒
            EventType.VOICE_RENDERED: 0.02    # 每秒
        }
        amount = default_costs.get(event_type, 0.01)
        return Money(amount=amount, currency="USD")
    
    def check_budget_status(self, budget: Budget) -> BudgetStatus:
        """
        检查预算状态
        
        Returns:
            BudgetStatus: 预算状态（OK, WARNING, EXCEEDED）
            
        Validates: Requirements 2.3, 2.4
        """
        usage_rate = budget.spent.amount / budget.total.amount
        
        if usage_rate >= 1.0:
            return BudgetStatus.EXCEEDED
        elif usage_rate >= 0.8:
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
        if progress == 0:
            return budget.total
        
        predicted = budget.spent.amount / progress
        return Money(amount=predicted, currency="USD")
```


### 2. StrategyAdjuster（策略调整器）

**职责**: 根据预算状况动态调整项目策略

**核心方法**:

```python
class StrategyAdjuster:
    def evaluate_strategy(self, budget: Budget, global_spec: GlobalSpec) -> StrategyDecision:
        """
        评估是否需要调整策略
        
        Args:
            budget: 当前预算状态
            global_spec: 全局项目规格
            
        Returns:
            StrategyDecision: 策略决策
            
        Validates: Requirements 3.1, 3.4
        """
        usage_rate = budget.spent.amount / budget.total.amount
        
        if usage_rate >= 0.8:
            # 预算紧张，考虑降级
            return StrategyDecision(
                action="REDUCE_QUALITY",
                reason="Budget usage exceeds 80%",
                params={"target_tier": self._get_lower_tier(global_spec.quality_tier)}
            )
        elif usage_rate < 0.5:
            # 预算充足，维持当前策略
            return StrategyDecision(
                action="CONTINUE",
                reason="Budget is sufficient"
            )
        else:
            # 预算正常，维持当前策略
            return StrategyDecision(
                action="CONTINUE",
                reason="Budget usage is normal"
            )
    
    def _get_lower_tier(self, current_tier: str) -> str:
        """获取更低的质量档位"""
        tier_order = ["high", "balanced", "fast"]
        current_index = tier_order.index(current_tier)
        if current_index < len(tier_order) - 1:
            return tier_order[current_index + 1]
        return current_tier
    
    def apply_strategy(self, decision: StrategyDecision, global_spec: GlobalSpec) -> GlobalSpec:
        """
        应用策略调整
        
        Args:
            decision: 策略决策
            global_spec: 当前全局规格
            
        Returns:
            GlobalSpec: 更新后的全局规格
            
        Validates: Requirements 3.2, 3.3
        """
        if decision.action == "REDUCE_QUALITY":
            global_spec.quality_tier = decision.params["target_tier"]
        
        return global_spec
```


### 3. FailureEvaluator（失败评估器）

**职责**: 评估任务失败情况，决定恢复策略

**核心方法**:

```python
class FailureEvaluator:
    def evaluate_failure(self, failure_report: FailureReport) -> EscalationDecision:
        """
        评估失败情况，决定是否需要人工介入
        
        Args:
            failure_report: 失败报告
            
        Returns:
            EscalationDecision: 升级决策
            
        Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
        """
        # 检查重试次数
        if failure_report.retry_count >= 3:
            return EscalationDecision(
                action="HUMAN_GATE",
                reason="Max retries exceeded",
                priority="high"
            )
        
        # 检查成本影响
        if failure_report.cost_impact > 20.0:
            return EscalationDecision(
                action="HUMAN_GATE",
                reason="Cost impact exceeds $20",
                priority="high"
            )
        
        # 检查严重程度
        if failure_report.severity == "critical":
            return EscalationDecision(
                action="HUMAN_GATE",
                reason="Critical failure",
                priority="critical"
            )
        
        # 可自动恢复
        return EscalationDecision(
            action="AUTO_RETRY",
            reason="Failure is recoverable",
            priority="low"
        )
```


### 4. HumanGate（人工介入管理器）

**职责**: 管理人工介入流程

**核心方法**:

```python
class HumanGate:
    def trigger_human_intervention(
        self,
        project_id: str,
        reason: str,
        context: Dict[str, Any]
    ) -> HumanGateRequest:
        """
        触发人工介入
        
        Args:
            project_id: 项目 ID
            reason: 触发原因
            context: 上下文信息
            
        Returns:
            HumanGateRequest: 人工介入请求
            
        Validates: Requirements 4.6, 4.7
        """
        request = HumanGateRequest(
            request_id=generate_id(),
            project_id=project_id,
            reason=reason,
            context=context,
            status="PENDING",
            created_at=datetime.now(),
            timeout_minutes=60
        )
        
        return request
    
    def handle_user_decision(
        self,
        request: HumanGateRequest,
        decision: UserDecision
    ) -> ProjectAction:
        """
        处理用户决策
        
        Args:
            request: 人工介入请求
            decision: 用户决策
            
        Returns:
            ProjectAction: 项目操作
            
        Validates: Requirements 5.1, 5.2, 5.3
        """
        if decision.action == "approve":
            return ProjectAction(
                action="RESUME",
                reason="User approved"
            )
        elif decision.action == "revise":
            return ProjectAction(
                action="CREATE_REVISION_TASK",
                reason="User requested revision",
                params={"revision_notes": decision.notes}
            )
        elif decision.action == "reject":
            return ProjectAction(
                action="MARK_FAILED",
                reason="User rejected"
            )
    
    def check_timeout(self, request: HumanGateRequest) -> bool:
        """
        检查是否超时
        
        Args:
            request: 人工介入请求
            
        Returns:
            bool: 是否超时
            
        Validates: Requirements 5.4
        """
        elapsed = datetime.now() - request.created_at
        return elapsed.total_seconds() > request.timeout_minutes * 60
```


### 5. ProjectValidator（项目验证器）

**职责**: 验证项目完成状态

**核心方法**:

```python
class ProjectValidator:
    def validate_completion(self, project: Project) -> ValidationResult:
        """
        验证项目是否完成
        
        Args:
            project: 项目对象
            
        Returns:
            ValidationResult: 验证结果
            
        Validates: Requirements 6.1
        """
        incomplete_shots = [
            shot_id for shot_id, shot in project.shots.items()
            if shot.status != "FINAL_RENDERED"
        ]
        
        if incomplete_shots:
            return ValidationResult(
                is_valid=False,
                reason=f"Incomplete shots: {incomplete_shots}"
            )
        
        return ValidationResult(is_valid=True)
    
    def calculate_total_cost(self, project: Project) -> Money:
        """
        计算项目总成本
        
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
        
        Args:
            project: 项目对象
            
        Returns:
            BudgetCompliance: 预算合规性
            
        Validates: Requirements 6.3, 6.4
        """
        total_cost = self.calculate_total_cost(project)
        budget = project.budget
        
        if total_cost.amount <= budget.total.amount:
            return BudgetCompliance(
                is_compliant=True,
                overrun_amount=0.0
            )
        else:
            return BudgetCompliance(
                is_compliant=False,
                overrun_amount=total_cost.amount - budget.total.amount
            )
    
    def generate_summary_report(self, project: Project) -> ProjectSummary:
        """
        生成项目总结报告
        
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
            completed_at=datetime.now()
        )
```


## Data Models

### Budget（预算）

```python
from pydantic import BaseModel, Field

class Money(BaseModel):
    """货币金额"""
    amount: float = Field(..., ge=0, description="金额")
    currency: str = Field(default="USD", description="货币单位")

class Budget(BaseModel):
    """预算对象"""
    total: Money = Field(..., description="总预算")
    spent: Money = Field(..., description="已使用预算")
    estimated_remaining: Money = Field(..., description="预计剩余预算")
    breakdown: Dict[str, Money] = Field(default_factory=dict, description="成本分解")
```

### FailureReport（失败报告）

```python
class FailureReport(BaseModel):
    """失败报告"""
    task_id: str = Field(..., description="任务 ID")
    error_type: str = Field(..., description="错误类型")
    error_message: str = Field(..., description="错误消息")
    retry_count: int = Field(..., ge=0, description="重试次数")
    cost_impact: float = Field(..., ge=0, description="成本影响（美元）")
    severity: str = Field(..., description="严重程度: low, medium, high, critical")
    timestamp: datetime = Field(..., description="时间戳")
```

### EscalationDecision（升级决策）

```python
class EscalationDecision(BaseModel):
    """升级决策"""
    action: str = Field(..., description="操作: AUTO_RETRY, HUMAN_GATE")
    reason: str = Field(..., description="原因")
    priority: str = Field(..., description="优先级: low, medium, high, critical")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
```

### StrategyDecision（策略决策）

```python
class StrategyDecision(BaseModel):
    """策略决策"""
    action: str = Field(..., description="操作: CONTINUE, REDUCE_QUALITY, INCREASE_BUDGET")
    reason: str = Field(..., description="原因")
    params: Dict[str, Any] = Field(default_factory=dict, description="参数")
```

### HumanGateRequest（人工介入请求）

```python
class HumanGateRequest(BaseModel):
    """人工介入请求"""
    request_id: str = Field(..., description="请求 ID")
    project_id: str = Field(..., description="项目 ID")
    reason: str = Field(..., description="触发原因")
    context: Dict[str, Any] = Field(..., description="上下文信息")
    status: str = Field(..., description="状态: PENDING, APPROVED, REJECTED, TIMEOUT")
    created_at: datetime = Field(..., description="创建时间")
    timeout_minutes: int = Field(default=60, description="超时时间（分钟）")
    decision: Optional[UserDecision] = Field(None, description="用户决策")
```

### UserDecision（用户决策）

```python
class UserDecision(BaseModel):
    """用户决策"""
    action: str = Field(..., description="操作: approve, revise, reject")
    notes: Optional[str] = Field(None, description="备注")
    decided_at: datetime = Field(..., description="决策时间")
    decided_by: str = Field(..., description="决策人")
```

### ProjectSummary（项目总结）

```python
class ProjectSummary(BaseModel):
    """项目总结"""
    project_id: str = Field(..., description="项目 ID")
    total_cost: Money = Field(..., description="总成本")
    budget_total: Money = Field(..., description="预算总额")
    budget_compliance: BudgetCompliance = Field(..., description="预算合规性")
    shots_count: int = Field(..., description="镜头数量")
    duration: float = Field(..., description="视频时长（秒）")
    quality_tier: str = Field(..., description="质量档位")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: datetime = Field(..., description="完成时间")
```


## Correctness Properties

*属性（Property）是关于系统行为的通用规则，应该对所有有效输入都成立。属性是需求和实现之间的桥梁，通过属性基测试（Property-Based Testing）来验证系统的正确性。*

### Property 1: 预算分配一致性

*对于任何*项目规格，计算出的预算应该等于基准预算乘以对应质量档位的乘数。

**Validates: Requirements 1.1, 1.2, 1.3, 1.4**

### Property 2: 预算累加正确性

*对于任何*预算对象和成本序列，按顺序累加所有成本后，已使用预算应该等于所有成本之和。

**Validates: Requirements 2.1**

### Property 3: 默认成本估算一致性

*对于任何*不包含成本信息的事件，估算的成本应该与事件类型的默认成本表一致。

**Validates: Requirements 2.2**

### Property 4: 预算阈值触发正确性

*对于任何*预算状态，当使用率达到特定阈值时，应该触发相应的警告事件。

**Validates: Requirements 2.3, 2.4**

### Property 5: 策略调整决策正确性

*对于任何*预算状态和项目规格，当预算使用率超过 80% 时，应该决定降低质量档位；当使用率低于 50% 时，应该维持当前策略。

**Validates: Requirements 3.1, 3.4**

### Property 6: 质量档位降级正确性

*对于任何*质量档位，降级后的档位应该在质量顺序中位于原档位之后（high → balanced → fast）。

**Validates: Requirements 3.2, 3.3**

### Property 7: 失败升级决策正确性

*对于任何*失败报告，当重试次数达到 3 次、成本影响超过 $20 或严重程度为 critical 时，应该触发 HUMAN_GATE；否则应该返回 AUTO_RETRY。

**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 8: 人工决策处理正确性

*对于任何*人工介入请求和用户决策，应该根据决策类型（approve/revise/reject）返回相应的项目操作（RESUME/CREATE_REVISION_TASK/MARK_FAILED）。

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 9: 超时检测正确性

*对于任何*人工介入请求，当经过的时间超过超时时间时，应该返回 true；否则返回 false。

**Validates: Requirements 5.4**

### Property 10: 项目完成验证正确性

*对于任何*项目，当且仅当所有 shots 的状态都为 FINAL_RENDERED 时，验证应该通过。

**Validates: Requirements 6.1**

### Property 11: 成本计算正确性

*对于任何*项目，计算出的总成本应该等于所有 artifacts 成本之和。

**Validates: Requirements 6.2**

### Property 12: 预算合规性判断正确性

*对于任何*项目，当且仅当总成本不超过预算总额时，预算合规性应该为 true。

**Validates: Requirements 6.3, 6.4**

### Property 13: 事件因果链完整性

*对于任何*发布的事件，都应该包含 causation_id 字段（除非是起始事件）。

**Validates: Requirements 8.8**

### Property 14: 事件成本信息完整性

*对于任何*涉及成本的事件，都应该包含 cost 和 latency_ms 字段。

**Validates: Requirements 8.9**

### Property 15: 错误重试指数退避

*对于任何*可重试的错误，重试延迟应该遵循指数退避策略（delay = initial_delay * 2^retry_count）。

**Validates: Requirements 9.3**


## Error Handling

### 三层错误恢复策略

#### Level 1: 自动重试（90% 场景）

**触发条件**:
- 临时网络错误
- API 超时
- 可恢复的业务逻辑错误

**处理策略**:
```python
async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Any:
    """指数退避重试"""
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
            await asyncio.sleep(delay)
            delay *= 2  # 指数退避
```

#### Level 2: 策略降级（9% 场景）

**触发条件**:
- Level 1 重试失败
- 预算不足
- 质量要求可降低

**处理策略**:
```python
async def handle_with_fallback(self, error: Exception, context: Dict) -> Any:
    """降级处理"""
    if isinstance(error, BudgetExceededError):
        # 降低质量档位
        decision = self.strategy_adjuster.evaluate_strategy(
            budget=context["budget"],
            global_spec=context["global_spec"]
        )
        
        if decision.action == "REDUCE_QUALITY":
            # 应用降级策略
            await self.apply_strategy(decision)
            return await self.retry_with_lower_quality()
    
    # 无法降级，升级到 Level 3
    raise error
```

#### Level 3: 人工介入（1% 场景）

**触发条件**:
- Level 2 降级失败
- 关键质量指标不达标
- 成本影响超过阈值

**处理策略**:
```python
async def escalate_to_human(self, error: Exception, context: Dict) -> None:
    """升级到人工介入"""
    request = self.human_gate.trigger_human_intervention(
        project_id=context["project_id"],
        reason=str(error),
        context={
            "error_type": type(error).__name__,
            "error_message": str(error),
            "budget_status": context["budget"],
            "retry_count": context.get("retry_count", 0)
        }
    )
    
    # 发布 HUMAN_GATE_TRIGGERED 事件
    await self.event_manager.publish_human_gate_triggered(request)
    
    # 暂停项目
    await self.pause_project(context["project_id"])
```

### 错误日志记录

所有错误都应该记录到 Blackboard 的 error_log：

```python
error_entry = ErrorEntry(
    error_id=generate_id(),
    timestamp=datetime.now(),
    severity="error",
    source="ChefAgent",
    message=str(error),
    details={
        "error_type": type(error).__name__,
        "context": context
    },
    causation_event_id=event.event_id,
    resolved=False
)

project.error_log.append(error_entry)
await blackboard.update_project(project)
```


## Testing Strategy

### 双重测试方法

ChefAgent 的测试策略采用单元测试和属性基测试相结合的方式：

- **单元测试**: 验证特定示例、边界情况和错误条件
- **属性基测试**: 验证通用属性在所有输入下都成立

### 单元测试

**测试范围**: 核心组件的具体行为

**示例测试用例**:

```python
def test_allocate_budget_high_quality():
    """测试高质量档位的预算分配"""
    global_spec = GlobalSpec(
        duration=30,
        quality_tier="high"
    )
    
    budget_manager = BudgetManager()
    budget = budget_manager.allocate_budget(global_spec)
    
    # 30秒 * $3/秒 * 1.5 = $135
    assert budget.total.amount == 135.0
    assert budget.spent.amount == 0.0

def test_evaluate_failure_max_retries():
    """测试达到最大重试次数时触发人工介入"""
    failure_report = FailureReport(
        task_id="task_001",
        error_type="APIError",
        error_message="API timeout",
        retry_count=3,
        cost_impact=5.0,
        severity="medium",
        timestamp=datetime.now()
    )
    
    evaluator = FailureEvaluator()
    decision = evaluator.evaluate_failure(failure_report)
    
    assert decision.action == "HUMAN_GATE"
    assert decision.reason == "Max retries exceeded"
```

### 属性基测试

**测试范围**: 通用属性验证

**测试库**: Hypothesis（Python）

**配置**: 每个属性测试运行 100 次迭代

**示例测试用例**:

```python
from hypothesis import given, strategies as st

@given(
    duration=st.floats(min_value=1.0, max_value=300.0),
    quality_tier=st.sampled_from(["high", "balanced", "fast"])
)
def test_property_budget_allocation_consistency(duration, quality_tier):
    """
    Property 1: 预算分配一致性
    
    Feature: chef-agent, Property 1: 预算分配一致性
    Validates: Requirements 1.1, 1.2, 1.3, 1.4
    """
    global_spec = GlobalSpec(
        duration=duration,
        quality_tier=quality_tier
    )
    
    budget_manager = BudgetManager()
    budget = budget_manager.allocate_budget(global_spec)
    
    # 计算预期预算
    base_budget = duration * 3.0
    multipliers = {"high": 1.5, "balanced": 1.0, "fast": 0.6}
    expected = base_budget * multipliers[quality_tier]
    
    # 验证预算分配一致性
    assert abs(budget.total.amount - expected) < 0.01

@given(
    costs=st.lists(st.floats(min_value=0.0, max_value=100.0), min_size=1, max_size=20)
)
def test_property_budget_accumulation_correctness(costs):
    """
    Property 2: 预算累加正确性
    
    Feature: chef-agent, Property 2: 预算累加正确性
    Validates: Requirements 2.1
    """
    budget = Budget(
        total=Money(amount=1000.0, currency="USD"),
        spent=Money(amount=0.0, currency="USD"),
        estimated_remaining=Money(amount=1000.0, currency="USD")
    )
    
    budget_manager = BudgetManager()
    
    # 累加所有成本
    for cost in costs:
        budget = budget_manager.update_spent(
            budget,
            Money(amount=cost, currency="USD")
        )
    
    # 验证累加正确性
    expected_total = sum(costs)
    assert abs(budget.spent.amount - expected_total) < 0.01

@given(
    retry_count=st.integers(min_value=0, max_value=5),
    cost_impact=st.floats(min_value=0.0, max_value=50.0),
    severity=st.sampled_from(["low", "medium", "high", "critical"])
)
def test_property_failure_escalation_correctness(retry_count, cost_impact, severity):
    """
    Property 7: 失败升级决策正确性
    
    Feature: chef-agent, Property 7: 失败升级决策正确性
    Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5
    """
    failure_report = FailureReport(
        task_id="task_001",
        error_type="TestError",
        error_message="Test error",
        retry_count=retry_count,
        cost_impact=cost_impact,
        severity=severity,
        timestamp=datetime.now()
    )
    
    evaluator = FailureEvaluator()
    decision = evaluator.evaluate_failure(failure_report)
    
    # 验证升级决策正确性
    should_escalate = (
        retry_count >= 3 or
        cost_impact > 20.0 or
        severity == "critical"
    )
    
    if should_escalate:
        assert decision.action == "HUMAN_GATE"
    else:
        assert decision.action == "AUTO_RETRY"
```

### 集成测试

**测试范围**: Agent 间协作和事件流转

**示例测试用例**:

```python
@pytest.mark.asyncio
async def test_budget_warning_workflow():
    """测试预算预警工作流"""
    # 1. 创建项目
    project = create_test_project(budget=100.0)
    
    # 2. 模拟成本事件
    for i in range(10):
        event = Event(
            event_type=EventType.IMAGE_GENERATED,
            cost=Money(amount=9.0, currency="USD")
        )
        await chef_agent.handle_event(event)
    
    # 3. 验证预警事件被发布
    events = await event_bus.get_events(project.project_id)
    warning_events = [e for e in events if e.event_type == EventType.COST_OVERRUN_WARNING]
    
    assert len(warning_events) > 0
```

### 测试覆盖率目标

| 类型 | 最低要求 | 推荐目标 |
|-----|---------|---------|
| 单元测试覆盖率 | 80% | 90%+ |
| 属性基测试覆盖率 | 所有属性 | 所有属性 |
| 集成测试覆盖率 | 关键流程 | 所有流程 |

