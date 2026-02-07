"""
测试 Admin CLI 工具

验证 CLI 工具的基本功能
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.admin_cli import AdminCLI
from src.agents.chef_agent.models import EventType
import asyncio


async def test_approve_command():
    """测试 approve 命令"""
    print("Testing approve command...")
    cli = AdminCLI()
    
    event = await cli.publish_user_decision_event(
        project_id="test_proj_001",
        action="approve",
        notes="Test approval",
        decided_by="test_user"
    )
    
    assert event.event_type == EventType.USER_APPROVED
    assert event.project_id == "test_proj_001"
    assert event.payload["decision"]["action"] == "approve"
    assert event.payload["decision"]["notes"] == "Test approval"
    print("✓ Approve command test passed\n")


async def test_reject_command():
    """测试 reject 命令"""
    print("Testing reject command...")
    cli = AdminCLI()
    
    event = await cli.publish_user_decision_event(
        project_id="test_proj_002",
        action="reject",
        notes="Test rejection",
        decided_by="test_user"
    )
    
    assert event.event_type == EventType.USER_REJECTED
    assert event.project_id == "test_proj_002"
    assert event.payload["decision"]["action"] == "reject"
    assert event.payload["decision"]["notes"] == "Test rejection"
    print("✓ Reject command test passed\n")


async def test_revise_command():
    """测试 revise 命令"""
    print("Testing revise command...")
    cli = AdminCLI()
    
    event = await cli.publish_user_decision_event(
        project_id="test_proj_003",
        action="revise",
        notes="Test revision request",
        decided_by="test_user"
    )
    
    assert event.event_type == EventType.USER_REVISION_REQUESTED
    assert event.project_id == "test_proj_003"
    assert event.payload["decision"]["action"] == "revise"
    assert event.payload["decision"]["notes"] == "Test revision request"
    print("✓ Revise command test passed\n")


def test_list_command():
    """测试 list 命令"""
    print("Testing list command...")
    cli = AdminCLI()
    
    # 添加测试项目
    cli.add_pending_project(
        project_id="test_proj_004",
        reason="Test reason",
        budget_info={
            "total": {"amount": 100.0, "currency": "USD"},
            "spent": {"amount": 80.0, "currency": "USD"},
            "estimated_remaining": {"amount": 20.0, "currency": "USD"}
        },
        context={"test": "data"}
    )
    
    assert "test_proj_004" in cli.pending_projects
    assert cli.pending_projects["test_proj_004"]["reason"] == "Test reason"
    print("✓ List command test passed\n")


def test_status_command():
    """测试 status 命令"""
    print("Testing status command...")
    cli = AdminCLI()
    
    # 添加测试项目
    cli.add_pending_project(
        project_id="test_proj_005",
        reason="Test reason",
        budget_info={
            "total": {"amount": 100.0, "currency": "USD"},
            "spent": {"amount": 90.0, "currency": "USD"},
            "estimated_remaining": {"amount": 10.0, "currency": "USD"}
        },
        context={"error_type": "TestError"}
    )
    
    project = cli.pending_projects["test_proj_005"]
    assert project["budget"]["spent"]["amount"] == 90.0
    assert project["context"]["error_type"] == "TestError"
    print("✓ Status command test passed\n")


async def run_all_tests():
    """运行所有测试"""
    print("=" * 50)
    print("Running Admin CLI Tests")
    print("=" * 50 + "\n")
    
    await test_approve_command()
    await test_reject_command()
    await test_revise_command()
    test_list_command()
    test_status_command()
    
    print("=" * 50)
    print("All tests passed! ✓")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
