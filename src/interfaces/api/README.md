# VideoGen 后端 API 服务

FastAPI 后端服务，集成 LLM 和各种 AI 模型。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动服务器

```bash
python api_server.py
```

或使用 uvicorn：

```bash
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### 3. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端点

### 基础端点

- `GET /` - API 信息
- `GET /health` - 健康检查

### 视频生成流程

#### 1. 需求分析
```
POST /api/analyze-requirement
Body: {
  "project_id": "PROJ-xxx",
  "requirement": {
    "description": "视频需求描述",
    "duration": 30,
    "quality_tier": "STANDARD",
    "style": "modern"
  }
}
```

#### 2. 剧本生成
```
POST /api/generate-script
Body: {
  "project_id": "PROJ-xxx",
  "analysis": {...}
}
```

#### 3. 分镜生成
```
POST /api/generate-storyboard
Body: {
  "project_id": "PROJ-xxx",
  "script": {...}
}
```

#### 4. 图像生成
```
POST /api/generate-image
Body: {
  "project_id": "PROJ-xxx",
  "shot": 1
}
```

#### 5. 视频合成
```
POST /api/generate-video
Body: {
  "project_id": "PROJ-xxx",
  "images": [...]
}
```

## LLM 配置

当前使用 SophNet 的 DeepSeek-V3.2 模型。

### 环境变量配置（推荐）

创建 `.env` 文件：

```env
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://www.sophnet.com/api/open-apis/v1
LLM_MODEL=DeepSeek-V3.2
```

### 修改 API Key

在 `api_server.py` 中修改（不推荐硬编码）：

```python
llm_client = OpenAI(
    api_key="your_api_key",
    base_url="https://www.sophnet.com/api/open-apis/v1"
)
```

## 集成其他 AI 模型

### 图像生成模型

可集成：
- SDXL (Stability AI)
- DALL-E 3 (OpenAI)
- Midjourney
- Flux

### 视频生成模型

可集成：
- Runway Gen-3
- Pika
- Sora
- Veo

## 开发

### 测试 API

```bash
# 使用 curl
curl -X POST "http://localhost:8000/api/analyze-requirement" \
  -H "Content-Type: application/json" \
  -d '{"project_id": "TEST-001", "requirement": {...}}'

# 使用 Python requests
import requests

response = requests.post(
    "http://localhost:8000/api/analyze-requirement",
    json={
        "project_id": "TEST-001",
        "requirement": {
            "description": "测试视频",
            "duration": 30,
            "quality_tier": "STANDARD",
            "style": "modern"
        }
    }
)

print(response.json())
```

### 添加新端点

```python
@app.post("/api/your-endpoint")
async def your_endpoint(data: YourModel):
    # 处理逻辑
    return {"success": True}
```

## 部署

### 生产环境

```bash
# 使用 gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# 使用 Docker
docker build -t videogen-api .
docker run -p 8000:8000 videogen-api
```

### Nginx 反向代理

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 注意事项

⚠️ **API Key 安全**: 不要将 API Key 提交到代码仓库
⚠️ **CORS 配置**: 生产环境应限制允许的域名
⚠️ **速率限制**: 建议添加请求速率限制
⚠️ **错误处理**: 完善错误处理和日志记录

## License

MIT
