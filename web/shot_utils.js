// 切换分镜详情显示/隐藏
function toggleShotDetails(shotNum) {
    const card = document.querySelector(`.shot-card[data-shot="${shotNum}"]`);
    if (!card) return;

    const body = card.querySelector('.shot-body');
    const icon = card.querySelector('.expand-icon');

    if (body.style.display === 'none' || !body.style.display) {
        body.style.display = 'block';
        icon.textContent = '▲';
        card.classList.add('expanded');
    } else {
        body.style.display = 'none';
        icon.textContent = '▼';
        card.classList.remove('expanded');
    }
}
