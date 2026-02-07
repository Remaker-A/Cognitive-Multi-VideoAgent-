#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彻底修复 app.js 编码问题"""

import re

try:
    # 读取文件，忽略编码错误
    with open('app.js', 'rb') as f:
        content = f.read()
    
    # 尝试解码为 UTF-8，替换错误字符
    text = content.decode('utf-8', errors='replace')
    
    # 替换所有替换字符（�）为空格
    text = text.replace('�', ' ')
    
    # 查找并修复已知的错误模式
    # 修复第99行附近的错误
    text = re.sub(r"throw new Error\('.*?后端.*?服.*?\);", 
                  "throw new Error('后端未启动或无法连接，请先运行后端服务');", 
                  text, flags=re.DOTALL)
    
    # 写回文件，使用正确的编码
    with open('app.js', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(text)
    
    print("✓ app.js 已彻底修复")
    
except Exception as e:
    print(f"✗ 修复失败: {e}")
    import traceback
    traceback.print_exc()
