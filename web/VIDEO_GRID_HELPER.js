// 添加到 app.js 中 generateVideo 函数之前的辅助函数

// 初始化视频网格
function initializeVideoGrid(totalShots) {
    const grid = document.getElementById('videos-grid');
    grid.innerHTML = '';

    for (let i = 1; i <= totalShots; i++) {
        grid.innerHTML += `
            <div class="video-card" id="video-${i}">
                <div class="video-preview">
                    <div class="status-icon loading">⏳</div>
                </div>
                <div class="video-info">
                    <div class="video-title">镜头 ${i}</div>
                    <div class="video-status">生成中...</div>
                </div>
            </div>
        `;
    }
}

// 更新视频卡片状态
function updateVideoCard(shotNum, videoUrl, status = 'success') {
    const card = document.getElementById(`video-${shotNum}`);
    if (!card) return;

    if (status === 'success' && videoUrl) {
        card.querySelector('.video-preview').innerHTML = `
            <video controls>
                <source src="${videoUrl}" type="video/mp4">
                您的浏览器不支持视频播放
            </video>
        `;
        card.querySelector('.video-status').textContent = '已完成';
    } else if (status === 'error') {
        card.querySelector('.video-preview').innerHTML = `<div class="status-icon error">❌</div>`;
        card.querySelector('.video-status').textContent = '生成失败';
    } else if (status === 'skip') {
        card.querySelector('.video-preview').innerHTML = `<div class="status-icon error">❌</div>`;
        card.querySelector('.video-status').textContent = '跳过（无参考图）';
    }
}

// 在 generateVideo 函数开始时调用：
// initializeVideoGrid(totalShots);

// 在视频生成成功时调用：
// updateVideoCard(i + 1, response.video_url, 'success');

// 在视频生成失败时调用：
// updateVideoCard(i + 1, null, 'error');
