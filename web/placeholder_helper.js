// 在 app.js 文件开头添加这个辅助函数

// 创建本地 SVG 占位图
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
