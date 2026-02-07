# RequirementParser Agent 部署指南

本文档提供了 RequirementParser Agent 的完整部署指南，包括多种部署方式和最佳实践。

## 目录

- [前置要求](#前置要求)
- [配置准备](#配置准备)
- [部署方式](#部署方式)
  - [Docker 部署](#docker-部署推荐)
  - [Kubernetes 部署](#kubernetes-部署)
  - [本地开发部署](#本地开发部署)
- [验证部署](#验证部署)
- [常见问题](#常见问题)
- [监控和维护](#监控和维护)

## 前置要求

### 硬件要求

- **CPU**: 最少 2 核，推荐 4 核
- **内存**: 最少 2GB，推荐 4GB
- **磁盘**: 最少 10GB 可用空间

### 软件要求

根据部署方式不同，需要以下软件：

#### Docker 部署
- Docker 20.10+
- Docker Compose 1.29+

#### Kubernetes 部署
- Kubernetes 1.20+
- kubectl 命令行工具
- Helm 3.0+ (可选)

#### 本地开发部署
- Python 3.9+
- pip 21.0+
- Redis 6.0+ (用于 Event Bus)

### 外部服务

- **DeepSeek API**: 需要有效的 API Key
- **Redis**: 用作 Event Bus (可使用 Docker 部署)
- **Blackboard 服务**: 项目数据存储服务

## 配置准备

### 1. 获取 DeepSeek API Key

访问 [DeepSeek 官网](https://www.deepseek.com) 申请 API Key。

### 2. 创建配置文件

```bash
# 复制配置模板
cp .env.template .env

# 编辑配置文件
nano .env  # 或使用其他编辑器
```

### 3. 填写必需配置

在 `.env` 文件中填写以下必需配置：

```env
# DeepSeek API 配置（必需）
REQ_PARSER_DEEPSEEK_API_KEY=your_api_key_here

# Event Bus 配置（必需）
REQ_PARSER_EVENT_BUS_URL=redis://localhost:6379

# Blackboard 配置（必需）
REQ_PARSER_BLACKBOARD_URL=http://localhost:8000
```

### 4. 配置验证

使用以下命令验证配置：

```bash
python -c "from src.agents.requirement_parser.config import get_config; config = get_config(validate=True); print('配置验证通过')"
```

## 部署方式

### Docker 部署（推荐）

Docker 部署是最简单和推荐的部署方式。

#### 使用部署脚本

**Linux/Mac**:
```bash
# 赋予执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

**Windows**:
```cmd
deploy.bat
```

部署脚本会自动：
1. 检查 Docker 和 Docker Compose
2. 验证配置文件
3. 构建 Docker 镜像
4. 启动服务
5. 检查健康状态

#### 手动部署

如果需要更多控制，可以手动执行：

```bash
# 1. 构建镜像
docker-compose build

# 2. 启动服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f

# 4. 检查状态
docker-compose ps
```

#### 常用 Docker 命令

```bash
# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看特定服务日志
docker-compose logs -f requirement-parser

# 进入容器
docker-compose exec requirement-parser bash

# 更新服务
docker-compose pull
docker-compose up -d
```

### Kubernetes 部署

适用于生产环境的大规模部署。

#### 准备工作

1. 确保 Kubernetes 集群可用
2. 配置 kubectl 连接到集群
3. 创建命名空间（可选）

#### 部署步骤

```bash
# 1. 创建 Secret（存储敏感信息）
kubectl create secret generic requirement-parser-secrets \
  --from-literal=REQ_PARSER_DEEPSEEK_API_KEY=your_api_key_here \
  -n requirement-parser

# 2. 应用配置
kubectl apply -f k8s-deployment.yaml

# 3. 检查部署状态
kubectl get pods -n requirement-parser

# 4. 查看日志
kubectl logs -f deployment/requirement-parser -n requirement-parser

# 5. 检查服务
kubectl get svc -n requirement-parser
```

#### 扩缩容

```bash
# 手动扩容
kubectl scale deployment requirement-parser --replicas=5 -n requirement-parser

# 查看 HPA 状态（自动扩缩容）
kubectl get hpa -n requirement-parser
```

#### 更新部署

```bash
# 更新镜像
kubectl set image deployment/requirement-parser \
  requirement-parser=requirement-parser:new-version \
  -n requirement-parser

# 查看滚动更新状态
kubectl rollout status deployment/requirement-parser -n requirement-parser

# 回滚
kubectl rollout undo deployment/requirement-parser -n requirement-parser
```

### 本地开发部署

适用于开发和测试环境。

#### 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 启动 Redis

```bash
# 使用 Docker 启动 Redis
docker run -d -p 6379:6379 --name redis redis:7-alpine

# 或使用本地 Redis
redis-server
```

#### 运行 Agent

```bash
# 方式 1: 直接运行
python -m src.agents.requirement_parser.agent

# 方式 2: 使用 Python 脚本
python -c "
import asyncio
from src.agents.requirement_parser import RequirementParserAgent

async def main():
    agent = RequirementParserAgent()
    # 处理逻辑...
    await agent.close()

asyncio.run(main())
"
```

## 验证部署

### 健康检查

#### Docker 部署

```bash
# 检查容器状态
docker-compose ps

# 检查健康状态
docker inspect requirement-parser-agent | grep -A 5 Health
```

#### Kubernetes 部署

```bash
# 检查 Pod 状态
kubectl get pods -n requirement-parser

# 检查健康探针
kubectl describe pod <pod-name> -n requirement-parser
```

### 功能测试

创建测试脚本 `test_deployment.py`:

```python
import asyncio
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.requirement_parser.models import UserInputData

async def test_deployment():
    """测试部署是否成功"""
    
    try:
        async with RequirementParserAgent() as agent:
            user_input = UserInputData(
                text_description="测试视频项目"
            )
            
            result = await agent.process_user_input(user_input)
            
            if result.is_successful():
                print("✅ 部署验证成功!")
                print(f"项目标题: {result.global_spec.title}")
                print(f"置信度: {result.confidence_report.overall_confidence:.2f}")
                return True
            else:
                print(f"❌ 处理失败: {result.error_message}")
                return False
    
    except Exception as e:
        print(f"❌ 部署验证失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_deployment())
    exit(0 if success else 1)
```

运行测试：

```bash
python test_deployment.py
```

## 常见问题

### 问题 1: API Key 无效

**症状**: 启动时报错 "DeepSeek API Key is required"

**解决方案**:
1. 检查 `.env` 文件中的 `REQ_PARSER_DEEPSEEK_API_KEY` 是否正确
2. 确认 API Key 没有过期
3. 验证 API Key 有足够的配额

### 问题 2: Redis 连接失败

**症状**: 日志显示 "Connection refused" 或 "Redis connection failed"

**解决方案**:
1. 确认 Redis 服务正在运行
2. 检查 `REQ_PARSER_EVENT_BUS_URL` 配置是否正确
3. 验证网络连接和防火墙设置

### 问题 3: 内存不足

**症状**: 容器频繁重启或 OOM (Out of Memory)

**解决方案**:
1. 增加容器内存限制（docker-compose.yml 或 k8s-deployment.yaml）
2. 减少并发请求数 (`REQ_PARSER_MAX_CONCURRENT_REQUESTS`)
3. 优化批处理大小 (`REQ_PARSER_BATCH_SIZE`)

### 问题 4: 处理超时

**症状**: 请求经常超时

**解决方案**:
1. 增加超时时间 (`REQ_PARSER_TIMEOUT_SECONDS`)
2. 检查网络延迟
3. 优化 DeepSeek API 调用参数

### 问题 5: 置信度过低

**症状**: 频繁触发人工澄清

**解决方案**:
1. 调整置信度阈值 (`REQ_PARSER_CONFIDENCE_THRESHOLD`)
2. 改进用户输入质量
3. 优化分析提示词

## 监控和维护

### 日志管理

#### Docker 部署

```bash
# 查看实时日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100

# 导出日志到文件
docker-compose logs > logs.txt
```

#### Kubernetes 部署

```bash
# 查看实时日志
kubectl logs -f deployment/requirement-parser -n requirement-parser

# 查看所有 Pod 日志
kubectl logs -l app=requirement-parser -n requirement-parser

# 导出日志
kubectl logs deployment/requirement-parser -n requirement-parser > logs.txt
```

### 性能监控

#### 指标收集

Agent 会自动收集以下指标：
- API 调用延迟和成本
- 处理时间和输入大小
- 置信度分布
- 错误类型和频率

#### 查看指标

```python
from src.agents.requirement_parser.metrics_collector import global_metrics_collector

# 获取 API 调用指标
api_metrics = global_metrics_collector.api_metrics
print(f"总调用次数: {len(api_metrics)}")

# 获取处理指标
processing_metrics = global_metrics_collector.processing_metrics
print(f"总处理次数: {len(processing_metrics)}")

# 获取错误指标
error_metrics = global_metrics_collector.error_metrics
print(f"总错误次数: {len(error_metrics)}")
```

### 备份和恢复

#### 配置备份

```bash
# 备份配置文件
cp .env .env.backup.$(date +%Y%m%d)

# 备份 Kubernetes 配置
kubectl get all -n requirement-parser -o yaml > backup.yaml
```

#### Redis 数据备份

```bash
# Docker 部署
docker-compose exec redis redis-cli SAVE
docker cp requirement-parser-redis:/data/dump.rdb ./backup/

# Kubernetes 部署
kubectl exec -it redis-0 -n requirement-parser -- redis-cli SAVE
kubectl cp requirement-parser/redis-0:/data/dump.rdb ./backup/dump.rdb
```

### 更新和升级

#### Docker 部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 重启服务
docker-compose down
docker-compose up -d
```

#### Kubernetes 部署

```bash
# 1. 更新镜像
docker build -t requirement-parser:v1.1.0 .
docker push requirement-parser:v1.1.0

# 2. 更新部署
kubectl set image deployment/requirement-parser \
  requirement-parser=requirement-parser:v1.1.0 \
  -n requirement-parser

# 3. 监控滚动更新
kubectl rollout status deployment/requirement-parser -n requirement-parser
```

### 安全最佳实践

1. **保护敏感信息**
   - 不要将 `.env` 文件提交到版本控制
   - 使用 Kubernetes Secrets 存储敏感配置
   - 定期轮换 API Key

2. **网络安全**
   - 使用 HTTPS 连接外部服务
   - 配置防火墙规则
   - 限制容器网络访问

3. **访问控制**
   - 使用非 root 用户运行容器
   - 配置 RBAC (Kubernetes)
   - 限制 API 访问权限

4. **日志安全**
   - 脱敏敏感信息
   - 限制日志访问权限
   - 定期清理旧日志

## 生产环境检查清单

部署到生产环境前，请确认以下事项：

- [ ] 所有必需配置已正确填写
- [ ] API Key 有效且配额充足
- [ ] Redis 服务稳定运行
- [ ] 资源限制已合理配置
- [ ] 健康检查正常工作
- [ ] 日志收集已配置
- [ ] 监控告警已设置
- [ ] 备份策略已制定
- [ ] 安全措施已实施
- [ ] 文档已更新

## 支持

如需帮助，请参考：
- [README](README.md) - 项目概述
- [API 文档](API.md) - API 参考
- [使用示例](EXAMPLES.md) - 代码示例
- [设计文档](.kiro/specs/requirement-parser-agent/design.md) - 架构设计

或联系技术支持：
- 邮箱: support@example.com
- 问题追踪: [GitHub Issues](https://github.com/example/issues)
