# 视频生成修改说明

## 已完成的后端修改

### 1. VideoInput 模型更新
```python
class VideoInput(BaseModel):
    project_id: str
    shot: int  # 镜头编号
    image_url: str  # 参考图 URL
    shot_info: Optional[Dict[str, Any]] = None  # 分镜详细信息
```

### 2. 视频生成 API 改进
- **模型**: 从 `Wan2.2-T2V-A14B` (text-to-video) 改为 `Wan2.2-I2V-A14B` (image-to-video)
- **输入**: 使用参考图作为起始帧
- **Prompt**: 基于分镜的动作描述和镜头运动

### 3. API 调用格式
```json
{
  "model": "Wan2.2-I2V-A14B",
  "content": [
    {
      "type": "image_url",
      "image_url": {
        "url": "参考图URL"
      }
    },
    {
      "type": "text",
      "text": "动作描述, 镜头运动, 场景, 人物, 情绪氛围"
    }
  ],
  "parameters": {
    "size": "1280*720",
    "watermark": true,
    "seed": 16 + shot_number
  }
}
```

## 需要的前端修改

### 当前问题
前端调用 `/api/generate-video` 时传递的是整个项目的图像列表，而不是单个镜头的信息。

### 需要修改的地方
文件: `web/app.js` 中的 `generateVideo` 函数

### 修改方案
```javascript
async function generateVideo() {
    showLoading('合成视频中...');
    
    try {
        const shots = projectData.storyboard?.shots || [];
        const images = projectData.images || [];
        const videoClips = [];
        
        // 逐个镜头生成视频
        for (let i = 0; i < shots.length; i++) {
            const shot = shots[i];
            const imageUrl = images[i]?.image_url;
            
            if (!imageUrl) {
                console.warn(`No image for shot ${i + 1}`);
                continue;
            }
            
            const response = await apiCall(`${API_BASE_URL}/generate-video`, {
                project_id: projectId,
                shot: i + 1,
                image_url: imageUrl,
                shot_info: shot
            });
            
            if (response.success && response.video_url) {
                videoClips.push(response.video_url);
            }
        }
        
        // TODO: 合并所有视频片段（需要额外的合并API或前端处理）
        
        hideLoading();
    } catch (error) {
        hideLoading();
        alert('视频生成失败: ' + error.message);
    }
}
```

### 额外需要
1. **保存图像数据**: 在图像生成步骤保存每个镜头的图像 URL
2. **视频合并**: 需要一个合并多个视频片段的方法（可以是后端 API 或前端处理）

## 效果
- ✅ 视频将基于参考图生成
- ✅ 动作和镜头运动将与分镜一致
- ✅ 每个镜头的视频都符合分镜描述
