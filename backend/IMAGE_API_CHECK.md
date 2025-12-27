# 图像生成 API 配置检查报告

## API 端点配置

### 基本信息
- **端点**: `POST /api/generate-image`
- **API 提供商**: SophNet
- **模型**: qwen-image
- **URL**: https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task

### 认证配置
- **认证方式**: Bearer Token
- **API Key**: HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg
- **状态**: ✅ 已配置（硬编码）

### 请求参数
```json
{
  "model": "qwen-image",
  "input": {
    "prompt": "专业电影镜头，高质量，4K分辨率，镜头 {shot_number}"
  },
  "parameters": {
    "size": "1328*1328",
    "seed": 42 + shot_number
  }
}
```

### 超时设置
- **HTTP 超时**: 60 秒
- **Trust Env**: 根据环境变量配置

## 当前问题

### 1. Prompt 过于简单
**问题**: 当前 prompt 只是通用描述，没有使用分镜脚本的详细信息
```python
prompt = f"专业电影镜头，高质量，4K分辨率，镜头 {data.shot}"
```

**建议**: 应该从分镜脚本中提取详细信息：
- 场景描述
- 人物/主体
- 视觉元素
- 拍摄角度

### 2. 缺少错误处理详情
**问题**: 错误处理只返回通用消息，没有详细的错误信息

### 3. 没有任务轮询机制
**问题**: 图像生成可能是异步的，需要轮询任务状态
- 当前代码假设同步返回结果
- 实际 API 可能返回 task_id，需要轮询

### 4. 响应格式假设
**问题**: 代码假设响应格式为 `result.get("output", {}).get("url", "")`
- 实际 API 响应格式可能不同
- 需要根据实际响应调整

## 建议改进

### 1. 使用分镜详细信息
```python
# 从分镜脚本获取详细信息
shot_info = get_shot_info(data.project_id, data.shot)
prompt = f"{shot_info['scene']}, {shot_info['characters']}, {shot_info['action']}, {shot_info['visual_elements']}, {shot_info['camera']}, {shot_info['angle']}"
```

### 2. 添加任务轮询
```python
# 提交任务
task_id = submit_image_task(prompt)
# 轮询任务状态
result = poll_task_status(task_id, max_wait=300)
```

### 3. 改进错误处理
```python
except httpx.TimeoutException:
    return {"success": False, "error": "请求超时"}
except httpx.NetworkError:
    return {"success": False, "error": "网络连接失败"}
```

### 4. 添加日志
```python
print(f"Image generation request for shot {data.shot}")
print(f"Prompt: {prompt}")
print(f"Response: {response.text}")
```

## 测试建议

1. **测试 API 连接**
   ```bash
   cd backend
   python test_image_gen.py
   ```

2. **检查响应格式**
   - 查看实际 API 返回的 JSON 结构
   - 调整代码以匹配实际格式

3. **测试超时处理**
   - 验证 60 秒超时是否足够
   - 考虑增加超时时间

## 当前状态

✅ API 配置正确  
⚠️ Prompt 需要改进  
⚠️ 可能需要添加任务轮询  
⚠️ 错误处理需要增强  
⚠️ 需要添加详细日志
