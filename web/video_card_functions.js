// 新的视频卡片渲染函数 - 添加到 app.js 中

// 渲染单个视频卡片
function renderVideoCard(shotIndex, shot, videoUrl, status = 'loading') {
    const shotNum = shotIndex + 1;
    const container = document.getElementById('video-cards-grid');

    const cardHTML = `
        <div class="video-shot-card" id="video-card-${shotNum}" data-shot="${shotNum}">
            <div class="video-player-wrapper">
                ${status === 'success' && videoUrl ? `
                    <video controls class="video-player">
                        <source src="${videoUrl}" type="video/mp4">
                        您的浏览器不支持视频播放
                    </video>
                    <div class="video-overlay">
                        <button class="play-btn" onclick="toggleVideoPlay(${shotNum})">▶</button>
                    </div>
                ` : status === 'loading' ? `
                    <div class="video-placeholder loading">
                        <div class="loading-spinner"></div>
                        <p>生成中...</p>
                    </div>
                ` : `
                    <div class="video-placeholder error">
                        <div class="error-icon">❌</div>
                        <p>生成失败</p>
                    </div>
                `}
                <div class="video-badge">镜头 ${shotNum}</div>
            </div>
            
            <div class="video-shot-info">
                <h4 class="shot-title">${shot.title || `镜头 ${shotNum}`}</h4>
                <div class="shot-meta-row">
                    <span class="meta-tag">⏱️ ${shot.duration || 4}秒</span>
                    <span class="meta-tag">📹 ${shot.camera || '中景'}</span>
                    <span class="meta-tag">🎬 ${shot.movement || '静止'}</span>
                </div>
                <div class="shot-description">
                    ${shot.description || shot.scene || '暂无描述'}
                </div>
                
                <div class="shot-details-toggle" onclick="toggleShotInfo(${shotNum})">
                    <span class="toggle-text">查看详情</span>
                    <span class="toggle-icon">▼</span>
                </div>
                
                <div class="shot-details-panel" id="shot-details-${shotNum}" style="display: none;">
                    ${shot.visual_elements ? `
                        <div class="detail-item">
                            <label>🎨 视觉元素</label>
                            <p>${shot.visual_elements}</p>
                        </div>
                    ` : ''}
                    ${shot.characters ? `
                        <div class="detail-item">
                            <label>👤 角色</label>
                            <p>${shot.characters}</p>
                        </div>
                    ` : ''}
                    ${shot.action ? `
                        <div class="detail-item">
                            <label>🎭 动作</label>
                            <p>${shot.action}</p>
                        </div>
                    ` : ''}
                    ${shot.emotion ? `
                        <div class="detail-item">
                            <label>💫 情绪</label>
                            <p>${shot.emotion}</p>
                        </div>
                    ` : ''}
                </div>
                
                <div class="video-card-actions">
                    <button class="action-btn" onclick="downloadVideo(${shotNum}, '${videoUrl}')" ${!videoUrl ? 'disabled' : ''}>
                        📥 下载
                    </button>
                    <button class="action-btn" onclick="regenerateVideo(${shotNum})" ${status === 'loading' ? 'disabled' : ''}>
                        🔄 重新生成
                    </button>
                </div>
            </div>
        </div>
    `;

    // 如果卡片已存在,更新它;否则添加新卡片
    const existingCard = document.getElementById(`video-card-${shotNum}`);
    if (existingCard) {
        existingCard.outerHTML = cardHTML;
    } else {
        container.insertAdjacentHTML('beforeend', cardHTML);
    }
}

// 切换视频播放
function toggleVideoPlay(shotNum) {
    const card = document.getElementById(`video-card-${shotNum}`);
    const video = card.querySelector('video');
    if (video) {
        if (video.paused) {
            video.play();
        } else {
            video.pause();
        }
    }
}

// 切换分镜详情
function toggleShotInfo(shotNum) {
    const panel = document.getElementById(`shot-details-${shotNum}`);
    const card = document.getElementById(`video-card-${shotNum}`);
    const icon = card.querySelector('.toggle-icon');

    if (panel.style.display === 'none') {
        panel.style.display = 'block';
        icon.textContent = '▲';
    } else {
        panel.style.display = 'none';
        icon.textContent = '▼';
    }
}

// 下载单个视频
function downloadVideo(shotNum, videoUrl) {
    if (!videoUrl) return;
    const a = document.createElement('a');
    a.href = videoUrl;
    a.download = `shot-${shotNum}.mp4`;
    a.click();
}

// 重新生成单个视频
async function regenerateVideo(shotNum) {
    if (!confirm(`确定要重新生成镜头 ${shotNum} 的视频吗?`)) {
        return;
    }

    const shots = projectData.storyboard?.shots || [];
    const images = projectData.images || [];
    const shot = shots[shotNum - 1];
    const image = images[shotNum - 1];

    if (!shot || !image) {
        alert('缺少分镜或图像数据');
        return;
    }

    // 更新卡片为加载状态
    renderVideoCard(shotNum - 1, shot, null, 'loading');

    try {
        const response = await apiCall(`${API_BASE_URL}/generate-video`, {
            project_id: projectId,
            shot: shotNum,
            image_url: image.image_url,
            shot_info: shot
        });

        if (response.success && response.video_url) {
            // 更新卡片为成功状态
            renderVideoCard(shotNum - 1, shot, response.video_url, 'success');

            // 更新 projectData
            if (projectData.videoClips) {
                const clipIndex = projectData.videoClips.findIndex(c => c.shot === shotNum);
                if (clipIndex >= 0) {
                    projectData.videoClips[clipIndex].url = response.video_url;
                } else {
                    projectData.videoClips.push({
                        shot: shotNum,
                        url: response.video_url,
                        duration: shot.duration || 4
                    });
                }
            }

            alert('视频重新生成成功!');
        } else {
            renderVideoCard(shotNum - 1, shot, null, 'error');
            alert('视频生成失败');
        }
    } catch (error) {
        renderVideoCard(shotNum - 1, shot, null, 'error');
        alert('视频生成失败: ' + error.message);
    }
}
