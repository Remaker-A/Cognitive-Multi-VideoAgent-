// VideoGen Web Application
// 完整?AI 视频生成流程应用

const API_BASE_URL = 'http://localhost:8000/api'; // TODO: 替换为实?API 地址
const API_HEALTH_URL = `${API_BASE_URL.replace(/\/api\/?$/, '')}/health`;
const API_CHECK_TIMEOUT_MS = 4000;
const API_CHECK_TTL_MS = 5000;
const API_LOGGING = true;

let apiHealthCache = {
    ok: null,
    checkedAt: 0
};

let currentStep = 1;
let maxCompletedStep = 1; // 跟踪用户完成的最大步骤数
let projectId = null;
let projectData = {};

// ==================== 初始?====================
document.addEventListener('DOMContentLoaded', () => {
    projectId = 'PROJ-' + Date.now().toString(36) + Math.random().toString(36).substr(2, 5).toUpperCase();
    document.getElementById('project-id').textContent = projectId;
    bindEvents();
    showStep(1);
    checkApiHealth(true);
});

function bindEvents() {
    // 绑定操作按钮
    document.getElementById('analyze-requirement-btn').addEventListener('click', analyzeRequirement);
    document.getElementById('proceed-to-script-btn')?.addEventListener('click', () => proceedTo(2));
    document.getElementById('proceed-to-storyboard-btn')?.addEventListener('click', () => proceedTo(3));
    document.getElementById('proceed-to-images-btn')?.addEventListener('click', () => proceedTo(4));
    document.getElementById('proceed-to-video-btn')?.addEventListener('click', () => proceedTo(5));

    // 绑定剧本编辑和重新生成按?
    document.getElementById('edit-script-btn')?.addEventListener('click', openScriptEditor);
    document.getElementById('regenerate-script-btn')?.addEventListener('click', regenerateScript);

    // 绑定导航栏步骤点击事件，允许返回查看之前的步?
    document.querySelectorAll('.nav-step').forEach(step => {
        step.addEventListener('click', () => {
            const stepNum = parseInt(step.dataset.step);
            // 允许切换到已完成的任何步?
            if (stepNum <= maxCompletedStep) {
                showStep(stepNum);
            }
        });

        // 添加鼠标悬停效果提示
        step.addEventListener('mouseenter', () => {
            const stepNum = parseInt(step.dataset.step);
            if (stepNum <= maxCompletedStep) {
                step.style.cursor = 'pointer';
            } else {
                step.style.cursor = 'not-allowed';
            }
        });
    });

    // 绑定模态框的ESC键关闭功?
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const modal = document.getElementById('script-editor-modal');
            if (modal && modal.style.display !== 'none') {
                closeScriptEditor();
            }
        }
    });
}

function showStep(num) {
    currentStep = num;
    document.querySelectorAll('.nav-step').forEach(s => {
        const n = parseInt(s.dataset.step);
        s.classList.toggle('active', n === num);
        // 标记为已完成：步骤号小于最大完成步?
        s.classList.toggle('completed', n < maxCompletedStep || (n === maxCompletedStep && n < num));
    });
    document.querySelectorAll('.step-content').forEach(c => c.classList.remove('active'));
    document.getElementById(`step-${num}`).classList.add('active');
}

function proceedTo(step) {
    // 更新最大完成步?
    if (step > maxCompletedStep) {
        maxCompletedStep = step;
    }
    showStep(step);
    [null, null, generateScript, generateStoryboard, generateImages, generateVideo][step]?.();
}

