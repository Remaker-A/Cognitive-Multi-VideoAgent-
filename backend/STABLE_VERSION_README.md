# VideoGen 后端稳定版本说明

## 当前稳定版本

**版本**: v1.0-stable  
**日期**: 2025-12-28  
**备份文件**: `api_server_stable_backup.py`

## 已实现的核心功能

### ✅ 稳定运行的功能

1. **需求分析** (`/api/analyze-requirement`)
   - LLM 分析用户需求
   - JSON 响应解析
   - 错误处理和降级

2. **剧本生成** (`/api/generate-script`)
   - 六维度专业框架
   - 参考提示词模板系统
   - 详细的场景、角色、镜头描述
   - 元数据支持

3. **分镜生成** (`/api/generate-storyboard`)
   - 详细的分镜脚本
   - JSON 格式输出
   - 包含所有拍摄参数

4. **图像生成** (`/api/generate-image`)
   - Image-to-Video 支持
   - 使用分镜详细信息构建 prompt
   - Qwen Image 模型集成
   - 任务轮询机制

5. **视频生成** (`/api/generate-video`)
   - Image-to-Video 模式
   - Wan2.2-I2V-A14B 模型
   - 基于参考图生成视频
   - 使用分镜动作描述

## 未来修改原则

### 🎯 最小改动原则

**在对后端进行任何修改时，必须遵循以下原则：**

1. **单一职责**
   - 每次只修改一个功能
   - 不要同时修改多个 API 端点
   - 避免改动无关代码

2. **增量修改**
   - 先在备份文件中测试
   - 验证无误后再应用到主文件
   - 保持向后兼容

3. **充分测试**
   - 修改后立即测试受影响的 API
   - 验证其他 API 未受影响
   - 检查前端集成

4. **版本控制**
   - 每次重大修改前创建备份
   - 记录修改内容和原因
   - 保留回滚路径

5. **文档先行**
   - 先写实施计划
   - 明确修改范围
   - 获得确认后再执行

## 修改流程

### 标准流程

```
1. 创建备份
   └─> Copy-Item api_server.py api_server_backup_YYYYMMDD.py

2. 编写修改计划
   └─> 创建 implementation_plan.md
   └─> 明确修改范围和影响

3. 最小化修改
   └─> 只修改必要的部分
   └─> 避免重构无关代码

4. 测试验证
   └─> 测试修改的功能
   └─> 测试相关功能
   └─> 检查整体系统

5. 确认稳定
   └─> 运行 > 5 分钟无错误
   └─> 前端可正常调用
   └─> 更新稳定版本备份
```

## 禁止的操作

❌ **以下操作可能破坏系统稳定性：**

1. ❌ 重构整个文件结构
2. ❌ 同时修改多个 API
3. ❌ 删除现有功能
4. ❌ 修改数据模型而不考虑兼容性
5. ❌ 修改 LLM 客户端配置
6. ❌ 更改核心工具函数

## 允许的安全修改

✅ **以下修改相对安全：**

1. ✅ 优化单个 API 的 prompt
2. ✅ 添加新的可选参数
3. ✅ 改进错误处理
4. ✅ 添加日志输出
5. ✅ 调整超时设置
6. ✅ 优化响应格式（保持兼容）

## 当前系统架构

### API 端点

```
GET  /               - 根路径
GET  /health         - 健康检查
POST /api/analyze-requirement - 需求分析
POST /api/generate-script     - 剧本生成
POST /api/generate-storyboard - 分镜生成
POST /api/generate-image      - 图像生成
POST /api/generate-video      - 视频生成
```

### 数据流

```
用户需求
  ↓
需求分析 (LLM)
  ↓
剧本生成 (LLM + 六维度框架)
  ↓
分镜生成 (LLM + JSON)
  ↓
图像生成 (Qwen + 分镜信息)
  ↓
视频生成 (Wan2.2 I2V + 参考图)
```

### 关键依赖

- **LLM**: DeepSeek-V3.2 (via SophNet)
- **Image**: Qwen Image (via SophNet)
- **Video**: Wan2.2-I2V-A14B (via SophNet)
- **Framework**: FastAPI + Uvicorn
- **HTTP Client**: httpx

## 回滚方法

如果修改导致问题：

```bash
# 1. 停止服务
# Ctrl+C

# 2. 恢复备份
Copy-Item api_server_stable_backup.py api_server.py -Force

# 3. 重启服务
python api_server.py
```

## 监控指标

确保以下指标正常：

- ✅ 服务启动成功
- ✅ `/health` 返回 200
- ✅ 所有 API 可正常调用
- ✅ 无 500 错误
- ✅ LLM 调用成功
- ✅ 前端集成正常

## 版本历史

| 版本 | 日期 | 主要改进 |
|------|------|---------|
| v1.0-stable | 2025-12-28 | 六维度剧本生成、Image-to-Video 视频生成、完整工作流 |

## 下一步优化建议

**仅在当前版本稳定运行至少 24 小时后考虑：**

1. 添加请求缓存机制
2. 优化 LLM prompt
3. 添加更详细的日志
4. 实现剧本编辑 API
5. 添加项目保存/加载功能

**所有优化必须：**
- 先创建备份
- 写实施计划
- 增量实施
- 充分测试

---

**重要提醒**: 
当前系统已经可以完整运行，包括需求分析、剧本生成、分镜设计、图像生成和视频生成。除非有明确的问题需要修复，否则应该保持当前版本的稳定性。
