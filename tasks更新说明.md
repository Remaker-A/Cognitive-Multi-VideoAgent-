# Tasks.md 更新说明

## 更新概述

基于进一步优化方案，在 tasks.md 中新增了 ImageEditAgent 和 ErrorCorrectionAgent 相关的实施任务。

## 更新内容

### 新增 Phase 4 任务（ErrorCorrectionAgent）

**任务 22-24**: ErrorCorrectionAgent 实现
- **任务 22**: 错误检测能力（姿态、手部、面部、物理、文字）
- **任务 23**: 智能修复策略（4 层修复机制）
- **任务 24**: 用户错误标注功能（UI 集成）
- **任务 24.1**: 单元测试（可选）

**工期**: 增加 1 周，Phase 4 从 3 周变为 4 周

### 新增 Phase 5（图像编辑功能）

**任务 25-28**: ImageEditAgent 实现
- **任务 25**: 基础功能（编辑请求处理、质量评估、历史管理）
- **任务 26**: 编辑模型 Adapter（Qwen-Image-Edit、ControlNet、InstructPix2Pix）
- **任务 27**: 功能集成（UI、审批流程）
- **任务 28**: DNA 一致性保持
- **任务 28.1**: 单元测试（可选）

**工期**: 新增 3 周

### 原有 Phase 调整

- **Phase 5** → **Phase 6**: Editor 与最终输出（任务 29-31）
- **Phase 6** → **Phase 7**: 用户审批与监控（任务 32-38）
- **Phase 7** → **Phase 8**: 集成测试与优化（任务 39-41）
- **Phase 8** → **Phase 9**: 高级 Adapter（任务 42-44）
- **Phase 9** → **Phase 10**: UI 与用户体验（任务 45-48）
- **Phase 10** → **Phase 11**: 文档与部署（任务 49-51）

## 任务总数变化

| 项目 | 原计划 | 新计划 | 变化 |
|------|--------|--------|------|
| 主任务数 | 44 | 51 | +7 |
| Phase 数 | 10 | 11 | +1 |
| 预计工期 | 28 周 | 32 周 | +4 周 |

## 新增任务详情

### ErrorCorrectionAgent 任务组

**任务 22: 实现 ErrorCorrectionAgent - 错误检测**
```
- 实现人物姿态检测（OpenPose 集成）
- 实现手部质量检测（手指数量、形态）
- 实现面部质量检测（五官、表情）
- 实现物理规律违背检测
- 实现文字错误检测
- 实现错误严重程度分级
```
- Requirements: 13.1, 13.2, 13.3
- Design: Components > 13. ErrorCorrectionAgent（detect_errors）

**任务 23: 实现 ErrorCorrectionAgent - 智能修复**
```
- 实现 Level 1 局部 inpainting 修复
- 实现 Level 2 ControlNet 控制重生成
- 实现 Level 3 完全重新生成
- 实现 Level 4 人工介入触发
- 实现修复效果验证
- 实现修复策略选择逻辑
```
- Requirements: 13.4, 13.5, 13.6, 13.7
- Design: Components > 13. ErrorCorrectionAgent（correct_error）

**任务 24: 实现用户错误标注功能**
```
- 实现错误标注 UI（圈选区域）
- 实现错误类型选择界面
- 实现错误描述输入
- 实现标注数据模型（ErrorAnnotation）
- 集成到用户审批流程
```
- Requirements: 13.4, 13.8, 13.9
- Design: Components > 13. ErrorCorrectionAgent（handle_user_error_report）

### ImageEditAgent 任务组

**任务 25: 实现 ImageEditAgent 基础功能**
```
- 定义 ImageEditAgent 接口
- 实现编辑请求处理逻辑
- 实现编辑质量评估
- 实现编辑历史管理
- 实现 IMAGE_EDITED 事件发布
```
- Requirements: 12.1, 12.6, 12.7, 12.9
- Design: Components > 12. ImageEditAgent

**任务 26: 集成图像编辑模型 Adapter**
```
- 实现 QwenImageEditAdapter（视角调整）
- 实现 ControlNetInpaintAdapter（局部修复）
- 实现 InstructPix2PixAdapter（通用编辑）
- 实现 Adapter 选择逻辑
- 实现编辑参数优化
```
- Requirements: 12.2, 12.3, 12.10
- Design: Components > 12. ImageEditAgent（select_adapter）

**任务 27: 实现编辑功能集成**
```
- 在用户审批界面添加"编辑"按钮
- 实现编辑指令输入界面
- 实现编辑预览功能
- 实现编辑撤销功能
- 集成到 Orchestrator 审批流程
```
- Requirements: 12.4, 12.5, 12.7
- Design: Components > 12. ImageEditAgent, Components > 13. Orchestrator

