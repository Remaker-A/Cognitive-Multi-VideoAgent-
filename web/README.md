# VideoGen Web 应用

完整的 AI 视频生成流程 Web 界面。

## 功能特性

✅ **5 步完整流程**
1. 需求理解与拆分
2. AI 剧本创作
3. 智能分镜设计
4. 关键帧图像生成
5. 最终视频合成

✅ **现代化 UI**
- 深色主题设计
- 流畅的动画效果
- 响应式布局
- 实时进度显示

✅ **API 集成**
- 预留完整的 API 调用接口
- 易于替换为实际后端
- 支持异步处理

## 快速开始

### 1. 本地预览

直接在浏览器中打开 `index.html` 即可预览（使用模拟数据）。

### 2. 本地服务器

```bash
# 使用 Python
python -m http.server 8080

# 或使用 Node.js
npx http-server -p 8080
```

然后访问 `http://localhost:8080`

## API 集成

### 配置 API 地址

在 `app.js` 中修改：

```javascript
const API_BASE_URL = 'http://your-api-server.com/api';
```

### API 端点定义

#### 1. 需求分析
```
POST /api/analyze-requirement
Body: {
  project_id: string,
  requirement: {
    description: string,
    duration: number,
    quality_tier: "PREVIEW"|"STANDARD"|"HIGH"|"ULTRA",
    style: string
  }
}
Response: {
  theme: string,
  style: string,
  shots: number,
  duration: number
}
```

#### 2. 剧本生成
```
POST /api/generate-script
Body: {
  project_id: string,
  analysis: object
}
Response: {
  content: string
}
```

#### 3. 分镜生成
```
POST /api/generate-storyboard
Body: {
  project_id: string,
  script: object
}
Response: {
  shots: [{
    shot_id: string,
    title: string,
    description: string,
    duration: number,
    camera: string,
    movement: string
  }]
}
```

#### 4. 图像生成
```
POST /api/generate-image
Body: {
  project_id: string,
  shot: number
}
Response: {
  image_url: string
}
```

#### 5. 视频合成
```
POST /api/generate-video
Body: {
  project_id: string,
  images: array
}
Response: {
  video_url: string
}
```

## 文件结构

```
web/
├── index.html          # 主页面
├── styles.css          # 样式表
├── app.js             # 应用逻辑
└── README.md          # 本文档
```

## 自定义

### 修改颜色主题

在 `styles.css` 中的 `:root` 变量：

```css
:root {
    --primary-color: #6366f1;     /* 主色调 */
    --secondary-color: #8b5cf6;   /* 辅助色 */
    --bg-primary: #0f172a;        /* 背景色 */
    /* ... */
}
```

### 添加新步骤

1. 在 `index.html` 中添加新的 `nav-step` 和 `step-content`
2. 在 `app.js` 中添加对应的处理函数
3. 更新 `showStep` 函数中的标题映射

## 技术栈

- **HTML5**: 语义化结构
- **CSS3**: Flexbox/Grid 布局，CSS 变量，动画
- **JavaScript (ES6+)**: 异步处理，模块化设计
- **字体**: Inter (Google Fonts)

## 浏览器支持

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## 注意事项

⚠️ **当前版本使用模拟数据**，需要连接实际 API 才能正常工作。

⚠️ **跨域问题**: 如果 API 在不同域名，需要配置 CORS。

⚠️ **生产部署**: 建议使用 HTTPS 和适当的安全措施。

## License

MIT
