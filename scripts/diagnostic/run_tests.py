"""
测试运行脚本
"""
import sys
import os

# 设置 Python 路径
sys.path.insert(0, r'd:\文档\Kiro\VIdeoGen')

# 运行 pytest
import pytest

if __name__ == "__main__":
    # 运行测试
    exit_code = pytest.main([
        'tests/agents/consistency_guardian/test_threshold_manager.py',
        '-v',
        '--tb=short',
        '--no-header'
    ])
    
    print(f"\n测试退出码: {exit_code}")
    sys.exit(exit_code)
