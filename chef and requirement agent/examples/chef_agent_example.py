"""
ChefAgent 使用示例

演示如何使用 ChefAgent 处理项目事件
"""

import asyncio
from datetime import datetime
from src.agents.chef_agent import ChefAgent
from src.agents.chef_agent.models import Event, EventType, Money


async def main():
    """主函数"""
    print("=" * 60)
    print("ChefAgent 使用示例")
    print("=" * 60)
    
    # 1. 创建 ChefAgent 实例
    print("\n1. 初始化 ChefAgent...")
    agent = ChefAgent()
    print(f"   ✓ ChefAgent 初始化成功")
    print(f"   ✓ 订阅了 {len(agent.get_subscribed_events())} 个事件类型")
    
    # 2. 处理 PROJECT_CREATED 事件
    print("\n2. 处理 PROJECT_CREATED 事件...")
    project_id = "proj_demo_001"
    
    create_event = Event(
        event_id="evt_001",
        project_id=project_id,
        event_type=EventType.PROJECT_CREATED,
        actor="Orchestrator",
        payload={
            "duration": 60.0,  # 60 秒视频
            "quality_tier": "high"  # 高质量档位
        },
        timestamp=datetime.now().isoformat()
    )
    
    await agent.handle_event(create_event)
    
    project_data = agent._project_cache.get(project_id)
    print(f"   ✓ 项目创建成功")
    print(f"   ✓ 总预算: ${project_data['budget'].total.amount:.2f}")
    print(f"   ✓ 质量档位: {project_data['quality_tier']}")
    print(f"   ✓ 项目状态: {project_data['status']}")
    
    # 3. 处理成本事件
    print("\n3. 处理成本事件...")
    
    # 图像生成
    image_event = Event(
        event_id="evt_002",
        project_id=project_id,
        event_type=EventType.IMAGE_GENERATED,
        actor="ImageAgent",
        payload={},
        timestamp=datetime.now().isoformat(),
        cost=Money(amount=15.0, currency="USD")
    )
    await agent.handle_event(image_event)
    
    project_data = agent._project_cache.get(project_id)
    print(f"   ✓ 图像生成成本: $15.00")
    print(f"   ✓ 已使用预算: ${project_data['budget'].spent.amount:.2f}")
    print(f"   ✓ 预算使用率: {project_data['budget'].spent.amount / project_data['budget'].total.amount * 100:.1f}%")
    
    # 视频生成
    video_event = Event(
        event_id="evt_003",
        project_id=project_id,
        event_type=EventType.VIDEO_GENERATED,
        actor="VideoAgent",
        payload={"duration": 60.0},
        timestamp=datetime.now().isoformat(),
        cost=Money(amount=50.0, currency="USD")
    )
    await agent.handle_event(video_event)
    
    project_data = agent._project_cache.get(project_id)
    print(f"   ✓ 视频生成成本: $50.00")
    print(f"   ✓ 已使用预算: ${project_data['budget'].spent.amount:.2f}")
    print(f"   ✓ 预算使用率: {project_data['budget'].spent.amount / project_data['budget'].total.amount * 100:.1f}%")
    
    # 4. 触发预算预警
    print("\n4. 触发预算预警...")
    
    # 添加更多成本，触发预警
    music_event = Event(
        event_id="evt_004",
        project_id=project_id,
        event_type=EventType.MUSIC_COMPOSED,
        actor="MusicAgent",
        payload={"duration": 60.0},
        timestamp=datetime.now().isoformat(),
        cost=Money(amount=150.0, currency="USD")
    )
    await agent.handle_event(music_event)
    
    project_data = agent._project_cache.get(project_id)
    print(f"   ✓ 音乐生成成本: $150.00")
    print(f"   ✓ 已使用预算: ${project_data['budget'].spent.amount:.2f}")
    print(f"   ✓ 预算使用率: {project_data['budget'].spent.amount / project_data['budget'].total.amount * 100:.1f}%")
    
    # 检查是否发布了预警事件
    events = agent.event_manager.get_published_events()
    warning_events = [e for e in events if e.event_type == EventType.COST_OVERRUN_WARNING]
    if warning_events:
        print(f"   ⚠ 预算预警已触发！")
    
    # 5. 处理失败事件
    print("\n5. 处理失败事件...")
    
    failed_event = Event(
        event_id="evt_005",
        project_id=project_id,
        event_type=EventType.CONSISTENCY_FAILED,
        actor="ConsistencyAgent",
        payload={
            "task_id": "task_001",
            "error_type": "APIError",
            "error_message": "API timeout after 3 retries",
            "retry_count": 3,
            "cost_impact": 10.0,
            "severity": "high"
        },
        timestamp=datetime.now().isoformat()
    )
    await agent.handle_event(failed_event)
    
    project_data = agent._project_cache.get(project_id)
    print(f"   ✓ 失败事件已处理")
    print(f"   ✓ 项目状态: {project_data['status']}")
    
    if project_data.get('human_gate_request'):
        request = project_data['human_gate_request']
        print(f"   ⚠ 人工介入已触发！")
        print(f"   ⚠ 请求 ID: {request.request_id}")
        print(f"   ⚠ 触发原因: {request.reason}")
    
    # 6. 查看所有发布的事件
    print("\n6. 查看所有发布的事件...")
    all_events = agent.event_manager.get_published_events()
    print(f"   ✓ 共发布了 {len(all_events)} 个事件:")
    for i, event in enumerate(all_events, 1):
        print(f"      {i}. {event.event_type.value} (ID: {event.event_id})")
    
    print("\n" + "=" * 60)
    print("示例完成！")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