**任务 28: 实现 DNA 一致性保持**
```
- 实现编辑时的 DNA token 注入
- 实现编辑后的特征验证
- 实现身份一致性检测
- 实现不一致时的自动调整
```
- Requirements: 12.5, 12.8
- Design: Components > 12. ImageEditAgent（preserve_identity）

## 工期影响分析

### 总工期变化

- **原计划**: 28 周（约 6.5 个月）
- **新计划**: 32 周（约 7.5 个月）
- **增加**: 4 周（约 1 个月）

### 各 Phase 工期

| Phase | 名称 | 原工期 | 新工期 | 变化 |
|-------|------|--------|--------|------|
| 1 | 核心基础设施 | 4 周 | 4 周 | - |
| 2 | 核心 Agent | 4 周 | 4 周 | - |
| 3 | 生成 Agent | 4 周 | 4 周 | - |
| 4 | QA 与一致性 | 3 周 | 4 周 | +1 周 |
| 5 | 图像编辑 | - | 3 周 | +3 周（新增）|
| 6 | Editor 输出 | 2 周 | 2 周 | - |
| 7 | 审批与监控 | 3 周 | 3 周 | - |
| 8 | 集成测试 | 3 周 | 3 周 | - |
| 9 | 高级 Adapter | 2 周 | 2 周 | - |
| 10 | UI 体验 | 3 周 | 3 周 | - |
| 11 | 文档部署 | 2 周 | 2 周 | - |

### MVP 交付时间

**原 MVP 计划**: 19 周（Phase 1-6）  
**新 MVP 计划**: 23 周（Phase 1-7，包含错误检测和图像编辑）

**建议**: 可以将图像编辑功能作为 MVP 后的第一个迭代，保持 MVP 在 20 周内交付。

## 优先级建议

### P0（MVP 必须）

- ✅ Phase 1-3: 核心基础设施和 Agent
- ✅ Phase 4: QA 与一致性（包含 ErrorCorrectionAgent）
- ✅ Phase 6: Editor 与输出
- ✅ Phase 7: 用户审批

**工期**: 20 周

### P1（MVP 后第一迭代）

- 🔄 Phase 5: 图像编辑功能
- 🔄 Phase 8: 集成测试优化
- 🔄 Phase 9: 高级 Adapter

**工期**: +8 周

### P2（后续迭代）

- 📋 Phase 10: UI 优化
- 📋 Phase 11: 文档完善

**工期**: +5 周

## 成本影响

### 开发成本

- **新增开发工时**: 约 4 周 × 团队规模
- **预计增加成本**: 根据团队规模计算

### 运营成本

**ErrorCorrectionAgent**:
- 错误检测: $0.001/次
- Inpainting 修复: $0.02/次
- 预计节省: 减少 60-80% 重新生成成本

**ImageEditAgent**:
- 图像编辑: $0.01-0.05/次
- 预计节省: 比完全重新生成节省 60-80%

**ROI**: 预计 3-6 个月回本

## 技术依赖

### 新增依赖

**ErrorCorrectionAgent**:
- OpenPose（姿态检测）
- Hand Detection Model（手部检测）
- Face Quality Assessment（面部检测）

**ImageEditAgent**:
- Qwen-Image-Edit API
- ControlNet Inpaint
- InstructPix2Pix

### 集成复杂度

- **低**: ErrorCorrectionAgent 检测功能
- **中**: ErrorCorrectionAgent 修复功能
- **中**: ImageEditAgent 基础编辑
- **高**: DNA 一致性保持

## 风险评估

### 技术风险

1. **编辑模型质量**: Qwen-Image-Edit 等模型可能不稳定
   - 缓解: 准备多个备选模型

2. **检测准确率**: 错误检测可能有误报或漏报
   - 缓解: 持续优化，用户反馈学习

3. **修复效果**: 自动修复可能破坏一致性
   - 缓解: 严格质量验证，保留原图

### 进度风险

1. **工期延长**: 增加 4 周可能影响上线时间
   - 缓解: 分阶段交付，MVP 不包含图像编辑

2. **资源不足**: 需要更多开发资源
   - 缓解: 优先级排序，外包部分工作

## 下一步行动

### 立即行动

1. ✅ 更新项目计划和时间表
2. ✅ 评估团队资源需求
3. ✅ 确定 MVP 范围（是否包含图像编辑）
4. ✅ 开始技术验证（测试编辑模型和检测模型）

### 短期行动（1 周内）

1. 🔄 与产品团队确认优先级
2. 🔄 与技术团队评估可行性
3. 🔄 更新预算和资源计划
4. 🔄 开始原型开发

### 中期行动（1 个月内）

1. 📋 完成 ErrorCorrectionAgent 原型
2. 📋 完成 ImageEditAgent 原型
3. 📋 内部测试和反馈
4. 📋 优化和迭代

---

**更新完成日期**: 2025-11-16  
**文档版本**: v3.1  
**下次更新**: 根据技术验证结果调整
