<div align="center">

# 🎬 VideoGen - AI Video Generation Pipeline

**An Event-Driven Multi-Agent System for Automated Video Production**

[English](#english) | [中文](#chinese)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Vue 3](https://img.shields.io/badge/Vue-3.0+-brightgreen.svg)](https://vuejs.org/)

### 🎥 Demo Video

https://github.com/user-attachments/assets/demo.mov

*Watch VideoGen in action: From text prompt to final video in minutes*

</div>

---

<a name="english"></a>

## 🚀 Overview

**VideoGen** (LivingAgentPipeline v2.0) is an enterprise-grade AI video generation system that orchestrates 14 specialized AI agents to automate the entire video production workflow - from script writing to final video delivery.

### ✨ Key Features

- 🎯 **Event-Driven Architecture**: Loosely coupled agents communicate via Redis Streams
- 🧠 **14 Specialized Agents**: Each agent handles a specific domain (scriptwriting, storyboarding, image generation, etc.)
- 🎨 **DNA Bank System**: Ensures visual consistency of characters across multiple shots
- 📊 **Shared Blackboard**: Single source of truth for project state (PostgreSQL + Redis + S3)
- 🔄 **Smart Orchestrator**: Intelligent task scheduling with budget control and user approval gates
- 🎭 **Multi-Model Support**: Integrates with OpenAI, Anthropic, SDXL, Runway, and more
- 💰 **Budget Management**: Real-time cost tracking and prediction
- 🔍 **Quality Assurance**: Automated QA with CLIP similarity, temporal coherence, and optical flow analysis

### 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│         L1: Interaction Layer (交互层)                   │
│         RequirementParser Agent                          │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│      L2: Cognitive Multi-Agent Layer (认知层)            │
│  14 Specialized Agents Working in Harmony                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│   L3: Infrastructure & Model Runtime (基础设施层)        │
│  Event Bus | Blackboard | Storage | Model Router        │
└─────────────────────────────────────────────────────────┘
```

### 🎬 Production Workflow

```
User Input → Script Writing → Storyboarding → Prompt Engineering
    ↓
Image Generation → Video Generation → Quality Check → User Approval
    ↓
Final Video Delivery
```

---

## 📦 Quick Start

### Prerequisites

- Python 3.9+
- Docker & Docker Compose
- Node.js 16+ (for frontend)
- 8GB+ RAM recommended

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/videogen.git
cd videogen
```

### 2. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: API_KEY, IMAGE_API_KEY, VIDEO_API_KEY
```

### 3. Start Infrastructure Services

```bash
# Start PostgreSQL, Redis, MinIO, Qdrant
docker-compose up -d

# Wait for services to be ready
docker-compose ps
```

### 4. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
# Run database migrations
python scripts/init_blackboard.sh

# Verify setup
python scripts/verify_blackboard.py
```

### 6. Start Backend Server

```bash
# Start FastAPI server
python src/main.py

# Server runs on http://localhost:8000
```

### 7. Start Frontend (Optional)

```bash
cd web-new
npm install
npm run dev

# Frontend runs on http://localhost:5173
```

### 8. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (admin/minioadmin)

For detailed setup instructions, see [QUICKSTART.md](QUICKSTART.md)

---

## 🧩 Core Components

### 14 Specialized Agents

| Agent | Role | Key Responsibilities |
|-------|------|---------------------|
| **ChefAgent** | Orchestrator | Coordinates overall workflow |
| **StoryArchitect** | Story Designer | Designs overall story structure |
| **BibleArchitect** | World Builder | Maintains setting consistency |
| **Showrunner** | Producer | Manages project progress |
| **EpisodeWriter** | Episode Writer | Writes episode scripts |
| **ScriptWriter** | Scriptwriter | Generates detailed scripts |
| **ShotDirector** | Cinematographer | Plans camera shots and angles |
| **PromptEngineer** | Prompt Specialist | Crafts optimized prompts |
| **ArtDirector** | Art Director | Manages visual style |
| **ImageGen** | Image Generator | Generates keyframe images |
| **VideoGen** | Video Generator | Produces video clips |
| **ConsistencyGuardian** | QA Specialist | Ensures quality standards |
| **PhysicsLogicChecker** | Logic Validator | Checks physical plausibility |
| **ErrorCorrection** | Error Handler | Handles failures and retries |

### Infrastructure Services

- **Event Bus**: Redis Streams-based pub/sub system
- **Shared Blackboard**: PostgreSQL + Redis + S3 storage
- **Orchestrator**: Task scheduling and dependency management
- **Storage Service**: S3/MinIO artifact management
- **Model Router**: Multi-model load balancing
- **DNA Bank**: Character consistency via face embeddings (Qdrant)

---

## 🛠️ Tech Stack

### Backend
- **Python 3.9+**: Core language
- **FastAPI**: Web framework
- **PostgreSQL 14**: Primary database
- **Redis 7**: Message queue & cache
- **MinIO/S3**: Object storage
- **Qdrant**: Vector database

### AI/ML
- **PyTorch**: Deep learning
- **Transformers**: NLP models
- **OpenAI API**: GPT models
- **Anthropic Claude**: LLM service
- **SDXL**: Image generation
- **Runway**: Video generation
- **CLIP**: Image-text similarity

### Frontend
- **Vue 3**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS 4**: Styling
- **Pinia**: State management

---

## 📚 Documentation

- [Quick Start Guide](QUICKSTART.md) - Detailed setup instructions
- [Contributing Guide](CONTRIBUTING.md) - How to contribute
- [API Documentation](http://localhost:8000/docs) - Interactive API docs
- [Architecture Design](docs/architecture.md) - System design details

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with modern event-driven architecture principles
- Inspired by multi-agent systems research
- Powered by cutting-edge AI models

---

## 📧 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/videogen/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/videogen/discussions)

---

<a name="chinese"></a>

# 🎬 VideoGen - AI 视频生成流水线

**基于事件驱动的多智能体视频制作系统**

---

## 🚀 项目简介

**VideoGen**（LivingAgentPipeline v2.0）是一个企业级 AI 视频生成系统，通过编排 14 个专业 AI 智能体，实现从剧本创作到最终视频交付的全流程自动化。

### ✨ 核心特性

- 🎯 **事件驱动架构**：智能体通过 Redis Streams 松耦合通信
- 🧠 **14 个专业智能体**：每个智能体负责特定领域（编剧、分镜、图像生成等）
- 🎨 **DNA Bank 系统**：确保角色在多个镜头中的视觉一致性
- 📊 **共享黑板**：单一事实来源的项目状态管理（PostgreSQL + Redis + S3）
- 🔄 **智能编排器**：智能任务调度，支持预算控制和用户审批
- 🎭 **多模型支持**：集成 OpenAI、Anthropic、SDXL、Runway 等
- 💰 **预算管理**：实时成本追踪和预测
- 🔍 **质量保证**：自动化 QA，包括 CLIP 相似度、时间连贯性、光流分析

### 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│              L1: 交互层 (Interaction Layer)              │
│              需求解析智能体                               │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│         L2: 认知层 (Cognitive Multi-Agent Layer)         │
│              14 个专业智能体协同工作                       │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│    L3: 基础设施层 (Infrastructure & Model Runtime)       │
│    事件总线 | 共享黑板 | 存储服务 | 模型路由              │
└─────────────────────────────────────────────────────────┘
```

### 🎬 制作流程

```
用户输入 → 剧本创作 → 分镜规划 → Prompt 工程
    ↓
图像生成 → 视频生成 → 质量检查 → 用户审批
    ↓
最终视频交付
```

---

## 📦 快速开始

### 环境要求

- Python 3.9+
- Docker & Docker Compose
- Node.js 16+（前端）
- 推荐 8GB+ 内存

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/videogen.git
cd videogen
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，添加你的 API 密钥
# 必需：API_KEY, IMAGE_API_KEY, VIDEO_API_KEY
```

### 3. 启动基础设施服务

```bash
# 启动 PostgreSQL, Redis, MinIO, Qdrant
docker-compose up -d

# 等待服务就绪
docker-compose ps
```

### 4. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 5. 初始化数据库

```bash
# 运行数据库迁移
python scripts/init_blackboard.sh

# 验证设置
python scripts/verify_blackboard.py
```

### 6. 启动后端服务

```bash
# 启动 FastAPI 服务器
python src/main.py

# 服务运行在 http://localhost:8000
```

### 7. 启动前端（可选）

```bash
cd web-new
npm install
npm run dev

# 前端运行在 http://localhost:5173
```

### 8. 访问应用

- **前端界面**：http://localhost:5173
- **API 文档**：http://localhost:8000/docs
- **MinIO 控制台**：http://localhost:9001 (admin/minioadmin)

详细设置说明请参考 [QUICKSTART.md](QUICKSTART.md)

---

## 🧩 核心组件

### 14 个专业智能体

| 智能体 | 角色 | 主要职责 |
|-------|------|---------|
| **ChefAgent** | 总指挥 | 协调整体工作流程 |
| **StoryArchitect** | 故事架构师 | 设计整体故事结构 |
| **BibleArchitect** | 世界观构建师 | 维护设定一致性 |
| **Showrunner** | 制片人 | 管理项目进度 |
| **EpisodeWriter** | 剧集编剧 | 编写剧集脚本 |
| **ScriptWriter** | 剧本编剧 | 生成详细剧本 |
| **ShotDirector** | 分镜导演 | 规划镜头和角度 |
| **PromptEngineer** | Prompt 工程师 | 优化生成提示词 |
| **ArtDirector** | 艺术指导 | 管理视觉风格 |
| **ImageGen** | 图像生成器 | 生成关键帧图像 |
| **VideoGen** | 视频生成器 | 制作视频片段 |
| **ConsistencyGuardian** | 质量守护者 | 确保质量标准 |
| **PhysicsLogicChecker** | 逻辑验证器 | 检查物理合理性 |
| **ErrorCorrection** | 错误修正器 | 处理失败和重试 |

### 基础设施服务

- **事件总线**：基于 Redis Streams 的发布/订阅系统
- **共享黑板**：PostgreSQL + Redis + S3 存储
- **编排器**：任务调度和依赖管理
- **存储服务**：S3/MinIO 资源管理
- **模型路由**：多模型负载均衡
- **DNA Bank**：通过人脸嵌入（Qdrant）保证角色一致性

---

## 🛠️ 技术栈

### 后端
- **Python 3.9+**：核心语言
- **FastAPI**：Web 框架
- **PostgreSQL 14**：主数据库
- **Redis 7**：消息队列和缓存
- **MinIO/S3**：对象存储
- **Qdrant**：向量数据库

### AI/ML
- **PyTorch**：深度学习框架
- **Transformers**：NLP 模型
- **OpenAI API**：GPT 模型
- **Anthropic Claude**：LLM 服务
- **SDXL**：图像生成
- **Runway**：视频生成
- **CLIP**：图像-文本相似度

### 前端
- **Vue 3**：UI 框架
- **TypeScript**：类型安全
- **Vite**：构建工具
- **Tailwind CSS 4**：样式框架
- **Pinia**：状态管理

---

## 📚 文档

- [快速启动指南](QUICKSTART.md) - 详细设置说明
- [贡献指南](CONTRIBUTING.md) - 如何贡献代码
- [API 文档](http://localhost:8000/docs) - 交互式 API 文档
- [架构设计](docs/architecture.md) - 系统设计细节

---

## 🤝 贡献

我们欢迎贡献！详情请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- 基于现代事件驱动架构原则构建
- 受多智能体系统研究启发
- 由前沿 AI 模型驱动

---

## 📧 联系方式

- **问题反馈**：[GitHub Issues](https://github.com/yourusername/videogen/issues)
- **讨论交流**：[GitHub Discussions](https://github.com/yourusername/videogen/discussions)

---

<div align="center">

**Made with ❤️ by the VideoGen Team**

⭐ Star us on GitHub if you find this project useful!

</div>
