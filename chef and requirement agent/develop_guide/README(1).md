# 开发规范文档总览

> LivingAgentPipeline 项目完整开发规范体系

---

## 📚 文档导航

本目录包含 LivingAgentPipeline 项目的完整开发规范文档，帮助团队成员遵循统一的开发标准，实现高效的协作开发。

### 核心文档

| 文档 | 用途 | 适用人群 |
|-----|------|---------|
| [📘 开发规范](./DEVELOPMENT_STANDARDS.md) | 完整的开发规范，涵盖契约、代码、测试等 | 所有开发人员 |
| [✅ 代码审查清单](./CODE_REVIEW_CHECKLIST.md) | Code Review 时的检查要点 | Reviewer 和 Author |
| [🚀 快速上手指南](./QUICK_START_GUIDE.md) | 新人快速上手教程 | 新加入的开发人员 |
| [📁 Agent 模板](./AGENT_TEMPLATE/) | Agent 开发模板代码 | Agent 开发人员 |

---

## 🎯 快速开始

### 我是新人，从哪里开始？

1. **第一步**：阅读 [快速上手指南](./QUICK_START_GUIDE.md)
   - 5 分钟快速开始
   - 开发你的第一个 Agent
   - 常见问题解答

2. **第二步**：浏览 [开发规范](./DEVELOPMENT_STANDARDS.md)
   - 了解契约优先开发流程
   - 学习 Agent 开发规范
   - 掌握代码风格标准

3. **第三步**：使用 [Agent 模板](./AGENT_TEMPLATE/)
   - 复制模板代码
   - 根据需求修改
   - 运行测试验证

### 我要开发新 Agent，怎么做？

```bash
# 1. 复制 Agent 模板
cp -r AGENT_TEMPLATE src/agents/my_agent

# 2. 替换占位符
# 将 {AgentName} 替换为你的 Agent 名称，如 ImageGeneratorAgent

# 3. 实现业务逻辑
# 编辑 src/agents/my_agent/agent.py

# 4. 编写测试
# 编辑 src/agents/my_agent/test_agent.py

# 5. 运行测试
pytest src/agents/my_agent/test_agent.py -v --cov

# 6. 提交代码
git add src/agents/my_agent
git commit -m "feat(agent): add MyAgent"
```

### 我要提交 Pull Request，需要检查什么？

使用 [代码审查清单](./CODE_REVIEW_CHECKLIST.md) 自查：

- ✅ 契约合规性检查
- ✅ 代码质量检查（类型注解、风格、命名）
- ✅ 测试完整性检查（覆盖率 > 80%）
- ✅ 错误处理检查
- ✅ 文档完整性检查

---

## 📖 核心概念速查

### 契约优先 (Contract First)

```
先定义契约 → 生成类型 → 编写代码
```

**为什么？**
- 类型安全
- 自动验证
- 多语言支持

**怎么做？**
1. 在 `contracts/` 定义 JSON Schema
2. 生成 TypeScript 类型和 Pydantic 模型
3. 使用模型编写业务代码

### Event vs Task

| 特性 | Event | Task |
|-----|-------|------|
| 含义 | 某事已发生 | 需要做某事 |
| 命名 | `IMAGE_GENERATED` | `GENERATE_IMAGE` |
| 发送者 | Agent | Orchestrator |
| 接收者 | 所有订阅者 | 特定 Agent |

### Agent 开发三要素

1. **订阅事件**：定义 Agent 关心哪些事件
2. **处理逻辑**：实现 `handle_event()` 方法
3. **发布结果**：完成后发布事件通知其他 Agent

### 三层错误恢复

```
Level 1 (90%) → 自动重试
Level 2 (9%)  → 模型切换/降级
Level 3 (1%)  → 人工介入
```

---

## 🛠️ 开发工具链

### 必需工具

```bash
# 代码格式化
black src/ tests/ --line-length 100

# 代码检查
flake8 src/ tests/ --max-line-length 100

# 类型检查
mypy src/ --strict

# 测试
pytest tests/ -v --cov=src
```

### 推荐的 VS Code 扩展

- Python
- Pylance
- Black Formatter
- Ruff

### Git 工作流

```bash
# 创建功能分支
git checkout -b feature/my-agent

# 提交代码（遵循 Conventional Commits）
git commit -m "feat(agent): implement MyAgent"

# 推送并创建 PR
git push origin feature/my-agent
```

---

## 📊 质量标准

### 代码质量

- ✅ 类型提示覆盖率：100%
- ✅ 测试覆盖率：≥ 80%
- ✅ 文档完整性：100%
- ✅ Black + Flake8 检查通过
- ✅ mypy 类型检查通过

