# VideoGen 系统测试指南

## 🧪 测试概述

本文档提供完整的测试指南，包括单元测试、集成测试和端到端测试。

## 📋 测试清单

### 1. API 连接测试

#### 测试 LLM API
```bash
python test_llm.py
```

**预期结果**:
- ✅ 连接成功
- ✅ 返回生成的文本内容

**常见问题**:
- ❌ Connection error - 检查网络连接
- ❌ 401 Unauthorized - 检查 API Key
- ❌ 429 Too Many Requests - API 限流

#### 测试图像生成 API
```bash
python test_image_gen.py
```

**预期结果**:
- ✅ 返回图像 URL
- ✅ 状态码 200

#### 测试视频生成 API
```bash
python test_video_gen.py
```

**预期结果**:
- ✅ 返回视频 URL
- ✅ 状态码 200

### 2. 后端服务测试

#### 启动后端
```bash
python api_server.py
```

**验证**:
- 访问 http://localhost:8000
- 访问 http://localhost:8000/docs (Swagger UI)
- 访问 http://localhost:8000/health

#### 测试各个端点

```bash
# 1. 健康检查
curl http://localhost:8000/health

# 2. 需求分析
curl -X POST "http://localhost:8000/api/analyze-requirement" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "TEST-001",
    "requirement": {
      "description": "测试视频",
      "duration": 30,
      "quality_tier": "STANDARD",
      "style": "modern"
    }
  }'

# 3. 剧本生成
curl -X POST "http://localhost:8000/api/generate-script" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "TEST-001",
    "analysis": {}
  }'

# 4. 分镜生成
curl -X POST "http://localhost:8000/api/generate-storyboard" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "TEST-001",
    "script": {}
  }'

# 5. 图像生成
curl -X POST "http://localhost:8000/api/generate-image" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "TEST-001",
    "shot": 1
  }'

# 6. 视频生成
curl -X POST "http://localhost:8000/api/generate-video" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "TEST-001",
    "images": []
  }'
```

### 3. 完整流程测试

```bash
python test_full_workflow.py
```

**测试步骤**:
1. 需求分析 (LLM)
2. 剧本生成 (LLM)
3. 分镜生成 (LLM)
4. 图像生成 (Qwen × 3)
5. 视频合成 (Wan2.2)

### 4. 前端测试

#### 启动前端
```bash
cd ../web
python -m http.server 8080
```

访问 http://localhost:8080

**测试流程**:
1. 输入需求
2. 点击"开始分析需求"
3. 查看分析结果
4. 进入下一步生成剧本
5. 继续完成所有步骤

## 🔧 故障排查

### LLM API 连接失败

**问题**: `Connection error` 或 `LLM 调用失败`

**解决方案**:
1. 检查网络连接
2. 验证 API Key 是否正确
3. 检查 API 端点 URL
4. 查看 API 配额和限流

**测试 API Key**:
```python
from openai import OpenAI

client = OpenAI(
    api_key="your_api_key",
    base_url="https://www.sophnet.com/api/open-apis/v1"
)

try:
    response = client.chat.completions.create(
        model="DeepSeek-V3.2",
        messages=[{"role": "user", "content": "测试"}]
    )
    print("✅ API Key 有效")
except Exception as e:
    print(f"❌ 错误: {e}")
```

### 图像生成失败

**问题**: 图像 API 返回错误

**解决方案**:
1. 检查 API 响应格式
2. 验证 prompt 是否符合要求
3. 检查图像尺寸参数
4. 查看错误降级机制是否工作

### 视频生成失败

**问题**: 视频 API 超时或失败

**解决方案**:
1. 增加超时时间（当前 120 秒）
2. 检查视频描述是否合适
3. 验证参数格式
4. 使用降级视频

### 前端无法连接后端

**问题**: CORS 错误或连接失败

**解决方案**:
1. 确认后端正在运行
2. 检查 API_BASE_URL 配置
3. 验证 CORS 设置
4. 查看浏览器控制台错误

## 📊 性能测试

### API 响应时间

| 端点 | 预期时间 | 超时设置 |
|------|---------|---------|
| 需求分析 | 5-10秒 | 30秒 |
| 剧本生成 | 10-20秒 | 60秒 |
| 分镜生成 | 10-20秒 | 60秒 |
| 图像生成 | 20-40秒 | 90秒 |
| 视频生成 | 60-90秒 | 180秒 |

### 并发测试

```python
import concurrent.futures
import requests

def test_concurrent_requests():
    urls = [f"http://localhost:8000/api/generate-image" for _ in range(5)]
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(
                requests.post,
                url,
                json={"project_id": "TEST", "shot": i}
            )
            for i, url in enumerate(urls, 1)
        ]
        
        results = [f.result() for f in futures]
    
    print(f"完成 {len(results)} 个并发请求")
```

## ✅ 测试检查表

### 基础功能
- [ ] 后端服务启动成功
- [ ] API 文档可访问
- [ ] 健康检查端点正常
- [ ] 前端页面加载正常

### API 测试
- [ ] LLM API 连接成功
- [ ] 图像生成 API 工作
- [ ] 视频生成 API 工作
- [ ] 所有端点返回正确格式

### 集成测试
- [ ] 需求分析流程完整
- [ ] 剧本生成正确
- [ ] 分镜生成正确
- [ ] 图像批量生成
- [ ] 视频合成成功

### 用户体验
- [ ] UI 响应流畅
- [ ] 进度显示正确
- [ ] 错误提示清晰
- [ ] 结果展示完整

## 🐛 已知问题

1. **LLM 连接不稳定**: 可能需要重试机制
2. **图像生成较慢**: 考虑添加缓存
3. **视频生成超时**: 需要异步任务队列
4. **并发限制**: API 可能有速率限制

## 📝 测试报告模板

```
测试日期: YYYY-MM-DD
测试人员: XXX
环境: 开发/测试/生产

测试结果:
✅ 通过: X 项
❌ 失败: X 项
⚠️ 警告: X 项

详细说明:
1. [测试项] - [结果] - [备注]
2. ...

问题列表:
1. [问题描述] - [严重程度] - [解决方案]
2. ...
```

## 🚀 持续集成

### GitHub Actions 示例

```yaml
name: VideoGen CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
    
    - name: Run tests
      run: |
        cd backend
        python test_llm.py
        python test_image_gen.py
        python test_video_gen.py
```

## 📞 支持

如遇问题，请检查:
1. 日志文件
2. API 响应
3. 网络连接
4. 配置文件

---

**最后更新**: 2025-12-27
