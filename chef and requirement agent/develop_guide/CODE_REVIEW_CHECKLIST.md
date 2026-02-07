# Code Review 检查清单

> 在审查代码前，请使用此清单确保代码符合项目规范

---

## ✅ 契约合规性检查

### 数据模型

- [ ] 所有数据结构都使用 Pydantic 模型定义
- [ ] 模型定义与 JSON Schema 契约一致
- [ ] 所有必需字段都已包含
- [ ] 使用了正确的枚举类型（EventType, TaskType 等）
- [ ] 没有使用未定义的枚举值

### Event 和 Task

- [ ] Event 命名使用过去式（如 `IMAGE_GENERATED`）
- [ ] Task 命名使用动词原型（如 `GENERATE_IMAGE`）
- [ ] Event 包含完整的元数据（cost, latency_ms, causation_id）
- [ ] Task 包含必要的 input_data 和 assigned_to
- [ ] 因果链（causation_id）正确链接

### 契约验证

- [ ] 在边界处（API、事件发布）进行数据验证
- [ ] 使用 `create_event()`, `create_task()` 等辅助函数
- [ ] 没有手动构造字典绕过验证

---

## ✅ 代码质量检查

### 类型注解

- [ ] 所有函数都有完整的类型注解（参数和返回值）
- [ ] 类属性都有类型注解
- [ ] 使用了正确的 typing 类型（Dict, List, Optional 等）
- [ ] 没有使用 `any` 类型（除非确实必要）
- [ ] mypy 类型检查通过（`mypy src/ --strict`）

### 代码风格

- [ ] 代码已使用 Black 格式化（`black src/ tests/`）
- [ ] Flake8 检查通过（`flake8 src/ tests/`）
- [ ] 行长度 ≤ 100 字符
- [ ] 导入语句按照 stdlib → 第三方 → 本地的顺序组织
- [ ] 没有未使用的导入和变量

### 命名规范

- [ ] 类名使用 PascalCase（如 `ImageGeneratorAgent`）
- [ ] 函数/方法名使用 snake_case（如 `generate_keyframe`）
- [ ] 私有方法以下划线开头（如 `_validate_prompt`）
- [ ] 常量使用 UPPER_SNAKE_CASE（如 `MAX_RETRY_COUNT`）
- [ ] 变量名清晰且有意义（避免 `x`, `tmp` 等模糊名称）

### 文档字符串

- [ ] 所有公共类、函数都有文档字符串
- [ ] 使用 Google Style Docstrings 格式
- [ ] 包含 Args, Returns, Raises 说明（如适用）
- [ ] 复杂逻辑有行内注释说明

---

## ✅ Agent 开发规范检查

### 目录结构

- [ ] Agent 目录结构符合规范（agent.py, config.py, README.md, tests/）
- [ ] `__init__.py` 正确导出 Agent 类

### Agent 实现

- [ ] Agent 继承自 `EventSubscriber`
- [ ] 实现了 `handle_event()` 方法
- [ ] 在 `__init__()` 中正确订阅事件
- [ ] 订阅的事件类型与 Agent 职责相关
- [ ] 使用私有方法组织代码逻辑

### Event 处理

- [ ] Event 处理方法有完整的错误处理
- [ ] 失败时发布错误事件
- [ ] 成功时发布完成事件
- [ ] 不阻塞等待其他 Agent 的响应

### Blackboard 访问

- [ ] 使用 Blackboard RPC 接口访问数据
- [ ] 没有直接访问数据库
- [ ] 没有 Agent 间直接通信
- [ ] 正确使用锁机制（如需要）

---

## ✅ 测试完整性检查

### 单元测试

- [ ] 所有公共方法都有单元测试
- [ ] 测试覆盖率 ≥ 80%（理想 ≥ 90%）
- [ ] 使用 pytest 框架
- [ ] 使用 AAA 模式（Arrange-Act-Assert）
- [ ] Mock 了外部依赖（API、数据库等）

### 测试质量

- [ ] 测试名称清晰描述测试内容（如 `test_handle_event_success`）
- [ ] 包含正常情况和异常情况的测试
- [ ] 使用 `@pytest.mark.asyncio` 标记异步测试
- [ ] 使用 fixtures 管理测试数据
- [ ] 测试独立且可重复运行

### 测试运行

- [ ] 所有测试通过（`pytest tests/ -v`）
- [ ] 没有跳过的测试（除非有明确理由）
- [ ] 测试运行时间合理（< 1分钟）

---

## ✅ 错误处理检查

### 异常处理

