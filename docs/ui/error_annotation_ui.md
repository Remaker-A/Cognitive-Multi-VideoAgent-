# 错误标注 UI 设计文档

## 概述

用户错误标注界面，允许用户手动标注和报告 AI 生成内容中的错误。

## UI 组件

### 1. 标注画布 (Annotation Canvas)

#### 功能
- 显示待标注的图像
- 支持三种选择工具：矩形、多边形、点
- 支持缩放和平移
- 支持撤销和重做

#### HTML 结构
```html
<div class="annotation-container">
    <div class="annotation-toolbar">
        <button id="rect-tool" class="tool-btn active">
            <i class="icon-rectangle"></i> 矩形选择
        </button>
        <button id="polygon-tool" class="tool-btn">
            <i class="icon-polygon"></i> 多边形选择
        </button>
        <button id="point-tool" class="tool-btn">
            <i class="icon-point"></i> 点选择
        </button>
        <div class="divider"></div>
        <button id="undo-btn"><i class="icon-undo"></i></button>
        <button id="redo-btn"><i class="icon-redo"></i></button>
        <button id="clear-btn"><i class="icon-clear"></i> 清除</button>
    </div>
    
    <div class="canvas-wrapper">
        <canvas id="annotation-canvas"></canvas>
        <div class="zoom-controls">
            <button id="zoom-in">+</button>
            <span id="zoom-level">100%</span>
            <button id="zoom-out">-</button>
            <button id="fit-screen">适应屏幕</button>
        </div>
    </div>
</div>
```

#### JavaScript 功能
```javascript
class AnnotationCanvas {
    constructor(imageUrl) {
        this.canvas = document.getElementById('annotation-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.image = new Image();
        this.image.src = imageUrl;
        
        this.currentTool = 'rectangle';
        this.annotations = [];
        this.currentAnnotation = null;
        
        this.init();
    }
    
    init() {
        this.image.onload = () => {
            this.canvas.width = this.image.width;
            this.canvas.height = this.image.height;
            this.render();
        };
        
        this.canvas.addEventListener('mousedown', this.onMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.onMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.onMouseUp.bind(this));
    }
    
    onMouseDown(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        if (this.currentTool === 'rectangle') {
            this.currentAnnotation = {
                type: 'rectangle',
                startX: x,
                startY: y,
                endX: x,
                endY: y
            };
        }
        // ... 其他工具逻辑
    }
    
    render() {
        // 绘制图像
        this.ctx.drawImage(this.image, 0, 0);
        
        // 绘制所有标注
        this.annotations.forEach(ann => {
            this.drawAnnotation(ann);
        });
        
        // 绘制当前标注
        if (this.currentAnnotation) {
            this.drawAnnotation(this.currentAnnotation);
        }
    }
    
    getAnnotationData() {
        return {
            type: this.currentAnnotation.type,
            coordinates: this.normalizeCoordinates(this.currentAnnotation)
        };
    }
}
```

### 2. 错误类型选择器 (Error Type Selector)

#### HTML 结构
```html
<div class="error-type-selector">
    <h3>错误类型</h3>
    
    <div class="form-group">
        <label>错误分类</label>
        <select id="error-category" onchange="updateErrorTypes()">
            <option value="">-- 请选择 --</option>
            <option value="hand">手部错误</option>
            <option value="face">面部错误</option>
            <option value="pose">姿态错误</option>
            <option value="physics">物理规律错误</option>
            <option value="text">文字错误</option>
            <option value="other">其他</option>
        </select>
    </div>
    
    <div class="form-group">
        <label>具体错误</label>
        <select id="error-type">
            <option value="">-- 请先选择分类 --</option>
        </select>
    </div>
</div>
```

#### JavaScript 功能
```javascript
const ERROR_TYPES = {
    hand: [
        { value: 'hand_finger_count_wrong', label: '手指数量错误' },
        { value: 'hand_deformed', label: '手部形态异常' },
        { value: 'hand_missing', label: '手部缺失' },
        { value: 'hand_other', label: '其他手部问题' }
    ],
    face: [
        { value: 'face_missing_eyes', label: '缺少眼睛' },
        { value: 'face_missing_nose', label: '缺少鼻子' },
        { value: 'face_missing_mouth', label: '缺少嘴巴' },
        { value: 'face_expression_abnormal', label: '表情异常' },
        { value: 'face_asymmetric', label: '面部不对称' },
        { value: 'face_other', label: '其他面部问题' }
    ],
    // ... 其他类别
};

function updateErrorTypes() {
    const category = document.getElementById('error-category').value;
    const typeSelect = document.getElementById('error-type');
    
    typeSelect.innerHTML = '<option value="">-- 请选择 --</option>';
    
    if (category && ERROR_TYPES[category]) {
        ERROR_TYPES[category].forEach(type => {
            const option = document.createElement('option');
            option.value = type.value;
            option.textContent = type.label;
            typeSelect.appendChild(option);
        });
    }
}
```

### 3. 标注表单 (Annotation Form)

