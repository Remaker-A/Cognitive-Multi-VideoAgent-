#!/usr/bin/env python3
"""
Blackboard 快速验证脚本

验证 Blackboard 基础设施是否正常工作
"""

import sys
import time
from src.infrastructure.blackboard.factory import BlackboardFactory
from src.infrastructure.blackboard import (
    ProjectNotFoundError,
    ShotNotFoundError
)


def check_services():
    """检查服务是否可用"""
    print("=== Checking Services ===\n")
    
    try:
        blackboard = BlackboardFactory.create()
        
        # 检查 PostgreSQL
        print("✓ PostgreSQL connection: OK")
        
        # 检查 Redis
        if blackboard.redis.ping():
            print("✓ Redis connection: OK")
        else:
            print("✗ Redis connection: FAILED")
            return False
        
        print()
        return True
    except Exception as e:
        print(f"✗ Service check failed: {e}")
        return False


def test_basic_operations():
    """测试基本操作"""
    print("=== Testing Basic Operations ===\n")
    
    try:
        blackboard = BlackboardFactory.create()
        
        # 测试项目 ID
        test_project_id = f"TEST-{int(time.time())}"
        
        # 1. 创建项目
        print(f"1. Creating project {test_project_id}...")
        project = blackboard.create_project(
            project_id=test_project_id,
            global_spec={
                "title": "Test Project",
                "duration": 30,
                "aspect_ratio": "9:16"
            },
            budget={
                "total": 100.0,
                "used": 0.0,
                "remaining": 100.0
            }
        )
        print(f"   ✓ Project created: {project['project_id']}")
        
        # 2. 获取项目
        print(f"\n2. Getting project {test_project_id}...")
        project = blackboard.get_project(test_project_id)
        print(f"   ✓ Project retrieved: {project['project_id']}")
        print(f"   Status: {project['status']}")
        print(f"   Version: {project['version']}")
        
        # 3. 更新预算
        print(f"\n3. Adding cost...")
        blackboard.add_cost(test_project_id, 10.5, "Test cost")
        budget = blackboard.get_budget(test_project_id)
        print(f"   ✓ Cost added: ${budget['used']}")
        
        # 4. 更新项目状态
        print(f"\n4. Updating project status...")
        blackboard.update_project_status(test_project_id, "SHOT_PLANNING")
        project = blackboard.get_project(test_project_id)
        print(f"   ✓ Status updated: {project['status']}")
        
        # 5. 创建 Shot
        print(f"\n5. Creating shot...")
        shot_id = "S01"
        shot_data = {
            "shot_id": shot_id,
            "index": 1,
            "status": "INIT",
            "duration": 6,
            "script": {
                "description": "Test shot",
                "mood_tags": ["test"]
            }
        }
        blackboard.update_shot(test_project_id, shot_id, shot_data)
        shot = blackboard.get_shot(test_project_id, shot_id)
        print(f"   ✓ Shot created: {shot['shot_id']}")
        
        # 6. 更新 DNA Bank
        print(f"\n6. Updating DNA Bank...")
        character_id = "C1_test"
        dna_entry = {
            "embeddings": [{
                "version": 1,
                "weight": 1.0,
                "confidence": 0.88
            }],
            "merge_strategy": "weighted_average",
            "current_confidence": 0.88
        }
        blackboard.update_dna_bank(test_project_id, character_id, dna_entry)
        dna_bank = blackboard.get_dna_bank(test_project_id)
        print(f"   ✓ DNA Bank updated: {list(dna_bank.keys())}")
        
        print("\n=== All Tests Passed! ===\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_handling():
    """测试错误处理"""
    print("=== Testing Error Handling ===\n")
    
    try:
        blackboard = BlackboardFactory.create()
        
        # 测试获取不存在的项目
        print("1. Testing ProjectNotFoundError...")
        try:
            blackboard.get_project("NONEXISTENT")
            print("   ✗ Should have raised ProjectNotFoundError")
            return False
        except ProjectNotFoundError:
            print("   ✓ ProjectNotFoundError raised correctly")
        
        # 测试获取不存在的 Shot
        print("\n2. Testing ShotNotFoundError...")
        try:
            blackboard.get_shot("NONEXISTENT", "S99")
            print("   ✗ Should have raised ShotNotFoundError")
            return False
        except (ShotNotFoundError, ProjectNotFoundError):
            print("   ✓ Error raised correctly")
        
        print("\n=== Error Handling Tests Passed! ===\n")
        return True
        
    except Exception as e:
        print(f"\n✗ Error handling test failed: {e}")
        return False


def main():
    """主函数"""
    print("\n" + "="*50)
    print("  Blackboard Infrastructure Verification")
    print("="*50 + "\n")
    
    # 检查服务
    if not check_services():
        print("\n❌ Service check failed!")
        print("\nPlease ensure Docker services are running:")
        print("  docker-compose up -d")
        print("  bash scripts/init_blackboard.sh")
        sys.exit(1)
    
    # 测试基本操作
    if not test_basic_operations():
        print("\n❌ Basic operations test failed!")
        sys.exit(1)
    
    # 测试错误处理
    if not test_error_handling():
        print("\n❌ Error handling test failed!")
        sys.exit(1)
    
    print("="*50)
    print("  ✅ All Verifications Passed!")
    print("="*50 + "\n")
    
    print("Blackboard is ready to use! 🚀\n")
    sys.exit(0)


if __name__ == "__main__":
    main()
