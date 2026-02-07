# ChefAgent 开发方案

## 概述

ChefAgent（总监 Agent）是 LivingAgentPipeline v2.0 系统的核心决策组件，负责项目总指挥、预算控制、质量把关和人工介入决策。

### 核心定位

- **角色**: 项目总监和决策中枢
- **层级**: L2 认知层的管理型 Agent
- **职责**: 全局协调、预算管理、异常处理、用户审批管理

## 核心职责

### 1. 项目初始化与预算分配

**功能描述**:
- 接收 `PROJECT_CREATED` 事件
- 根据项目规格分配初始预算
- 设定质量档位和成本策略

**输入**:
```json
{
  "event_type": "PROJECT_CREATED",
  "project_spec": {
    "duration": 30,
    "quality_tier": "balanced",
    "aspect_ratio": "9:16"
  }
}
```

**输出**:
```json
{
  "event_type": "BUDGET_ALLOCATED",
  "budget": {
    "total": 90.0,
    "breakdown": {
      "image_generation": 30.0,
      "video_generation": 45.0,
      "audio": 10.0,
      "qa_buffer": 5.0
    },
    "quality_multiplier": 1.0
  }
}
```

**核心逻辑**:
```python
def allocate_budget(self, project_spec):
    """根据项目规格分配预算"""
    base_budget = project_spec.duration * 3.0  # $3/秒基准
    
    quality_multiplier = {
        "high": 1.5,
        "balanced": 1.0,
        "fast": 0.6
    }
    
    total = base_budget * quality_multiplier[project_spec.quality_tier]
    
    return {
        "total": total,
        "breakdown": {
            "image_generation": total * 0.33,
            "video_generation": total * 0.50,
            "audio": total * 0.11,
            "qa_buffer": total * 0.06
        }
    }
```

---

### 2. 预算监控与动态调整

**功能描述**:
- 实时监控预算使用情况
- 当预算使用超过 80% 时触发策略调整
- 预测最终成本并提前预警

**监控指标**:
```python
class BudgetMonitor:
    def check_budget_health(self, project_id):
        """检查预算健康度"""
        project = self.blackboard.get_project(project_id)
        budget = project.budget
        
        usage_rate = budget.used / budget.total
        
        if usage_rate > 0.8:
            return {
                "status": "WARNING",
                "action": "REDUCE_QUALITY",
                "suggestion": "切换到快速模型"
            }
        elif usage_rate > 0.95:
            return {
                "status": "CRITICAL",
                "action": "FORCE_DOWNGRADE",
                "suggestion": "降级到最低成本模型"
            }
        
        return {"status": "HEALTHY"}
```

**动态策略调整**:
```python
def adjust_strategy(self, budget_status):
    """动态调整项目策略"""
    if budget_status.used / budget_status.total > 0.8:
        return {
            "action": "REDUCE_QUALITY",
            "params": {
                "switch_to": "fast_models",
                "reduce_qa_iterations": True,
                "skip_optional_features": ["music_generation"]
            }
        }
    
    if budget_status.predicted_final > budget_status.total * 1.1:
        return {
            "action": "HUMAN_GATE",
            "reason": "预算预计超支 10%+"
        }
    
    return {"action": "CONTINUE"}
```

---

### 3. 质量异常处理与升级决策

**功能描述**:
- 监听 `CONSISTENCY_FAILED` 事件
- 评估是否需要人工介入
- 管理三层错误恢复策略

**输入事件**:
- `CONSISTENCY_FAILED`: QA 检测失败
- `COST_OVERRUN_WARNING`: 成本超支预警
- `RETRY_EXHAUSTED`: Agent 重试次数用尽

**升级决策矩阵**:
```python
def evaluate_escalation(self, failure_report):
    """评估是否需要人工介入"""
    # 重试次数过多
    if failure_report.retry_count >= 3:
        return "HUMAN_GATE"
    
    # 成本影响过大
    if failure_report.cost_impact > 20.0:
        return "HUMAN_GATE"
    
    # 关键质量指标失败
    if failure_report.severity == "critical":
        return "HUMAN_GATE"
    
    # DNA 置信度过低
    if failure_report.get("dna_confidence", 1.0) < 0.55:
        return "HUMAN_GATE"
    
    # 可以自动重试
    return "AUTO_RETRY"
```