### 性能标准

- 单 Shot 生成时间：< 5 分钟
- Event Bus 延迟：< 100ms
- Blackboard 读写延迟：< 50ms

### 成本控制

- 30 秒视频成本：< $100 (balanced)
- 成本估算误差：< 20%
- 预算超支率：< 5%

---

## 🎓 学习路径

### 第 1 周：基础知识

- [ ] 阅读[快速上手指南](./QUICK_START_GUIDE.md)
- [ ] 阅读[设计文档](../../文档/Kiro/VIdeoGen/LivingAgentPipeline_v2_Unified_Design.md)
- [ ] 运行 Event Bus 示例
- [ ] 理解契约优先架构

### 第 2 周：开发实践

- [ ] 阅读[开发规范](./DEVELOPMENT_STANDARDS.md)
- [ ] 使用模板创建简单 Agent
- [ ] 编写完整的单元测试
- [ ] 提交第一个 PR

### 第 3 周：深入理解

- [ ] 研究现有 Agent 代码
- [ ] 理解 Event Bus 实现
- [ ] 理解 Blackboard 设计
- [ ] 参与 Code Review

### 第 4 周：独立开发

- [ ] 独立开发完整 Agent
- [ ] 实现复杂业务逻辑
- [ ] 进行性能优化
- [ ] 协助其他团队成员

---

## 📁 目录结构

```
contracts/
├── README.md                    # 本文件
├── DEVELOPMENT_STANDARDS.md     # 开发规范（主文档）
├── CODE_REVIEW_CHECKLIST.md    # 代码审查清单
├── QUICK_START_GUIDE.md         # 快速上手指南
├── AGENT_TEMPLATE/              # Agent 开发模板
│   ├── agent.py                 # Agent 实现模板
│   ├── __init__.py              # 模块导出
│   ├── config.py                # 配置管理
│   ├── test_agent.py            # 测试模板
│   └── README.md                # Agent 文档模板
└── contracts/                   # JSON Schema 契约定义
    ├── 0_shared/                # 共享数据模型
    ├── 1_event/                 # Event 定义
    ├── 2_task/                  # Task 定义
    ├── 3_blackboard_api/        # Blackboard API
    └── 4_orchestrator_mapping/  # 编排器映射
```

---

## ❓ 常见问题

### Q: 为什么要契约优先？

**A**: 契约优先确保：
- 前后端类型一致
- 自动数据验证
- 清晰的接口定义
- 易于维护和演化

### Q: 测试覆盖率一定要 80% 吗？

**A**: 这是最低要求。关键路径必须 100% 覆盖，推荐整体 > 90%。

### Q: 如何平衡代码质量和开发速度？

**A**: 
- 使用模板快速起步
- 自动化工具保证质量（Black、mypy）
- Code Review 互相学习
- 重构而不是重写

### Q: Event 和 Task 有什么区别？

**A**: 
- **Event**：广播"已发生的事"，所有订阅者都收到
- **Task**：指派"要做的事"，只有被分配的 Agent 执行

### Q: 如何调试 Agent？

**A**:
1. 查看日志（`logger.debug()`, `logger.info()`）
2. 使用 VS Code 断点调试
3. 查看 Event Bus 的因果链
4. 检查 Blackboard 的数据状态

---

## 🔄 文档更新

### 版本历史

| 版本 | 日期 | 变更 |
|-----|------|------|
| 1.0 | 2025-12-26 | 初始版本，包含完整规范体系 |

### 贡献指南

发现文档问题或有改进建议？

1. 创建 Issue 描述问题
2. 或直接提交 PR 修改文档
3. 文档变更也需要 Code Review

---

## 📞 获取帮助

### 文档问题

- 查看项目 Wiki
- 在 Slack/Teams 频道提问
- 创建 GitHub Issue

### 技术问题

- 查看[开发规范](./DEVELOPMENT_STANDARDS.md)中的相关章节
- 参考现有代码实现
- 请教有经验的团队成员

### 紧急问题

- 联系架构团队
- 在 Slack 紧急频道发消息

---

## 🎯 下一步

- 开始阅读 → [快速上手指南](./QUICK_START_GUIDE.md)
- 深入学习 → [开发规范](./DEVELOPMENT_STANDARDS.md)
- 开始编码 → [Agent 模板](./AGENT_TEMPLATE/)
- 提交代码 → [代码审查清单](./CODE_REVIEW_CHECKLIST.md)

---

**让我们一起构建高质量的 LivingAgentPipeline 系统！** 🚀
