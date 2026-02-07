#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复损坏的 web 文件"""

# 修复 index.html - 在 </body> 之前添加 script 标签
try:
    with open('index.html.corrupted', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 查找 </body> 标签并在之前插入 script 标签
    if '</body>' in content:
        script_tags = '''
    <script src="shot-editor.js"></script>
    <script src="storyboard-display-helper.js"></script>
</body>'''
        content = content.replace('</body>', script_tags)
        
        # 写入修复后的文件
        with open('index.html', 'w', encoding='utf-8', newline='\r\n') as f:
            f.write(content)
        print("✓ index.html 已修复")
    else:
        print("✗ 找不到 </body> 标签")
except Exception as e:
    print(f"✗ 修复 index.html 失败: {e}")

# app.js 不需要修改，只需要确保编码正确
try:
    with open('app.js.corrupted', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 重新以正确编码写入
    with open('app.js', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)
    print("✓ app.js 已修复")
except Exception as e:
    print(f"✗ 修复 app.js 失败: {e}")

print("\n完成！请刷新浏览器测试。")