#### HTML 结构
```html
<form id="annotation-form" class="annotation-form">
    <div class="form-group">
        <label>严重程度</label>
        <div class="severity-options">
            <label class="severity-option critical">
                <input type="radio" name="severity" value="CRITICAL" required>
                <span>严重 (CRITICAL)</span>
                <small>必须修复</small>
            </label>
            <label class="severity-option high">
                <input type="radio" name="severity" value="HIGH">
                <span>高 (HIGH)</span>
                <small>强烈建议修复</small>
            </label>
            <label class="severity-option medium">
                <input type="radio" name="severity" value="MEDIUM">
                <span>中 (MEDIUM)</span>
                <small>建议修复</small>
            </label>
            <label class="severity-option low">
                <input type="radio" name="severity" value="LOW">
                <span>低 (LOW)</span>
                <small>可选修复</small>
            </label>
        </div>
    </div>
    
    <div class="form-group">
        <label for="error-description">错误描述</label>
        <textarea 
            id="error-description" 
            name="description"
            rows="4"
            placeholder="请详细描述您发现的错误..."
            required
        ></textarea>
        <small class="hint">提供详细描述有助于更好地修复错误</small>
    </div>
    
    <div class="form-actions">
        <button type="button" class="btn-secondary" onclick="cancelAnnotation()">
            取消
        </button>
        <button type="submit" class="btn-primary">
            提交标注
        </button>
    </div>
</form>
```

#### JavaScript 提交逻辑
```javascript
document.getElementById('annotation-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const canvas = annotationCanvas;
    const formData = new FormData(e.target);
    
    const annotationData = {
        project_id: currentProjectId,
        shot_id: currentShotId,
        artifact_url: currentImageUrl,
        region: canvas.getAnnotationData(),
        error_category: document.getElementById('error-category').value,
        error_type: document.getElementById('error-type').value,
        error_description: formData.get('description'),
        severity: formData.get('severity'),
        annotated_by: currentUserId
    };
    
    try {
        const response = await fetch('/api/error-correction/annotate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(annotationData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showSuccess('标注已提交，正在处理修复...');
            closeAnnotationModal();
        } else {
            showError('提交失败：' + result.error);
        }
    } catch (error) {
        showError('提交失败：' + error.message);
    }
});
```

## 完整工作流程

### 1. 打开标注界面
```javascript
function openAnnotationModal(imageUrl, shotId) {
    // 显示模态框
    const modal = document.getElementById('annotation-modal');
    modal.style.display = 'block';
    
    // 初始化画布
    annotationCanvas = new AnnotationCanvas(imageUrl);
    
    // 设置上下文
    currentShotId = shotId;
}
```

### 2. 用户操作流程
1. 用户在审批界面点击"标注错误"按钮
2. 打开标注模态框，显示图像
3. 用户选择工具（矩形/多边形/点）
4. 用户在图像上圈选错误区域
5. 用户选择错误分类和具体类型
6. 用户选择严重程度
7. 用户输入错误描述
8. 用户点击"提交标注"
9. 系统处理标注并触发修复流程

### 3. 集成到审批流程
```html
<!-- 在审批界面添加 -->
<div class="approval-actions">
    <button class="btn-approve" onclick="approveShot()">通过</button>
    <button class="btn-revise" onclick="requestRevision()">要求修改</button>
    <button class="btn-annotate" onclick="openAnnotationModal(currentImage, currentShotId)">
        <i class="icon-annotate"></i> 标注错误
    </button>
</div>
```

## CSS 样式建议

```css
.annotation-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

.annotation-toolbar {
    display: flex;
    gap: 8px;
    padding: 12px;
    background: #f5f5f5;
    border-bottom: 1px solid #ddd;
}

.tool-btn {
    padding: 8px 16px;
    border: 1px solid #ccc;
    background: white;
    cursor: pointer;
    border-radius: 4px;
}

.tool-btn.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.canvas-wrapper {
    flex: 1;
    position: relative;
    overflow: auto;
    background: #fafafa;
}

.severity-options {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
}

.severity-option {
    padding: 12px;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s;
}

.severity-option.critical { border-color: #dc3545; }
.severity-option.high { border-color: #fd7e14; }
.severity-option.medium { border-color: #ffc107; }
.severity-option.low { border-color: #28a745; }

.severity-option input:checked + span {
    font-weight: bold;
}
```

## API 端点

### POST /api/error-correction/annotate
提交错误标注

**请求体**:
```json
{
    "project_id": "PROJ-001",
    "shot_id": "S001_001",
    "artifact_url": "...",
    "region": {
        "type": "rectangle",
        "coordinates": [...]
    },
    "error_category": "hand",
    "error_type": "hand_finger_count_wrong",
    "error_description": "左手有6个手指",
    "severity": "CRITICAL",
    "annotated_by": "user_123"
}
```

**响应**:
```json
{
    "success": true,
    "annotation_id": "ANN-abc123",
    "repair_result": {
        "repair_level": 1,
        "status": "requested"
    }
}
```

## 注意事项

1. **坐标归一化**: 所有坐标应归一化为 0-1 范围，以适应不同分辨率
2. **实时预览**: 在绘制标注时提供实时视觉反馈
3. **验证**: 提交前验证所有必填字段
4. **错误提示**: 提供清晰的错误提示和帮助信息
5. **响应式设计**: 确保在不同屏幕尺寸下都能正常使用
