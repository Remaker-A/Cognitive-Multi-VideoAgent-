// 分镜显示辅助函数 - 添加操作按钮
function addStoryboardActions() {
    // 为每个分镜卡片添加操作按钮
    const shotCards = document.querySelectorAll('.shot-card');
    shotCards.forEach((card, index) => {
        const shotNum = index + 1;

        // 检查是否已添加操作按钮
        if (card.querySelector('.shot-actions')) {
            return;
        }

        // 创建操作按钮容器
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'shot-actions';
        actionsDiv.innerHTML = `
            <button onclick="editShot(${shotNum})">✏️ 编辑</button>
            <button class="delete-btn" onclick="deleteShot(${shotNum})">🗑️ 删除</button>
        `;

        // 添加到卡片
        card.appendChild(actionsDiv);
    });

    // 添加"添加新分镜"按钮到头部
    const header = document.querySelector('.storyboard-header');
    if (header && !document.querySelector('.storyboard-actions')) {
        const actionsDiv = document.createElement('div');
        actionsDiv.className = 'storyboard-actions';
        actionsDiv.innerHTML = '<button class="btn-secondary" onclick="addNewShot()">➕ 添加新分镜</button>';
        header.appendChild(actionsDiv);
    }
}

// 在分镜显示后调用此函数
// 可以在生成分镜后的代码中添加：addStoryboardActions();
