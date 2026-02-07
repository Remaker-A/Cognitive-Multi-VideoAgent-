#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 app.js 中的编码问题"""

import re

# 修复策略：找到损坏的中文字符串，替换为正确的版本
replacements = {
    "鍚庣鏈惎鍔ㄦ垨鏃犳硶杩炴帴锛岃鍏堣繍琛屽悗绔湇": "后端未启动或无法连接，请先运行后端服务",
    "鍚庣鏈惎": "后端未启",
}

try:
    # 读取损坏的文件
    with open('app.js', 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # 替换所有损坏的字符串
    for bad, good in replacements.items():
        content = content.replace(bad, good)
    
    # 写回文件
    with open('app.js', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(content)
    
    print("✓ app.js 编码已修复")
    
except Exception as e:
    print(f"✗ 修复失败: {e}")