---

### 4. 人工审批流程管理

**功能描述**:
- 管理用户审批检查点
- 处理审批请求和用户决策
- 暂停/恢复项目执行

**审批检查点**:
```python
APPROVAL_CHECKPOINTS = [
    "SCENE_WRITTEN",         # 剧本完成
    "SHOT_PLANNED",          # 分镜规划完成
    "PREVIEW_VIDEO_READY",   # 预览视频完成
    "FINAL_VIDEO_READY"      # 最终视频完成
]
```

**审批请求处理**:
```python
def request_approval(self, stage, content):
    """请求用户审批"""
    approval_request = {
        "approval_id": f"APPR-{uuid.uuid4()}",
        "stage": stage,
        "content": content,
        "options": ["approve", "revise", "reject"],
        "timeout_minutes": 60
    }
    
    # 写入 Blackboard
    self.blackboard.create_approval_request(approval_request)
    
    # 发布审批事件
    self.event_bus.publish(Event(
        type="USER_APPROVAL_REQUIRED",
        payload=approval_request
    ))
    
    # 暂停项目
    self.pause_project_execution()
    
    return approval_request
```

**用户决策处理**:
```python
def handle_user_decision(self, decision):
    """处理用户决策"""
    if decision.decision == "approve":
        self.resume_project_execution()
        
    elif decision.decision == "revise":
        # 创建修订任务
        self.create_revision_task(
            decision.original_stage,
            decision.revision_notes
        )
        
    elif decision.decision == "reject":
        # 重新执行原任务
        self.retry_original_task(decision.original_stage)
```

---

### 5. 项目熔断与终止

**功能描述**:
- 监控项目健康度
- 触发熔断机制
- 管理项目终止流程

**熔断触发条件**:
```python
def check_circuit_breaker(self, project_id):
    """检查是否需要熔断"""
    project = self.blackboard.get_project(project_id)
    
    # 预算严重超支
    if project.budget.used > project.budget.total * 1.2:
        return {
            "action": "FORCE_ABORT",
            "reason": "预算超支 20%+"
        }
    
    # 连续失败次数过多
    error_count = len([
        e for e in project.error_log 
        if e.severity == "critical"
    ])
    if error_count >= 5:
        return {
            "action": "FORCE_ABORT",
            "reason": "连续 5 次关键错误"
        }
    
    # 关键 Agent 不响应
    if self.check_agent_timeout(project_id):
        return {
            "action": "FORCE_ABORT",
            "reason": "Agent 超时无响应"
        }
    
    return {"action": "CONTINUE"}
```

---

## 接口设计

### 输入事件

| 事件类型 | 说明 | 处理方法 |
|---------|------|---------|
| `PROJECT_CREATED` | 项目创建 | `handle_project_created()` |
| `CONSISTENCY_FAILED` | QA 检测失败 | `handle_consistency_failure()` |
| `COST_OVERRUN_WARNING` | 成本预警 | `handle_cost_warning()` |
| `HUMAN_APPROVAL_REQUEST` | 人工审批请求 | `handle_approval_request()` |
| `USER_APPROVED` | 用户批准 | `handle_user_approved()` |
| `USER_REVISION_REQUESTED` | 用户请求修改 | `handle_user_revision()` |
| `USER_REJECTED` | 用户拒绝 | `handle_user_rejected()` |
| `TASK_TIMEOUT` | 任务超时 | `handle_task_timeout()` |

### 输出事件

| 事件类型 | 说明 | 触发条件 |
|---------|------|---------|
| `BUDGET_ALLOCATED` | 预算分配完成 | 项目初始化 |
| `STRATEGY_UPDATE` | 策略更新 | 预算压力触发 |
| `FORCE_ABORT` | 强制终止 | 熔断条件满足 |
| `HUMAN_GATE_TRIGGERED` | 触发人工介入 | 自动恢复失败 |
| `PROJECT_PAUSED` | 项目暂停 | 等待用户审批 |
| `PROJECT_RESUMED` | 项目恢复 | 用户批准继续 |

---

## 数据模型

