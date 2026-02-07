# ChefAgent Admin CLI Tool

Admin CLI 工具用于在开发环境中模拟人工决策，测试 ChefAgent 的人工介入流程。

## 功能

- **approve**: 批准项目并恢复执行
- **reject**: 拒绝项目并标记为失败
- **revise**: 请求修订项目
- **list**: 列出所有待审批项目
- **status**: 显示项目详细状态

## 安装

确保已安装项目依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

### 批准项目

```bash
python tools/admin_cli.py approve <project_id> [--notes "approval notes"] [--user "username"]
```

示例：
```bash
python tools/admin_cli.py approve proj_123 --notes "Looks good, approved"
```

### 拒绝项目

```bash
python tools/admin_cli.py reject <project_id> [--notes "rejection reason"] [--user "username"]
```

示例：
```bash
python tools/admin_cli.py reject proj_123 --notes "Quality issues detected"
```

### 请求修订

```bash
python tools/admin_cli.py revise <project_id> --notes "revision instructions" [--user "username"]
```

示例：
```bash
python tools/admin_cli.py revise proj_123 --notes "Please improve audio quality"
```

### 列出待审批项目

```bash
python tools/admin_cli.py list
```

输出示例：
```
=== Pending Projects ===

Project ID: proj_test_001
  Reason: Max retries exceeded
  Created: 2025-12-27T14:52:51.979520
  Budget: $85.00 / $100.00 (85.0%)
```

### 查看项目详情

```bash
python tools/admin_cli.py status <project_id>
```

输出示例：
```
=== Project Status: proj_test_001 ===

Reason for Review: Max retries exceeded
Created At: 2025-12-27T14:53:00.750136

Budget Information:
  Total Budget: $100.00 USD
  Spent: $85.00 USD
  Remaining: $15.00 USD
  Usage Rate: 85.0%

Context Information:
  error_type: APIError
  retry_count: 3
  last_error: API timeout after 30s
```

## 帮助信息

查看所有可用命令：

```bash
python tools/admin_cli.py --help
```

查看特定命令的帮助：

```bash
python tools/admin_cli.py approve --help
python tools/admin_cli.py reject --help
python tools/admin_cli.py revise --help
```

## 测试

运行测试脚本验证 CLI 工具功能：

```bash
python tools/test_admin_cli.py
```

## 架构说明

Admin CLI 工具通过发布用户决策事件与 ChefAgent 通信：

1. **approve** → 发布 `USER_APPROVED` 事件
2. **reject** → 发布 `USER_REJECTED` 事件
3. **revise** → 发布 `USER_REVISION_REQUESTED` 事件

这些事件会被 ChefAgent 订阅并处理，从而恢复或终止项目执行。

## 开发环境使用

在没有 Web 前端的开发环境中，Admin CLI 工具提供了完整的人工决策功能：

1. ChefAgent 触发 `HUMAN_GATE_TRIGGERED` 事件
2. 开发者使用 `list` 命令查看待审批项目
3. 开发者使用 `status` 命令查看项目详情
4. 开发者使用 `approve`/`reject`/`revise` 命令做出决策
5. ChefAgent 接收决策事件并继续处理

## Requirements 映射

- **11.1**: 提供 Admin CLI 工具用于模拟人工决策
- **11.2**: 实现 `approve` 命令发布 USER_APPROVED 事件
- **11.3**: 实现 `reject` 命令发布 USER_REJECTED 事件
- **11.4**: 实现 `revise` 命令发布 USER_REVISION_REQUESTED 事件
- **11.5**: 实现 `list` 命令显示待审批项目列表
- **11.6**: 实现 `status` 命令显示项目预算使用情况和失败原因
