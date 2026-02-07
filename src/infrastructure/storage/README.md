# Storage Service

Storage Service 是 LivingAgentPipeline v2.0 的对象存储层，负责 S3 兼容存储、artifact 管理、缓存复用和元数据管理。

## 核心特性

✅ **S3 兼容存储**: 支持 AWS S3 和 MinIO
✅ **Artifact 管理**: 完整的上传/下载/删除功能
✅ **Signed URL**: 生成临时访问 URL
✅ **缓存复用**: 基于生成参数的智能缓存
✅ **元数据管理**: 完整的 artifact 元数据存储

## 快速开始

### 1. 安装依赖

```bash
pip install boto3
```

### 2. 启动 MinIO

```bash
docker-compose up -d minio
```

### 3. 基础使用

```python
from src.infrastructure.storage import StorageService, ArtifactType
from src.infrastructure.storage.config import StorageConfig

# 创建 Storage Service
config = StorageConfig.from_env()
storage = StorageService(blackboard, config)

# 上传 artifact
artifact = await storage.upload_artifact(
    file_path="image.png",
    project_id="PROJ-001",
    artifact_type=ArtifactType.IMAGE,
    metadata={"description": "Generated image"},
    generation_params={"prompt": "A cat", "seed": 42}
)

# 获取 signed URL
url = storage.get_artifact_url(artifact.artifact_id)

# 下载 artifact
storage.download_artifact(artifact.artifact_id, "downloaded.png")
```

## 核心组件

### 1. Artifact 数据模型

**类型**:
- 图像: `IMAGE`, `KEYFRAME`, `REFERENCE_IMAGE`
- 视频: `VIDEO`, `PREVIEW_VIDEO`, `FINAL_VIDEO`
- 音频: `AUDIO`, `MUSIC`, `VOICE`
- 文本: `SCRIPT`, `PROMPT`

**状态**:
- `UPLOADING`: 上传中
- `AVAILABLE`: 可用
- `PROCESSING`: 处理中
- `EXPIRED`: 已过期
- `DELETED`: 已删除

### 2. S3 客户端

```python
from src.infrastructure.storage import S3Client

s3 = S3Client(
    endpoint_url="http://localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    bucket_name="artifacts"
)

# 上传文件
url = s3.upload_file("image.png", "project/image.png")

# 生成 signed URL
signed_url = s3.generate_signed_url("project/image.png", expires_in=3600)
```

### 3. 缓存复用

```python
# 基于生成参数查找缓存
cached = cache_manager.find_cached_artifact({
    "prompt": "A cat",
    "seed": 42,
    "model": "sdxl"
})

if cached:
    print("Cache hit!")
    return cached
else:
    # 生成新 artifact
    artifact = generate_new()
```

## 配置

### 环境变量

```bash
# S3 配置
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY=minioadmin
S3_SECRET_KEY=minioadmin
S3_BUCKET_NAME=artifacts
S3_REGION=us-east-1

# 缓存配置
STORAGE_ENABLE_CACHE=true
STORAGE_CACHE_TTL_DAYS=30
STORAGE_SIGNED_URL_EXPIRES=3600
```

## License

MIT
