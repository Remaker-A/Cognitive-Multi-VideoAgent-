#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""彻底清理所有损坏的 Web 文件"""

import re
import os

def clean_file(filepath):
    """清理文件中的所有替换字符和损坏的编码"""
    try:
        # 读取文件为字节
        with open(filepath, 'rb') as f:
            raw_bytes = f.read()
        
        # 尝试多种编码解码
        text = None
        for encoding in ['utf-8', 'gbk', 'gb2312', 'latin-1']:
            try:
                text = raw_bytes.decode(encoding, errors='ignore')
                break
            except:
                continue
        
        if not text:
            print(f"✗ 无法解码 {filepath}")
            return False
        
        # 移除所有不可打印字符（保留换行和制表符）
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        
        # 移除 Unicode 替换字符
        text = text.replace('�', '')
        text = text.replace('\ufffd', '')
        
        # 写回文件，使用 UTF-8-BOM 确保兼容性
        with open(filepath, 'w', encoding='utf-8-sig', newline='\r\n') as f:
            f.write(text)
        
        print(f"✓ {filepath} 已清理")
        return True
        
    except Exception as e:
        print(f"✗ 清理 {filepath} 失败: {e}")
        return False

# 清理所有 web 文件
files_to_clean = ['index.html', 'app.js']

print("开始清理损坏的文件...")
for filename in files_to_clean:
    if os.path.exists(filename):
        clean_file(filename)
    else:
        print(f"⚠ {filename} 不存在")

print("\n清理完成！")
