# 如何修复后端 LLM 响应解析

## 问题

当前 `backend/api_server.py` 中的 `analyze_requirement` 端点虽然调用了 LLM，但返回的是硬编码的模拟数据，而不是 LLM 的真实分析结果。

## 解决方案

### 方法 1: 手动修改 api_server.py

找到 `api_server.py` 第 127-137 行，将：

```python
result = call_llm(system_prompt, user_prompt)

# 简化版返回（实际应解析 JSON）
return {
    "success": True,
    "theme": "智能产品宣传",
    "style": "现代科技风格",
    "shots": 8,
    "duration": req.get('duration', 30),
    "analysis_detail": result
}
```

替换为：

```python
result = call_llm(system_prompt, user_prompt)

# 解析 LLM 返回的 JSON
import json
import re

try:
    # 提取 JSON 部分
    json_match = re.search(r'\{[\s\S]*\}', result)
    if json_match:
        json_str = json_match.group(0)
        analysis = json.loads(json_str)
        
        return {
            "success": True,
            "theme": analysis.get("theme", "视频创作"),
            "style": analysis.get("style", req.get('style', '现代')),
            "shots": analysis.get("shots", 8),
            "duration": analysis.get("duration", req.get('duration', 30)),
            "key_elements": analysis.get("key_elements", []),
            "analysis_detail": result
        }
except Exception as e:
    print(f"JSON parse error: {e}")

# 降级返回
return {
    "success": True,
    "theme": "视频创作",
    "style": req.get('style', '现代'),
    "shots": 8,
    "duration": req.get('duration', 30),
    "key_elements": [],
    "analysis_detail": result
}
```

### 方法 2: 使用辅助函数

1. 已创建 `backend/llm_utils.py` 辅助函数
2. 在 `api_server.py` 顶部添加导入：
   ```python
   from llm_utils import parse_llm_json
   ```

3. 修改 `analyze_requirement` 函数：
   ```python
   result = call_llm(system_prompt, user_prompt)
   
   # 使用辅助函数解析
   analysis = parse_llm_json(result, {
       "theme": "视频创作",
       "style": req.get('style', '现代'),
       "shots": 8,
       "duration": req.get('duration', 30)
   })
   
   return {
       "success": True,
       "theme": analysis.get("theme"),
       "style": analysis.get("style"),
       "shots": analysis.get("shots"),
       "duration": analysis.get("duration"),
       "key_elements": analysis.get("key_elements", []),
       "analysis_detail": result
   }
   ```

## 修改后的效果

修改后，当用户输入需求时：
1. 前端发送用户的真实需求到后端
2. 后端调用 LLM API 分析需求
3. 解析 LLM 返回的 JSON
4. 返回 LLM 的真实分析结果给前端
5. 前端显示基于用户输入的分析结果

## 测试

修改后重启后端服务：
```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python api_server.py
```

然后在前端输入不同的需求，应该会看到不同的分析结果。

## 注意事项

- 如果 LLM API 连接失败，会降级到默认值
- 如果 JSON 解析失败，也会降级到默认值
- 所有错误都会被捕获并记录，不会导致服务崩溃
