// 将此代码添加到 app.js 文件末尾,替换原有的 generateVideo 函数

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
        document.getElementById('video-status').innerHTML = `
            <div class="status-text">正在生成视频片段...</div>
            <div class="progress-bar">
                <div class="progress-fill" id="video-progress-fill"></div>
            </div>
            <div class="progress-text" id="video-progress-text">0 / ${totalShots} 已完成</div>
        `;

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
                console.warn(`No image for shot ${i + 1}, skipping`);
                renderVideoCard(i, shot, null, 'error');
                continue;
            }

            try {
                console.log(`Generating video for shot ${i + 1}...`);

                const response = await apiCall(`${API_BASE_URL}/generate-video`, {
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
                    console.log(`Shot ${i + 1} video generated:`, response.video_url);
                } else {
                    renderVideoCard(i, shot, null, 'error');
                }

                // 更新进度
                document.getElementById('video-progress-fill').style.width = `${((i + 1) / totalShots) * 100}%`;
                document.getElementById('video-progress-text').textContent = `${i + 1} / ${totalShots} 已完成`;

            } catch (error) {
                console.error(`Video generation failed for shot ${i + 1}:`, error);
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
        alert(`成功生成 ${videoClips.length} 个视频片段!`);

    } catch (error) {
        hideLoading();
        alert('视频生成失败: ' + error.message);
        document.getElementById('video-status').style.display = 'none';
    }
}
