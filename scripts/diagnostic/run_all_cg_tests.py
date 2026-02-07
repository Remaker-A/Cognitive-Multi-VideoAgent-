"""
完整测试套件运行脚本
"""
import sys
import os

# 设置 Python 路径
sys.path.insert(0, r'd:\文档\Kiro\VIdeoGen')

import pytest

if __name__ == "__main__":
    print("=" * 80)
    print("ConsistencyGuardian 测试套件")
    print("=" * 80)
    
    # 运行所有测试
    exit_code = pytest.main([
        'tests/agents/consistency_guardian/',
        '-v',
        '--tb=short',
        '-q',
        '--no-header',
        '--color=yes'
    ])
    
    print("\n" + "=" * 80)
    print(f"测试完成 - 退出码: {exit_code}")
    print("=" * 80)
    
    if exit_code == 0:
        print("✅ 所有测试通过！")
    else:
        print(f"❌ 测试失败，退出码: {exit_code}")
    
    sys.exit(exit_code)
