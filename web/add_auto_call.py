#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在 HTML 中添加自动调用脚本"""

try:
    with open('index.html', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 在 shot-editor.js 和 storyboard-display-helper.js 之后添加自动调用脚本
    auto_call_script = '''
    <script>
        // 自动调用分镜操作按钮添加函数
        // 监听 DOM 变化，当分镜列表出现时自动添加操作按钮
        document.addEventListener('DOMContentLoaded', function() {
            // 使用 MutationObserver 监听分镜列表的变化
            const observer = new MutationObserver(function(mutations) {
                const storyboardList = document.getElementById('storyboard-list');
                if (storyboardList && storyboardList.children.length > 0) {
                    // 检查是否已添加操作按钮
                    const firstCard = storyboardList.querySelector('.shot-card');
                    if (firstCard && !firstCard.querySelector('.shot-actions')) {
                        console.log('检测到分镜列表，正在添加操作按钮...');
                        if (typeof addStoryboardActions === 'function') {
                            addStoryboardActions();
                        }
                    }
                }
            });
            
            // 开始观察 document.body
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        });
    </script>'''
    
    # 在 </body> 之前插入
    content = content.replace('</body>', auto_call_script + '\n</body>')
    
    # 写回文件
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ 自动调用脚本已添加到 index.html")
    
except Exception as e:
    print(f"✗ 失败: {e}")