### ChefAgentState
```typescript
interface ChefAgentState {
  project_id: string;
  current_strategy: Strategy;
  budget_health: BudgetHealth;
  pending_approvals: ApprovalRequest[];
  escalation_history: EscalationRecord[];
  circuit_breaker_status: CircuitBreakerStatus;
}

interface Strategy {
  quality_tier: "high" | "balanced" | "fast";
  cost_optimization: boolean;
  auto_mode: boolean;
  approval_checkpoints: string[];
}

interface BudgetHealth {
  usage_rate: number;
  predicted_final: number;
  status: "HEALTHY" | "WARNING" | "CRITICAL";
  last_check: string;
}

interface CircuitBreakerStatus {
  triggered: boolean;
  reason?: string;
  triggered_at?: string;
}
```

---

## 核心算法

### 1. 预算预测算法

```python
def predict_final_cost(self, project_id):
    """预测最终成本"""
    project = self.blackboard.get_project(project_id)
    
    # 已完成和进行中的 shots
    completed_shots = [s for s in project.shots.values() 
                       if s.status == "COMPLETED"]
    in_progress_shots = [s for s in project.shots.values() 
                         if s.status == "IN_PROGRESS"]
    pending_shots = [s for s in project.shots.values() 
                     if s.status == "INIT"]
    
    # 计算平均单 shot 成本
    if completed_shots:
        avg_cost_per_shot = sum(
            s.metadata.total_cost for s in completed_shots
        ) / len(completed_shots)
    else:
        # 使用预估值
        avg_cost_per_shot = project.budget.total / len(project.shots)
    
    # 预测剩余成本
    remaining_cost = (
        len(in_progress_shots) * avg_cost_per_shot * 0.8 +
        len(pending_shots) * avg_cost_per_shot
    )
    
    # 加上后期制作成本（10%）
    final_cost = project.budget.used + remaining_cost
    final_cost *= 1.1
    
    return {
        "predicted_final": final_cost,
        "confidence": min(len(completed_shots) / len(project.shots), 0.9)
    }
```

### 2. 质量-成本权衡决策

```python
def quality_cost_tradeoff(self, project_id, failure_report):
    """质量-成本权衡决策"""
    project = self.blackboard.get_project(project_id)
    budget_health = self.check_budget_health(project_id)
    
    # 预算充足，优先质量
    if budget_health.status == "HEALTHY":
        return {
            "action": "RETRY_HIGH_QUALITY",
            "model": "premium"
        }
    
    # 预算紧张，平衡质量和成本
    if budget_health.status == "WARNING":
        # 评估失败严重程度
        if failure_report.severity == "critical":
            return {
                "action": "RETRY_BALANCED",
                "model": "balanced"
            }
        else:
            return {
                "action": "ACCEPT_DEGRADED",
                "model": "fast"
            }
    
    # 预算危急，降级或终止
    if budget_health.status == "CRITICAL":
        if failure_report.is_critical:
            return {
                "action": "HUMAN_GATE",
                "reason": "预算不足无法保证质量"
            }
        else:
            return {
                "action": "ACCEPT_DEGRADED",
                "model": "fast"
            }
```

---

## 开发计划

### Phase 1: 核心功能（Week 1-2）

1. **预算管理模块**
   - 预算分配算法
   - 预算监控与预测
   - 成本统计与报告

2. **事件处理框架**
   - 事件订阅与分发
   - 事件处理器注册
   - 事件日志记录

3. **Blackboard 集成**
   - 读取项目状态
   - 更新策略配置
   - 管理锁机制

### Phase 2: 决策引擎（Week 3-4）

1. **升级决策模块**
   - 失败评估逻辑
   - 升级决策矩阵
   - 人工介入触发

2. **策略调整模块**
   - 质量-成本权衡算法
   - 动态策略更新
   - 模型选择建议

3. **熔断机制**
   - 健康度检查
   - 熔断条件判断
   - 项目终止流程

### Phase 3: 审批流程（Week 5-6）

1. **审批管理模块**
   - 审批请求创建
   - 用户决策处理
   - 项目暂停/恢复

2. **通知系统集成**
   - 审批通知发送
   - 超时提醒
   - 状态同步

### Phase 4: 监控与优化（Week 7-8）

1. **监控仪表板**
   - 实时预算监控
   - 项目进度追踪
   - 异常告警

2. **性能优化**
   - 决策延迟优化
   - 并发处理优化
   - 缓存策略

3. **测试与文档**
   - 单元测试
   - 集成测试
   - API 文档

---

## 验证方案

### 1. 单元测试

