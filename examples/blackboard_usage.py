"""
Shared Blackboard 使用示例
"""

from src.infrastructure.blackboard import SharedBlackboard
from src.infrastructure.blackboard.factory import BlackboardFactory
from src.infrastructure.blackboard.config import BlackboardConfig


def example_basic_usage():
    """基础使用示例"""
    # 方式 1: 使用工厂创建（推荐）
    blackboard = BlackboardFactory.create()
    
    # 方式 2: 手动创建
    # config = BlackboardConfig.from_env()
    # blackboard = BlackboardFactory.create(config)
    
    # 创建项目
    project_id = "PROJ-2025-001"
    global_spec = {
        "title": "Rain and Warmth",
        "duration": 30,
        "aspect_ratio": "9:16",
        "quality_tier": "balanced"
    }
    budget = {
        "total": 90.0,
        "used": 0.0,
        "remaining": 90.0
    }
    
    project = blackboard.create_project(project_id, global_spec, budget)
    print(f"Created project: {project['project_id']}")
    
    # 获取项目
    project = blackboard.get_project(project_id)
    print(f"Retrieved project: {project['project_id']}, status: {project['status']}")
    
    # 更新预算
    budget = blackboard.get_budget(project_id)
    print(f"Current budget: {budget}")
    
    # 增加成本
    blackboard.add_cost(project_id, 10.5, "Image generation for S01")
    print("Added cost: $10.5")
    
    # 更新项目状态
    blackboard.update_project_status(project_id, "SHOT_PLANNING")
    print("Updated project status to SHOT_PLANNING")


def example_shot_operations():
    """Shot 操作示例"""
    blackboard = BlackboardFactory.create()
    project_id = "PROJ-2025-001"
    
    # 创建 shot
    shot_id = "S01"
    shot_data = {
        "shot_id": shot_id,
        "index": 1,
        "status": "INIT",
        "duration": 6,
        "script": {
            "description": "Rainy street, girl walks alone",
            "mood_tags": ["lonely", "soft"]
        }
    }
    
    # 更新 shot
    blackboard.update_shot(project_id, shot_id, shot_data)
    print(f"Created shot: {shot_id}")
    
    # 获取 shot
    shot = blackboard.get_shot(project_id, shot_id)
    print(f"Retrieved shot: {shot['shot_id']}, status: {shot['status']}")
    
    # 更新 shot 状态
    shot['status'] = "KEYFRAME_GENERATED"
    blackboard.update_shot(project_id, shot_id, shot)
    print(f"Updated shot status to KEYFRAME_GENERATED")
    
    # 获取所有 shots
    all_shots = blackboard.get_all_shots(project_id)
    print(f"Total shots: {len(all_shots)}")


def example_dna_bank():
    """DNA Bank 操作示例"""
    blackboard = BlackboardFactory.create()
    project_id = "PROJ-2025-001"
    
    # 更新 DNA Bank
    character_id = "C1_girl"
    dna_entry = {
        "embeddings": [
            {
                "version": 1,
                "weight": 1.0,
                "source": "S01_keyframe_mid",
                "confidence": 0.88,
                "timestamp": "2025-11-16T10:05:00Z"
            }
        ],
        "merge_strategy": "weighted_average",
        "current_confidence": 0.88
    }
    
    blackboard.update_dna_bank(project_id, character_id, dna_entry)
    print(f"Updated DNA Bank for {character_id}")
    
    # 获取 DNA Bank
    dna_bank = blackboard.get_dna_bank(project_id)
    print(f"DNA Bank: {list(dna_bank.keys())}")


def example_artifact_registration():
    """Artifact 注册示例"""
    blackboard = BlackboardFactory.create()
    project_id = "PROJ-2025-001"
    
    # 注册 artifact
    artifact_url = "s3://artifacts/PROJ-001/S01_start.png"
    metadata = {
        "seed": 123456,
        "model": "sdxl-1.0",
        "model_version": "1.0.2",
        "prompt": "A girl walking in the rain...",
        "cost": 0.02,
        "type": "image",
        "params": {"steps": 30, "cfg_scale": 7.5}
    }
    
    blackboard.register_artifact(project_id, artifact_url, metadata)
    print(f"Registered artifact: {artifact_url}")


def example_with_lock():
    """使用分布式锁示例"""
    from src.infrastructure.blackboard import DistributedLock
    
    blackboard = BlackboardFactory.create()
    project_id = "PROJ-2025-001"
    
    # 使用上下文管理器自动管理锁
    with DistributedLock(blackboard.redis, f"project:{project_id}:global_style"):
        # 在锁保护下更新全局样式
        global_spec = blackboard.get_global_spec(project_id)
        global_spec['style']['palette'] = ["#2b3a67", "#cfa66b"]
        blackboard.update_global_spec(project_id, global_spec)
        print("Updated global style with lock protection")


def example_error_handling():
    """错误处理示例"""
    from src.infrastructure.blackboard import (
        ProjectNotFoundError,
        ShotNotFoundError,
        LockAcquisitionError
    )
    
    blackboard = BlackboardFactory.create()
    
    try:
        # 尝试获取不存在的项目
        project = blackboard.get_project("NONEXISTENT")
    except ProjectNotFoundError as e:
        print(f"Caught ProjectNotFoundError: {e}")
    
    try:
        # 尝试获取不存在的 shot
        shot = blackboard.get_shot("PROJ-001", "S99")
    except ShotNotFoundError as e:
        print(f"Caught ShotNotFoundError: {e}")


if __name__ == "__main__":
    print("=== Blackboard Usage Examples ===\n")
    
    print("1. Basic Usage")
    example_basic_usage()
    print()
    
    print("2. Shot Operations")
    example_shot_operations()
    print()
    
    print("3. DNA Bank")
    example_dna_bank()
    print()
    
    print("4. Artifact Registration")
    example_artifact_registration()
    print()
    
    print("5. With Lock")
    example_with_lock()
    print()
    
    print("6. Error Handling")
    example_error_handling()
    print()
    
    print("=== Examples Complete ===")
