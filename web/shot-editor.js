// ==================== 分镜编辑功能 ====================

let currentEditingShot = null;
let isAddingNewShot = false;

function editShot(shotNum) {
    const shot = projectData.storyboard.shots[shotNum - 1];
    if (!shot) {
        alert('分镜不存在');
        return;
    }

    currentEditingShot = shotNum;
    isAddingNewShot = false;

    // 填充表单
    document.getElementById('edit-shot-number').textContent = shotNum;
    document.getElementById('edit-scene').value = shot.scene || '';
    document.getElementById('edit-characters').value = shot.characters || '';
    document.getElementById('edit-action').value = shot.action || '';
    document.getElementById('edit-visual-elements').value = shot.visual_elements || '';
    document.getElementById('edit-camera').value = shot.camera || '中景';
    document.getElementById('edit-angle').value = shot.angle || '平视';
    document.getElementById('edit-movement').value = shot.movement || '静止';
    document.getElementById('edit-transition').value = shot.transition || '切';
    document.getElementById('edit-emotion').value = shot.emotion || '';
    document.getElementById('edit-duration').value = shot.duration || 4;

    // 显示模态框
    document.getElementById('shot-edit-modal').style.display = 'flex';
}

function deleteShot(shotNum) {
    if (!confirm(`确定要删除镜头 ${shotNum} 吗？`)) {
        return;
    }

    // 从数组中删除
    projectData.storyboard.shots.splice(shotNum - 1, 1);

    // 重新编号
    projectData.storyboard.shots.forEach((shot, index) => {
        shot.shot_id = index + 1;
    });

    // 更新总镜头数
    projectData.storyboard.total_shots = projectData.storyboard.shots.length;

    // 重新渲染
    displayStoryboard(projectData.storyboard);

    alert('镜头已删除');
}

function addNewShot() {
    const newShotNum = projectData.storyboard.shots.length + 1;

    currentEditingShot = newShotNum;
    isAddingNewShot = true;

    // 清空表单
    document.getElementById('edit-shot-number').textContent = newShotNum;
    document.getElementById('edit-scene').value = '';
    document.getElementById('edit-characters').value = '';
    document.getElementById('edit-action').value = '';
    document.getElementById('edit-visual-elements').value = '';
    document.getElementById('edit-camera').value = '中景';
    document.getElementById('edit-angle').value = '平视';
    document.getElementById('edit-movement').value = '静止';
    document.getElementById('edit-transition').value = '切';
    document.getElementById('edit-emotion').value = '';
    document.getElementById('edit-duration').value = 4;

    // 显示模态框
    document.getElementById('shot-edit-modal').style.display = 'flex';
}

function closeEditModal() {
    document.getElementById('shot-edit-modal').style.display = 'none';
    currentEditingShot = null;
    isAddingNewShot = false;
}

function confirmEditShot() {
    // 获取表单数据
    const updatedShot = {
        shot_id: currentEditingShot,
        scene: document.getElementById('edit-scene').value.trim(),
        characters: document.getElementById('edit-characters').value.trim(),
        action: document.getElementById('edit-action').value.trim(),
        visual_elements: document.getElementById('edit-visual-elements').value.trim(),
        camera: document.getElementById('edit-camera').value,
        angle: document.getElementById('edit-angle').value,
        movement: document.getElementById('edit-movement').value,
        transition: document.getElementById('edit-transition').value,
        emotion: document.getElementById('edit-emotion').value.trim(),
        duration: parseInt(document.getElementById('edit-duration').value) || 4
    };

    // 验证必填字段
    if (!updatedShot.scene || !updatedShot.action) {
        alert('场景和动作不能为空');
        return;
    }

    if (isAddingNewShot) {
        // 添加新分镜
        projectData.storyboard.shots.push(updatedShot);
        projectData.storyboard.total_shots = projectData.storyboard.shots.length;
    } else {
        // 更新现有分镜
        projectData.storyboard.shots[currentEditingShot - 1] = updatedShot;
    }

    // 关闭模态框
    closeEditModal();

    // 重新渲染分镜列表
    displayStoryboard(projectData.storyboard);

    alert(isAddingNewShot ? '新分镜已添加' : '分镜已更新');
}