// ==================== API 调用 ====================
async function apiCall(endpoint, data) {
    try {
        const healthy = await checkApiHealth();
        if (!healthy) {
            throw new Error('后端未启动或无法连接，请先运行后端服务');
        }

        const startTime = performance.now();
        logApiEvent('request', endpoint, { payload: data });
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            logApiEvent('response', endpoint, {
                status: response.status,
                durationMs: Math.round(performance.now() - startTime)
            });
            throw new Error(`API Error: ${response.status}`);
        }

        const payload = await response.json();
        logApiEvent('response', endpoint, {
            status: response.status,
            durationMs: Math.round(performance.now() - startTime),
            data: payload
        });
        setApiStatus(true);
        return payload;
    } catch (error) {
        if (error.name === 'AbortError' || error.message.includes('Failed to fetch')) {
            setApiStatus(false);
            throw new Error('后端未启动或无法连接，请先运行后端服务');
        }
        logApiEvent('error', endpoint, { message: error.message });
        console.error('API call failed:', error);
        throw error;
    }
}

// ==================== 步骤逻辑 ====================
async function analyzeRequirement() {
    const req = document.getElementById('user-requirement').value.trim();
    if (!req) return alert('请输入需?);

    projectData.requirement = {
            description: req,
            duration: parseInt(document.getElementById('video-duration').value),
            quality_tier: document.getElementById('quality-tier').value,
            style: document.getElementById('video-style').value
        };

    showLoading('分析需求中...');

    try {
        const response = await apiCall(`${API_BASE_URL}/analyze-requirement`, {
            project_id: projectId,
            requirement: projectData.requirement
        });

        // 使用 API 返回的真实数?
        document.getElementById('analysis-theme').textContent = response.theme || '未知主题';
        document.getElementById('analysis-style').textContent = response.style || '未知风格';
        document.getElementById('analysis-shots').textContent = `${response.shots || 0} 个镜头`;
        document.getElementById('analysis-duration').textContent = `${response.duration || 0} 秒`;
        document.getElementById('analysis-result').style.display = 'block';

        // 保存分析结果
        projectData.analysis = response;

        hideLoading();
    } catch (error) {
        hideLoading();
        alert('需求分析失? ' + error.message);
    }
}

async function generateScript() {
    showLoading('生成剧本?..');

    try {
        const response = await apiCall(`${API_BASE_URL}/generate-script`, {
            project_id: projectId,
            analysis: projectData.analysis
        });

        // 使用 API 返回的真实剧?
        const script = response.content || '剧本生成失败';

        document.getElementById('script-status').style.display = 'none';
        document.getElementById('script-content').textContent = script;
        document.getElementById('script-result').style.display = 'block';

        // 保存剧本数据
        projectData.script = response;

        // 渲染角色列表
        if (response.characters && response.characters.length > 0) {
            renderCharacters(response.characters);
            projectData.characters = response.characters;
        } else {
            // 如果没有角色,显示提示
            document.getElementById('characters-list').innerHTML = '<p class="no-characters">此剧本暂无角色信?/p>';
        }

        hideLoading();
    } catch (error) {
        hideLoading();
        alert('剧本生成失败: ' + error.message);
    }
}

// 渲染角色列表
function renderCharacters(characters) {
    const container = document.getElementById('characters-list');
    const html = characters.map(char => `
        <div class="character-card">
            <h5 class="character-name">${char.name}</h5>
            <p class="character-desc">${char.description}</p>
        </div>
    `).join('');
    container.innerHTML = html;
}

async function generateStoryboard() {
    showLoading('生成分镜?..');

    try {
        const response = await apiCall(`${API_BASE_URL}/generate-storyboard`, {
            project_id: projectId,
            script: projectData.script
        });

        // 使用 API 返回的真实分镜数?
        const shots = response.shots || [];

        const html = shots.map((s, i) => `
            <div class="shot-card" data-shot="${i + 1}">
                <div class="shot-header">
                    <div class="shot-number">${i + 1}</div>
                    <div class="shot-header-info">
                        <div class="shot-title">${s.title || `镜头 ${i + 1}`}</div>
                        <div class="shot-meta">
                            <span class="meta-item"><span class="meta-icon">⏱️</span> ${s.duration || 0}?/span>
                            <span class="meta-item"><span class="meta-icon">📹</span> ${s.camera || '未知'}</span>
                            <span class="meta-item"><span class="meta-icon">🎬</span> ${s.movement || '未知'}</span>
                        </div>
                    </div>
                    <button class="expand-btn" onclick="toggleShotDetails(${i + 1})">
                        <span class="expand-icon">?/span>
                    </button>
                </div>
                <div class="shot-body">
                    <div class="shot-section">
                        <div class="section-label">📝 场景描述</div>
                        <div class="section-content">${s.description || '无描?}</div>
                    </div >
            ${
            s.visual_elements ? `
                    <div class="shot-section">
                        <div class="section-label">🎨 视觉元素</div>
                        <div class="section-content">${s.visual_elements}</div>
                    </div>
                    ` : ''
        }
                    ${
            s.dialogue || s.narration ? `
                    <div class="shot-section">
                        <div class="section-label">💬 文案/对白</div>
                        <div class="section-content">${s.dialogue || s.narration || ''}</div>
                    </div>
                    ` : ''
        }
                    ${
            s.transition ? `
                    <div class="shot-section">
                        <div class="section-label">🔄 转场效果</div>
                        <div class="section-content">${s.transition}</div>
                    </div>
                    ` : ''
        }
                    ${
            s.notes ? `
                    <div class="shot-section">
                        <div class="section-label">📌 备注</div>
                        <div class="section-content shot-notes">${s.notes}</div>
                    </div>
                    ` : ''
        }
                </div >
            </div >
            `).join('');

        document.getElementById('storyboard-status').style.display = 'none';
        document.getElementById('storyboard-list').innerHTML = html;
        document.getElementById('storyboard-result').style.display = 'block';

        // 保存分镜数据
        projectData.storyboard = response;

        hideLoading();
    } catch (error) {
        hideLoading();
        alert('分镜生成失败: ' + error.message);
    }
}

async function generateImages() {
    const grid = document.getElementById('images-grid');
    grid.innerHTML = '';

    const totalShots = projectData.storyboard?.shots?.length || 8;

    for (let i = 1; i <= totalShots; i++) {
        grid.innerHTML += `
            < div class="image-card" id = "img-${i}" >
                <div class="image-preview">
                    <div class="status-icon loading">?/div>
                    </div>
                    <div class="image-info">
                        <div class="image-title">镜头 ${i}</div>
                        <div class="image-status">生成?..</div>
                    </div>
                </div>
        `;
    }

    // 逐个生成图像
    for (let i = 1; i <= totalShots; i++) {
        document.getElementById('images-progress-fill').style.width = `${ (i / totalShots) * 100 }% `;
        document.getElementById('images-progress-text').textContent = `${ i } / ${totalShots} 已完成`;

        try {
            // 获取对应的分镜信?
            const shots = projectData.storyboard?.shots || [];
            const shotInfo = shots[i - 1] || null; // 数组索引?0 开?

            const response = await apiCall(`${API_BASE_URL}/generate-image`, {
                project_id: projectId,
                shot: i,
                shot_info: shotInfo  // 传递分镜详细信?
            });

            const card = document.getElementById(`img-${i}`);
            const imageUrl = response.image_url || createPlaceholderSVG(i, '#6366f1');
            card.querySelector('.image-preview').innerHTML = `<img src="${imageUrl}">`;
            card.querySelector('.image-status').textContent = response.success ? '已完? : '使用占位 ?;

            // 保存图像数据供视频生成使?
            if (!projectData.images) {
                projectData.images = [];
            }
            projectData.images[i - 1] = {
                shot: i,
                image_url: imageUrl,
                success: response.success
            };
        } catch (error) {
            console.error(`Image ${i} generation failed:`, error);
            const card = document.getElementById(`img-${i}`);
            card.querySelector('.image-preview').innerHTML = `<img src="${createPlaceholderSVG(i, '#ef4444')}">`;
            card.querySelector('.image-status').textContent = '生成失败';

            // 保存失败的图像数?
            if (!projectData.images) {
                projectData.images = [];
            }
            projectData.images[i - 1] = {
                shot: i,
                image_url: createPlaceholderSVG(i, '#ef4444'),
                success: false
            };
        }

        await new Promise(r => setTimeout(r, 500));
    }

    document.getElementById('images-actions').style.display = 'block';
}

// 创建本地 SVG 占位?
function createPlaceholderSVG(shotNumber, color = '#6366f1') {
    const svg = `
        <svg width="800" height="450" xmlns="http://www.w3.org/2000/svg">
            <rect width="800" height="450" fill="#1e293b"/>
            <text x="400" y="225" font-family="Arial, sans-serif" font-size="48" 
                  fill="${color}" text-anchor="middle" dominant-baseline="middle">
                镜头 ${shotNumber}
            </text>
        </svg>
    `;
    return 'data:image/svg+xml;base64,' + btoa(unescape(encodeURIComponent(svg)));
}

async function generateVideo() {
    showLoading('生成视频中...');
    try {
        const shots = projectData.storyboard?.shots || [];
        const images = projectData.images || [];
        if (shots.length === 0) {
            throw new Error('没有分镜数据');
        }
        if (images.length === 0) {
            throw new Error('没有参考图,请先生成图像');
        }
        const videoClips = [];
        const totalShots = Math.min(shots.length, images.length);
        // 显示进度
        document.getElementById('video-status').style.display = 'block';
        document.getElementById('video-status').innerHTML = \`
            <div class="status-text">正在生成视频片段...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="video-progress-fill"></div>
            </div>
            <div class="progress-text" id="video-progress-text">0 / \${totalShots} 已完成</div>
        \`;
        // 显示卡片容器
        document.getElementById('video-cards-container').style.display = 'block';
        const grid = document.getElementById('video-cards-grid');
        grid.innerHTML = '';
        // 为每个镜头创建加载状态的卡片
        for (let i = 0; i < totalShots; i++) {
            renderVideoCard(i, shots[i], null, 'loading');
        }
        hideLoading();
        // 逐个镜头生成视频
        for (let i = 0; i < totalShots; i++) {
            const shot = shots[i];
            const image = images[i];
            if (!image || !image.image_url) {
                console.warn(\`No image for shot \${i + 1}, skipping\`);
                renderVideoCard(i, shot, null, 'error');
                continue;
            }
            try {
                console.log(\`Generating video for shot \${i + 1}...\`);
                const response = await apiCall(\`\${API_BASE_URL}/generate-video\`, {
                    project_id: projectId,
                    shot: i + 1,
                    image_url: image.image_url,
                    shot_info: shot
                });
                if (response.success && response.video_url) {
                    videoClips.push({
                        shot: i + 1,
                        url: response.video_url,
                        duration: shot.duration || 4
                    });
                    // 更新卡片为成功状态
                    renderVideoCard(i, shot, response.video_url, 'success');
                    console.log(\`Shot \${i + 1} video generated:\`, response.video_url);
                } else {
                    renderVideoCard(i, shot, null, 'error');
                }
                // 更新进度
                document.getElementById('video-progress-fill').style.width = \`\${((i + 1) / totalShots) * 100}%\`;
                document.getElementById('video-progress-text').textContent = \`\${i + 1} / \${totalShots} 已完成\`;
            } catch (error) {
                console.error(\`Video generation failed for shot \${i + 1}:\`, error);
                renderVideoCard(i, shot, null, 'error');
            }
            await new Promise(r => setTimeout(r, 500));
        }
        // 隐藏进度条
        document.getElementById('video-status').style.display = 'none';
        if (videoClips.length === 0) {
            throw new Error('所有镜头的视频生成都失败了');
        }
        // 保存视频片段数据
        projectData.videoClips = videoClips;
        // 显示所有视频片段信息
        console.log('Generated video clips:', videoClips);
        alert(\`成功生成 \${videoClips.length} 个视频片段!\`);
    } catch (error) {
        hideLoading();
        alert('视频生成失败: ' + error.message);
        document.getElementById('video-status').style.display = 'none';
    }
}

// 下载所有视?
function downloadAllVideos() {
    const videoClips = projectData.videoClips || [];
    if (videoClips.length === 0) {
        alert('没有可下载的视频');
        return;
    }

    videoClips.forEach((clip, index) => {
        setTimeout(() => {
            const a = document.createElement('a');
            a.href = clip.url;
            a.download = `shot - ${ clip.shot }.mp4`;
            a.click();
        }, index * 500);
    });
}

// ==================== 工具函数 ====================
function showLoading(text) {
    document.getElementById('loading-text').textContent = text;
    document.getElementById('loading-overlay').classList.add('active');
}

function hideLoading() {
    document.getElementById('loading-overlay').classList.remove('active');
}

async function checkApiHealth(force = false) {
    const now = Date.now();
    if (!force && apiHealthCache.ok !== null && now - apiHealthCache.checkedAt < API_CHECK_TTL_MS) {
        return apiHealthCache.ok;
    }

    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), API_CHECK_TIMEOUT_MS);
    try {
        const response = await fetch(API_HEALTH_URL, { signal: controller.signal });
        apiHealthCache.ok = response.ok;
    } catch (error) {
        apiHealthCache.ok = false;
    } finally {
        clearTimeout(timer);
        apiHealthCache.checkedAt = now;
        setApiStatus(apiHealthCache.ok);
    }

    return apiHealthCache.ok;
}

function setApiStatus(ok) {
    const statusEl = document.getElementById('project-status');
    if (!statusEl) return;
    statusEl.textContent = ok ? '后端已连? : '后端未连 ?;
}

function logApiEvent(type, endpoint, detail) {
    if (!API_LOGGING) return;
    const time = new Date().toISOString();
    const label = `[API] ${ type.toUpperCase() } ${ endpoint } `;
    if (type === 'error') {
        console.error(label, time, detail);
        return;
    }
    console.log(label, time, detail);
}

// ==================== 剧本编辑功能 ====================
function openScriptEditor() {
    const scriptContent = projectData.script?.content || '';
    const modal = document.getElementById('script-editor-modal');
    const textarea = document.getElementById('script-editor-textarea');

    if (!scriptContent) {
        alert('没有可编辑的剧本内容');
        return;
    }

    textarea.value = scriptContent;
    modal.style.display = 'flex';
    textarea.focus();
}

function closeScriptEditor() {
    const modal = document.getElementById('script-editor-modal');
    modal.style.display = 'none';
}

async function saveScriptEdits() {
    const textarea = document.getElementById('script-editor-textarea');
    const newContent = textarea.value.trim();

    if (!newContent) {
        alert('剧本内容不能为空');
        return;
    }

    showLoading('保存剧本?..');

    try {
        // 调用后端API保存编辑后的剧本
        const response = await apiCall(`${ API_BASE_URL }/update-script`, {
        project_id: projectId,
            content: newContent
    });

    if (response.success) {
        // 更新本地数据
        projectData.script.content = newContent;

        // 更新页面显示
        document.getElementById('script-content').textContent = newContent;

        // 关闭模态框
        closeScriptEditor();

        hideLoading();
        alert('剧本保存成功?);
        } else {
        throw new Error(response.message || '保存失败');
    }
} catch (error) {
    hideLoading();
    alert('保存剧本失败: ' + error.message);
}
}

async function regenerateScript() {
    if (!confirm('确定要重新生成剧本吗？当前的剧本内容将被覆盖?)) {
        return;
}

showLoading('重新生成剧本?..');

try {
    const response = await apiCall(`${API_BASE_URL}/generate-script`, {
