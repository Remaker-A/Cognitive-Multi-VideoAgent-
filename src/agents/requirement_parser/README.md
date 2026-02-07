# RequirementParser Agent

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen.svg)](tests/)

## 概述

RequirementParser Agent 是 LivingAgentPipeline 系统中的入口层 Agent，负责解析用户的多模态输入（文本、图片、视频、音频）并生成标准化的 GlobalSpec 数据结构。

### 核心特性

- 🎯 **多模态输入处理**: 支持文本、图片、视频、音频等多种输入格式
- 🤖 **AI 驱动分析**: 集成 DeepSeek-V3.2 模型进行智能需求理解
- 📊 **置信度评估**: 自动评估解析结果质量，低置信度时触发人工审核
- 🔄 **三层错误恢复**: 自动重试、降级处理、人工介入的完整错误处理策略
- 📈 **全面监控**: 详细的日志记录和性能指标收集
- 🚀 **高性能**: 支持并发处理和批量操作

## 职责

- 接收和验证用户多模态输入
- 调用 DeepSeek-V3.2 模型进行智能分析
- 提取关键信息（标题、时长、角色、风格等）
- 生成标准化的 GlobalSpec
- 评估解析结果的置信度
- 发布 PROJECT_CREATED 事件

## 事件交互

### 订阅事件

| 事件类型 | 说明 | 触发条件 |
|---------|------|---------|
| `USER_INPUT_SUBMITTED` | 用户提交需求 | 用户通过UI提交输入 |

### 发布事件

| 事件类型 | 说明 | 发布时机 |
|---------|------|---------|
| `PROJECT_CREATED` | 项目创建成功 | GlobalSpec生成完成且置信度足够 |
| `HUMAN_CLARIFICATION_REQUIRED` | 需要人工澄清 | 置信度低于阈值 |
| `ERROR_OCCURRED` | 处理失败 | 发生错误 |

## Blackboard 数据访问

### 读取数据

- 无（作为入口Agent，不读取已有项目数据）

### 写入数据

- 写入新创建的 Project 数据（包含 GlobalSpec）
- 写入处理日志和成本信息

## 快速开始

### 安装

```bash
# 克隆仓库
git clone <repository-url>
cd <repository-name>

# 安装依赖
pip install -r requirements.txt
```

### 配置

1. 复制环境配置模板：
```bash
cp .env.template .env
```

2. 编辑 `.env` 文件，填写必需的配置项：
```env
# DeepSeek API 配置（必需）
REQ_PARSER_DEEPSEEK_API_KEY=your_api_key_here

# Event Bus 配置（必需）
REQ_PARSER_EVENT_BUS_URL=redis://localhost:6379

# Blackboard 配置（必需）
REQ_PARSER_BLACKBOARD_URL=http://localhost:8000
```

完整的配置选项请参考 [.env.template](.env.template) 文件。

### 运行

#### 方式 1: 直接运行

```bash
python -m src.agents.requirement_parser.agent
```

#### 方式 2: Docker 部署

```bash
# 使用部署脚本（推荐）
./deploy.sh  # Linux/Mac
deploy.bat   # Windows

# 或手动部署
docker-compose up -d
```

#### 方式 3: Kubernetes 部署

```bash
# 应用 Kubernetes 配置
kubectl apply -f k8s-deployment.yaml

# 检查部署状态
kubectl get pods -n requirement-parser
```

## 配置详解

### 环境变量

| 变量名 | 说明 | 默认值 | 必需 |
|-------|------|--------|------|
| `REQ_PARSER_DEEPSEEK_API_KEY` | DeepSeek API Key | - | ✅ |
| `REQ_PARSER_DEEPSEEK_API_ENDPOINT` | API 端点 | https://www.sophnet.com/api/open-apis/v1/chat/completions | ❌ |
| `REQ_PARSER_MAX_RETRIES` | 最大重试次数 | 3 | ❌ |
| `REQ_PARSER_TIMEOUT_SECONDS` | 超时时间（秒） | 30 | ❌ |
| `REQ_PARSER_CONFIDENCE_THRESHOLD` | 置信度阈值 | 0.6 | ❌ |
| `REQ_PARSER_DEFAULT_QUALITY_TIER` | 默认质量档位 | balanced | ❌ |
| `REQ_PARSER_DEFAULT_ASPECT_RATIO` | 默认宽高比 | 9:16 | ❌ |
| `REQ_PARSER_EVENT_BUS_URL` | Event Bus URL | redis://localhost:6379 | ✅ |
| `REQ_PARSER_BLACKBOARD_URL` | Blackboard URL | http://localhost:8000 | ✅ |

### 配置验证

Agent 启动时会自动验证配置的有效性。如果配置无效，会提供详细的错误信息和修复建议。

```python
from src.agents.requirement_parser.config import get_config

# 加载并验证配置
config = get_config(validate=True)
```

## 使用示例

### 基本用法

```python
import asyncio
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.requirement_parser.models import UserInputData

async def main():
    # 创建 Agent
    agent = RequirementParserAgent()
    
    # 准备用户输入
    user_input = UserInputData(
        text_description="一个年轻的探险家在神秘森林中寻找宝藏，时长30秒",
        reference_images=["s3://bucket/reference1.jpg"],
        user_preferences={"quality_tier": "balanced"}
    )
    
    # 处理输入
    result = await agent.process_user_input(user_input)
    
    if result.is_successful():
        print(f"GlobalSpec created: {result.global_spec.title}")
        print(f"Confidence: {result.confidence_report.overall_confidence}")
    else:
        print(f"Processing failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 自定义配置

```python
from src.agents.requirement_parser import RequirementParserAgent, RequirementParserConfig

