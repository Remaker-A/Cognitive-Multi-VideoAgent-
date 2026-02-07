"""
契约使用示例

展示如何在实际代码中使用契约模型,确保数据符合契约定义。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime
from src.contracts import (
    EventType,
    TaskType,
    Money,
    create_event,
    create_task,
    create_blackboard_request,
    create_blackboard_response,
    create_blackboard_error_response,
)


# ============================================================================
# 示例 1: 事件驱动流程
# ============================================================================

def example_event_driven_workflow():
    """示例：事件驱动的工作流"""
    print("=" * 60)
    print("示例 1: 事件驱动工作流")
    print("=" * 60)
    
    # 步骤 1: 创建项目事件
    project_created_event = create_event(
        event_id="evt_proj_001",
        project_id="proj_001",
        event_type=EventType.PROJECT_CREATED,
        actor="SystemAgent",
        payload={
            "project_name": "我的第一个视频项目",
            "description": "一个关于冒险的短视频",
        },
        cost=Money(amount=0.0, currency="USD"),
    )
    print(f"\n✅ 创建项目事件: {project_created_event.event_id}")
    print(f"   事件类型: {project_created_event.type}")
    print(f"   项目ID: {project_created_event.project_id}")
    
    # 步骤 2: 发布场景编写事件（链接到项目创建事件）
    scene_written_event = create_event(
        event_id="evt_scene_001",
        project_id="proj_001",
        event_type=EventType.SCENE_WRITTEN,
        actor="ScriptWriterAgent",
        payload={
            "scene_text": "一个勇敢的探险家在森林中发现了神秘的宝藏...",
            "word_count": 150,
        },
        causation_id=project_created_event.event_id,  # 因果链
        cost=Money(amount=0.02, currency="USD"),
        latency_ms=2500,
    )
    print(f"\n✅ 场景编写事件: {scene_written_event.event_id}")
    print(f"   因果链: {scene_written_event.causation_id} -> {scene_written_event.event_id}")
    
    # 步骤 3: 发布镜头规划事件
    shot_planned_event = create_event(
        event_id="evt_shot_001",
        project_id="proj_001",
        event_type=EventType.SHOT_PLANNED,
        actor="ShotPlannerAgent",
        payload={
            "shots": [
                {"shot_id": "S01", "description": "探险家走进森林"},
                {"shot_id": "S02", "description": "发现宝藏箱"},
            ],
        },
        causation_id=scene_written_event.event_id,
        blackboard_pointer="/projects/proj_001/shots",
        cost=Money(amount=0.01, currency="USD"),
    )
    print(f"\n✅ 镜头规划事件: {shot_planned_event.event_id}")
    print(f"   Blackboard 指针: {shot_planned_event.blackboard_pointer}")
    
    return [project_created_event, scene_written_event, shot_planned_event]


# ============================================================================
# 示例 2: 任务编排
# ============================================================================

def example_task_orchestration():
    """示例：任务编排"""
    print("\n" + "=" * 60)
    print("示例 2: 任务编排")
    print("=" * 60)
    
    # 任务 1: 生成关键帧（无依赖）
    task_keyframe = create_task(
        task_id="task_kf_001",
        project_id="proj_001",
        task_type=TaskType.GENERATE_KEYFRAME,
        assigned_to="ImageGeneratorAgent",
        input_data={
            "shot_id": "S01",
            "prompt": "探险家走进神秘的森林，阳光透过树叶",
            "style": "cinematic",
        },
        priority=4,
        estimated_cost=Money(amount=0.10, currency="USD"),
        causation_event_id="evt_shot_001",
    )
    print(f"\n✅ 创建任务: {task_keyframe.task_id}")
    print(f"   任务类型: {task_keyframe.type}")
    print(f"   分配给: {task_keyframe.assigned_to}")
    print(f"   优先级: {task_keyframe.priority}")
    
    # 任务 2: 运行视觉 QA（依赖于关键帧生成）
    task_qa = create_task(
        task_id="task_qa_001",
        project_id="proj_001",
        task_type=TaskType.RUN_VISUAL_QA,
        assigned_to="QAAgent",
        input_data={
            "shot_id": "S01",
            "keyframe_url": "s3://bucket/keyframe_S01.png",
        },
        priority=3,
        dependencies=[task_keyframe.task_id],  # 依赖关系
        estimated_cost=Money(amount=0.05, currency="USD"),
    )
    print(f"\n✅ 创建任务: {task_qa.task_id}")
    print(f"   依赖于: {task_qa.dependencies}")
    
    # 任务 3: 更新 DNA Bank（需要锁）
    task_dna = create_task(
        task_id="task_dna_001",
        project_id="proj_001",
        task_type=TaskType.UPDATE_DNA_BANK,
        assigned_to="DNAAgent",
        input_data={
            "character": "探险家",
            "features": {"face_embedding": [0.1, 0.2, 0.3]},
        },
        priority=5,
        requires_lock=True,
        lock_key="dna_bank",  # 锁定 DNA Bank
        estimated_cost=Money(amount=0.01, currency="USD"),
    )
    print(f"\n✅ 创建任务: {task_dna.task_id}")
    print(f"   需要锁: {task_dna.requires_lock}")
    print(f"   锁键: {task_dna.lock_key}")
    
    return [task_keyframe, task_qa, task_dna]


# ============================================================================
# 示例 3: Blackboard RPC 通信
# ============================================================================

def example_blackboard_rpc():
    """示例：Blackboard RPC 通信"""
    print("\n" + "=" * 60)
    print("示例 3: Blackboard RPC 通信")
    print("=" * 60)
    
    # 请求 1: 获取项目
    request_get_project = create_blackboard_request(
        request_id="req_001",
        method="get_project",
        params={"project_id": "proj_001"},
    )
    print(f"\n📤 发送请求: {request_get_project.method}")
    print(f"   请求ID: {request_get_project.id}")
    print(f"   参数: {request_get_project.params}")
    
    # 成功响应
    response_success = create_blackboard_response(
        request_id=request_get_project.id,
        result={
            "project": {
                "project_id": "proj_001",
                "name": "我的第一个视频项目",
                "status": "IN_PROGRESS",
            }
        },
    )
    print(f"\n📥 收到响应: OK={response_success.ok}")
    print(f"   结果: {response_success.result}")
    
    # 请求 2: 更新镜头（模拟错误）
    request_update_shot = create_blackboard_request(
        request_id="req_002",
        method="update_shot",
        params={
            "project_id": "proj_001",
            "shot_id": "S99",  # 不存在的镜头
            "updates": {"status": "APPROVED"},
        },
    )
    print(f"\n📤 发送请求: {request_update_shot.method}")
    
    # 错误响应
    response_error = create_blackboard_error_response(
        request_id=request_update_shot.id,
        error_code="SHOT_NOT_FOUND",
        error_message="镜头 S99 不存在",
        error_details={
            "project_id": "proj_001",
            "shot_id": "S99",
        },
    )
    print(f"\n📥 收到错误响应: OK={response_error.ok}")
    print(f"   错误代码: {response_error.error.code}")
    print(f"   错误消息: {response_error.error.message}")
    print(f"   错误详情: {response_error.error.details}")
    
    return [request_get_project, response_success, request_update_shot, response_error]


# ============================================================================
# 示例 4: 数据序列化和验证
# ============================================================================

def example_serialization_and_validation():
    """示例：数据序列化和验证"""
    print("\n" + "=" * 60)
    print("示例 4: 数据序列化和验证")
    print("=" * 60)
    
    # 创建事件
    event = create_event(
        event_id="evt_test_001",
        project_id="proj_001",
        event_type=EventType.IMAGE_GENERATED,
        actor="ImageGeneratorAgent",
        payload={"image_url": "s3://bucket/image.png"},
        cost=Money(amount=0.08, currency="USD"),
    )
    
    # 序列化为字典
    event_dict = event.dict()
    print(f"\n📦 序列化为字典:")
    print(f"   event_id: {event_dict['event_id']}")
    print(f"   type: {event_dict['type']}")
    print(f"   timestamp: {event_dict['timestamp']}")
    
    # 序列化为 JSON
    event_json = event.json(indent=2)
    print(f"\n📦 序列化为 JSON:")
    print(event_json[:200] + "...")
    
    # Pydantic 自动验证
    print(f"\n✅ Pydantic 自动验证通过")
    print(f"   所有字段类型正确")
    print(f"   所有必需字段存在")
    print(f"   枚举值在允许范围内")


# ============================================================================
# 主函数
# ============================================================================

def main():
    """运行所有示例"""
    print("\n" + "🎬" * 30)
    print("契约使用示例")
    print("🎬" * 30)
    
    # 运行示例
    example_event_driven_workflow()
    example_task_orchestration()
    example_blackboard_rpc()
    example_serialization_and_validation()
    
    print("\n" + "=" * 60)
    print("✅ 所有示例运行完成")
    print("=" * 60)
    print("\n💡 提示:")
    print("   - 所有数据都符合 contracts 目录中定义的 JSON Schema")
    print("   - Pydantic 模型提供运行时类型验证")
    print("   - 使用辅助函数确保数据结构正确")
    print("   - 事件因果链追踪系统行为")
    print("   - 任务依赖确保执行顺序")
    print()


if __name__ == "__main__":
    main()