```python
def test_budget_allocation():
    """测试预算分配算法"""
    chef = ChefAgent()
    
    spec = {
        "duration": 30,
        "quality_tier": "balanced"
    }
    
    budget = chef.allocate_budget(spec)
    
    assert budget["total"] == 90.0
    assert budget["breakdown"]["video_generation"] == 45.0

def test_escalation_decision():
    """测试升级决策"""
    chef = ChefAgent()
    
    # 重试次数过多
    report = {"retry_count": 3}
    assert chef.evaluate_escalation(report) == "HUMAN_GATE"
    
    # 成本影响大
    report = {"retry_count": 1, "cost_impact": 25.0}
    assert chef.evaluate_escalation(report) == "HUMAN_GATE"
    
    # 可以自动重试
    report = {"retry_count": 1, "cost_impact": 5.0}
    assert chef.evaluate_escalation(report) == "AUTO_RETRY"
```

### 2. 集成测试

```python
async def test_approval_workflow():
    """测试审批流程"""
    chef = ChefAgent()
    
    # 1. 触发审批请求
    approval = chef.request_approval("SCENE_WRITTEN", {...})
    assert approval.status == "PENDING"
    
    # 2. 模拟用户批准
    decision = {
        "approval_id": approval.approval_id,
        "decision": "approve"
    }
    chef.handle_user_decision(decision)
    
    # 3. 验证项目恢复
    project = blackboard.get_project(project_id)
    assert project.status != "PAUSED"
```

### 3. 端到端测试

```python
async def test_full_project_with_budget_control():
    """测试完整项目的预算控制"""
    # 1. 创建项目，设置较低预算
    project = create_project(duration=30, budget=50.0)
    
    # 2. ChefAgent 自动调整策略
    await wait_for_event("STRATEGY_UPDATE")
    
    # 3. 验证使用了低成本模型
    project = blackboard.get_project(project.id)
    assert project.current_strategy.quality_tier == "fast"
    
    # 4. 验证最终成本在预算内
    await wait_for_completion()
    assert project.budget.used <= project.budget.total
```

---

## KPI 指标

### 业务指标

1. **成本控制**
   - `cost_overrun_rate`: 预算超支率 < 5%
   - `cost_prediction_accuracy`: 成本预测准确度 > 90%

2. **项目成功率**
   - `project_completion_rate`: 项目完成率 > 95%
   - `quality_satisfaction_rate`: 质量满意度 > 85%

3. **人工介入**
   - `human_intervention_rate`: 人工介入率 < 3%
   - `auto_recovery_rate`: 自动恢复成功率 > 90%

### 性能指标

1. **响应时间**
   - `avg_decision_latency`: 平均决策延迟 < 200ms
   - `approval_response_time`: 审批响应时间 < 100ms

2. **可靠性**
   - `uptime`: 可用性 > 99.9%
   - `error_rate`: 错误率 < 0.1%

---

## 技术栈

- **语言**: Python 3.11+
- **框架**: FastAPI (HTTP API)
- **事件总线**: Redis Streams / Kafka
- **存储**: PostgreSQL (状态) + Redis (缓存)
- **监控**: Prometheus + Grafana
- **日志**: Structured Logging (JSON)
- **测试**: pytest + pytest-asyncio

---

## 风险与挑战

### 技术风险

1. **并发控制**
   - 风险: 多个事件并发处理导致状态不一致
   - 缓解: 使用 Blackboard 锁机制

2. **决策延迟**
   - 风险: 决策过慢影响项目进度
   - 缓解: 优化决策算法，使用缓存

### 业务风险

1. **预算预测不准**
   - 风险: 预测偏差导致预算失控
   - 缓解: 增加预算 buffer，动态调整

2. **过度人工介入**
   - 风险: 频繁触发人工审批影响体验
   - 缓解: 优化升级决策阈值，提高自动恢复能力

---

## 总结

ChefAgent 是 LivingAgentPipeline v2.0 的核心管理组件，负责：

1. ✅ 预算分配与监控
2. ✅ 质量异常处理与升级决策
3. ✅ 用户审批流程管理
4. ✅ 项目熔断与终止
5. ✅ 全局策略动态调整

通过智能的预算控制和决策引擎，ChefAgent 确保项目在成本、质量和时间之间取得最佳平衡。