# 创建自定义配置
config = RequirementParserConfig(
    agent_name="CustomRequirementParser",
    max_retries=5,
    timeout_seconds=60,
    confidence_threshold=0.7
)

# 创建 Agent
agent = RequirementParserAgent(config=config)
```

## 部署

### Docker 部署（推荐）

使用提供的部署脚本快速部署：

```bash
# Linux/Mac
chmod +x deploy.sh
./deploy.sh

# Windows
deploy.bat
```

或手动使用 Docker Compose:

```bash
# 构建并启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Kubernetes 部署

```bash
# 应用配置
kubectl apply -f k8s-deployment.yaml

# 检查部署状态
kubectl get pods -n requirement-parser

# 查看日志
kubectl logs -f deployment/requirement-parser -n requirement-parser
```

### 本地开发部署

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.template .env
# 编辑 .env 文件填写配置

# 运行 Agent
python -m src.agents.requirement_parser.agent
```

## 文档

- 📖 [API 文档](../../../API.md) - 完整的 API 参考
- 💡 [使用示例](../../../EXAMPLES.md) - 各种使用场景的代码示例
- 🚀 [快速开始指南](#快速开始) - 快速上手指南
- 🏗️ [设计文档](../../../.kiro/specs/requirement-parser-agent/design.md) - 架构和设计细节
- 📋 [需求文档](../../../.kiro/specs/requirement-parser-agent/requirements.md) - 功能需求说明

## 开发

### 项目结构

```
src/agents/requirement_parser/
├── agent.py                    # 主 Agent 类
├── config.py                   # 配置管理
├── models.py                   # 数据模型
├── deepseek_client.py          # DeepSeek API 客户端
├── input_manager.py            # 输入管理器
├── preprocessor.py             # 预处理器
├── multimodal_analyzer.py      # 多模态分析器
├── global_spec_generator.py    # GlobalSpec 生成器
├── confidence_evaluator.py     # 置信度评估器
├── event_manager.py            # 事件管理器
├── error_recovery.py           # 错误恢复
├── metrics_collector.py        # 指标收集器
├── logger.py                   # 日志配置
├── exceptions.py               # 异常定义
├── utils.py                    # 工具函数
└── tests/                      # 测试文件
    ├── test_agent.py
    ├── test_config.py
    ├── test_deepseek_client.py
    └── ...
```

### 运行测试

```bash
# 运行所有测试
pytest tests/unit/agents/requirement_parser/ -v

# 运行特定测试
pytest tests/unit/agents/requirement_parser/test_agent.py::TestRequirementParserAgent::test_process_user_input -v

# 查看覆盖率
pytest tests/unit/agents/requirement_parser/ --cov=src.agents.requirement_parser --cov-report=html
```

### 调试

```python
import logging

# 启用调试日志
logging.basicConfig(level=logging.DEBUG)

# 创建 Agent
agent = RequirementParserAgent()
```

## 性能指标

| 指标 | 目标值 | 当前值 |
|-----|-------|--------|
| 文本解析延迟 | < 2s | TBD |
| 图片分析延迟 | < 5s | TBD |
| 完整处理延迟 | < 30s | TBD |
| API 成功率 | > 95% | TBD |
| 置信度准确率 | > 85% | TBD |

## 错误处理

### 常见错误

#### 错误 1: DeepSeek API 连接失败

**症状**: API 调用超时或返回错误

**解决方案**:
1. 检查 API Key 是否正确
2. 验证网络连接
3. 检查 API 端点是否可访问
4. 查看 API 配额是否充足

#### 错误 2: 置信度过低

**症状**: 系统频繁触发人工澄清

**解决方案**:
1. 检查用户输入是否足够详细
2. 调整置信度阈值
3. 优化分析提示词
4. 增加参考资料

#### 错误 3: 文件处理失败

**症状**: 无法处理上传的文件

**解决方案**:
1. 检查文件格式是否支持
2. 验证文件大小是否超限
3. 确认文件 URL 可访问
4. 检查存储服务状态

### 重试策略

Agent 实现了三层错误恢复策略：

1. **Level 1**: 自动重试（最多 3 次）- 处理临时性错误
2. **Level 2**: 降级策略 - 仅处理文本输入或使用默认模板
3. **Level 3**: 人工介入 - 发布 HUMAN_GATE_TRIGGERED 事件

## 监控

### 日志

Agent 会记录以下结构化日志：

- `INFO`: 正常操作（输入接收、处理完成、事件发布）
- `WARNING`: 警告信息（重试、置信度低）
- `ERROR`: 错误信息（API失败、处理错误）
- `DEBUG`: 调试信息（详细的处理步骤）

### 指标

可以通过以下方式监控 Agent：

```python
# 查看处理统计
result = await agent.process_user_input(user_input)
print(f"Processing time: {result.processing_time}s")
print(f"Cost: ${result.cost}")
print(f"Confidence: {result.confidence_report.overall_confidence}")

# 查看错误日志
errors = project.error_log
```

## 贡献

在修改 RequirementParser Agent 时，请遵循以下规范：

1. 更新测试以覆盖新功能
2. 保持测试覆盖率 > 80%
3. 更新文档
4. 遵循代码风格指南（Black + Flake8）
5. 添加类型注解
6. 编写清晰的文档字符串

## 参考资料

- [开发规范](../../../develop_guide/DEVELOPMENT_STANDARDS.md)
- [设计文档](../../../.kiro/specs/requirement-parser-agent/design.md)
- [需求文档](../../../.kiro/specs/requirement-parser-agent/requirements.md)
- [任务列表](../../../.kiro/specs/requirement-parser-agent/tasks.md)

---

**最后更新**: 2025-12-27
**版本**: 1.0.0
**维护者**: LivingAgentPipeline Team