- [ ] 所有可能失败的操作都有 try-except
- [ ] 异常处理具体且有意义（避免裸 `except:`）
- [ ] 记录异常详情（使用 `exc_info=True`）
- [ ] 错误信息包含足够的上下文

### 重试机制

- [ ] 实现了指数退避重试（如适用）
- [ ] 设置了合理的最大重试次数
- [ ] 记录重试日志
- [ ] 最终失败时发布错误事件

### 错误记录

- [ ] 错误记录到 Project.error_log
- [ ] 包含 causation_event_id 链接
- [ ] severity 级别合理
- [ ] 错误详情足够详细以便调试

---

## ✅ 性能和成本考虑

### 性能优化

- [ ] 独立的异步操作使用 `asyncio.gather()` 并发执行
- [ ] 避免 N+1 查询问题（使用批量查询）
- [ ] 大数据操作使用流式处理
- [ ] 没有不必要的阻塞操作

### 成本追踪

- [ ] Event 包含 cost 和 latency_ms 信息
- [ ] 成本估算准确
- [ ] 考虑了成本预算限制
- [ ] 使用了合适的质量档位模型

### 资源管理

- [ ] 正确关闭连接和文件句柄
- [ ] 使用 async with 管理异步资源
- [ ] 没有内存泄漏（如大对象未释放）

---

## ✅ 日志和监控

### 日志规范

- [ ] 关键操作有日志记录
- [ ] 日志级别使用正确（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- [ ] 日志信息包含足够的上下文
- [ ] 没有记录敏感信息（密钥、密码等）
- [ ] 使用结构化日志（extra 参数）

### 可追溯性

- [ ] Event 包含 causation_id 构建因果链
- [ ] Task 包含 causation_event_id
- [ ] 关键决策有记录（change_log）
- [ ] Artifact 有完整的元数据

---

## ✅ 安全性检查

### 输入验证

- [ ] 所有外部输入都经过验证
- [ ] 使用 Pydantic 自动验证
- [ ] 防止注入攻击（SQL、命令注入等）
- [ ] 文件路径经过验证和清理

### 敏感信息

- [ ] 密钥、密码不硬编码在代码中
- [ ] 使用环境变量或配置文件管理敏感信息
- [ ] 密钥不记录到日志
- [ ] 不在 git 中提交敏感信息

---

## ✅ 文档完整性

### 代码文档

- [ ] README.md 说明 Agent 的职责和用法
- [ ] 复杂算法有详细注释
- [ ] 公共 API 有使用示例

### 变更文档

- [ ] 重要变更记录在 change_log
- [ ] 破坏性变更有明确警告
- [ ] 迁移指南（如适用）

---

## ✅ Git 和协作

### Commit 质量

- [ ] Commit 消息符合 Conventional Commits 规范
- [ ] 每个 commit 是一个完整的逻辑单元
- [ ] Commit 消息清晰描述"为什么"而不仅仅是"做了什么"

### Pull Request

- [ ] PR 描述清晰完整
- [ ] 链接了相关 Issue
- [ ] 通过了 CI 检查
- [ ] 代码冲突已解决
- [ ] 分支名称符合规范（feature/, bugfix/ 等）

---

## 📊 Review 决策

### ✅ 批准条件

所有以下条件都满足：
- [ ] 所有强制检查项都通过
- [ ] 测试覆盖率 ≥ 80%
- [ ] 没有严重的性能或安全问题
- [ ] 文档完整且清晰

### 🔄 需要修改

- [ ] 列出具体需要修改的项目
- [ ] 提供改进建议
- [ ] 标注优先级（必须修改 vs 建议修改）

### ❌ 拒绝条件

- [ ] 违反核心架构原则
- [ ] 存在严重的安全漏洞
- [ ] 破坏现有功能且没有测试覆盖
- [ ] 代码质量极差且难以维护

---

## 💡 Review 最佳实践

### 作为 Reviewer

1. **及时响应**：在 24 小时内开始 review
2. **建设性反馈**：不仅指出问题，还提供解决建议
3. **保持友善**：记住是在 review 代码，不是 review 人
4. **关注重点**：优先关注架构、逻辑、安全，而不是纠结代码风格细节（工具已检查）

### 作为 Author

1. **自我 review**：提交 PR 前先自己过一遍检查清单
2. **小而频繁**：避免巨大的 PR（理想 < 500 行）
3. **响应及时**：快速回复 review 意见
4. **虚心接受**：把 review 意见当作学习机会

---

**检查清单版本**: 1.0  
**最后更新**: 2025-12-26

参考：[DEVELOPMENT_STANDARDS.md](file:///d:/下载/contracts/DEVELOPMENT_STANDARDS.md)
