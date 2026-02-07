#!/usr/bin/env python3
"""
ChefAgent Admin CLI 工具

用于在开发环境中模拟人工决策，测试 ChefAgent 的人工介入流程。

Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6
"""

import argparse
import sys
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.chef_agent.models import (
    Event,
    EventType,
    UserDecision,
    Money
)
from src.agents.chef_agent.event_manager import EventManager


class AdminCLI:
    """
    Admin CLI 工具
    
    提供命令行界面用于:
    - 发布人工决策事件 (approve, reject, revise)
    - 查询待审批项目列表
    - 查询项目详情和预算使用情况
    """
    
    def __init__(self):
        """初始化 CLI 工具"""
        self.event_manager = EventManager(agent_name="AdminCLI")
        # 在实际环境中，这里应该连接到真实的 Blackboard 和 EventBus
        # 目前使用内存存储进行开发测试
        self.pending_projects: Dict[str, Dict[str, Any]] = {}
    
    def generate_event_id(self) -> str:
        """生成唯一的事件 ID"""
        return f"evt_{uuid.uuid4().hex[:12]}"
    
    async def publish_user_decision_event(
        self,
        project_id: str,
        action: str,
        notes: Optional[str] = None,
        decided_by: str = "admin"
    ) -> Event:
        """
        发布用户决策事件
        
        Args:
            project_id: 项目 ID
            action: 决策操作 (approve, reject, revise)
            notes: 决策备注
            decided_by: 决策人
            
        Returns:
            发布的事件对象
        """
        event_id = self.generate_event_id()
        
        # 创建用户决策对象
        decision = UserDecision(
            action=action,
            notes=notes,
            decided_at=datetime.now(),
            decided_by=decided_by
        )
        
        # 确定事件类型
        event_type_map = {
            "approve": EventType.USER_APPROVED,
            "reject": EventType.USER_REJECTED,
            "revise": EventType.USER_REVISION_REQUESTED
        }
        event_type = event_type_map.get(action, EventType.USER_APPROVED)
        
        # 构建事件 payload
        payload = {
            "decision": {
                "action": decision.action,
                "notes": decision.notes,
                "decided_at": decision.decided_at.isoformat(),
                "decided_by": decision.decided_by
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # 创建事件
        event = Event(
            event_id=event_id,
            project_id=project_id,
            event_type=event_type,
            actor="AdminCLI",
            payload=payload,
            causation_id=None,  # 人工决策是起始事件
            timestamp=datetime.now().isoformat(),
            cost=None,
            latency_ms=None,
            metadata={}
        )
        
        print(f"✓ Published {event_type.value} event")
        print(f"  Event ID: {event_id}")
        print(f"  Project ID: {project_id}")
        print(f"  Action: {action}")
        if notes:
            print(f"  Notes: {notes}")
        
        return event
    
    def add_pending_project(
        self,
        project_id: str,
        reason: str,
        budget_info: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        添加待审批项目（用于测试）
        
        Args:
            project_id: 项目 ID
            reason: 触发人工介入的原因
            budget_info: 预算信息
            context: 上下文信息
        """
        self.pending_projects[project_id] = {
            "project_id": project_id,
            "reason": reason,
            "budget": budget_info,
            "context": context,
            "created_at": datetime.now().isoformat()
        }
    
    def list_pending_projects(self) -> None:
        """
        列出所有待审批项目
        
        Requirements: 11.5
        """
        if not self.pending_projects:
            print("No pending projects for approval.")
            return
        
        print("\n=== Pending Projects ===\n")
        for project_id, info in self.pending_projects.items():
            print(f"Project ID: {project_id}")
            print(f"  Reason: {info['reason']}")
            print(f"  Created: {info['created_at']}")
            
            # 显示预算信息
            budget = info.get('budget', {})
            if budget:
                spent = budget.get('spent', {}).get('amount', 0)
                total = budget.get('total', {}).get('amount', 0)
                usage_rate = (spent / total * 100) if total > 0 else 0
                print(f"  Budget: ${spent:.2f} / ${total:.2f} ({usage_rate:.1f}%)")
            
            print()
    
    def show_project_status(self, project_id: str) -> None:
        """
        显示项目详细状态
        
        Args:
            project_id: 项目 ID
            
        Requirements: 11.6
        """
        if project_id not in self.pending_projects:
            print(f"Error: Project {project_id} not found in pending list.")
            return
        
        info = self.pending_projects[project_id]
        
        print(f"\n=== Project Status: {project_id} ===\n")
        print(f"Reason for Review: {info['reason']}")
        print(f"Created At: {info['created_at']}")
        
        # 显示预算详情
        budget = info.get('budget', {})
        if budget:
            print("\nBudget Information:")
            total = budget.get('total', {})
            spent = budget.get('spent', {})
            remaining = budget.get('estimated_remaining', {})
            
            print(f"  Total Budget: ${total.get('amount', 0):.2f} {total.get('currency', 'USD')}")
            print(f"  Spent: ${spent.get('amount', 0):.2f} {spent.get('currency', 'USD')}")
            print(f"  Remaining: ${remaining.get('amount', 0):.2f} {remaining.get('currency', 'USD')}")
            
            if total.get('amount', 0) > 0:
                usage_rate = spent.get('amount', 0) / total.get('amount', 1) * 100
                print(f"  Usage Rate: {usage_rate:.1f}%")
        
        # 显示上下文信息
        context = info.get('context', {})
        if context:
            print("\nContext Information:")
            for key, value in context.items():
                print(f"  {key}: {value}")
        
        print()


def create_parser() -> argparse.ArgumentParser:
    """
    创建命令行参数解析器
    
    Requirements: 11.1
    """
    parser = argparse.ArgumentParser(
        description="ChefAgent Admin CLI - Manage human intervention decisions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Approve a project
  python tools/admin_cli.py approve proj_123 --notes "Looks good"
  
  # Reject a project
  python tools/admin_cli.py reject proj_123 --notes "Quality issues"
  
  # Request revision
  python tools/admin_cli.py revise proj_123 --notes "Please fix the audio"
  
  # List pending projects
  python tools/admin_cli.py list
  
  # Show project status
  python tools/admin_cli.py status proj_123
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # approve 命令
    approve_parser = subparsers.add_parser(
        'approve',
        help='Approve a project and resume execution'
    )
    approve_parser.add_argument('project_id', help='Project ID to approve')
    approve_parser.add_argument('--notes', help='Optional approval notes')
    approve_parser.add_argument('--user', default='admin', help='Decision maker name')
    
    # reject 命令
    reject_parser = subparsers.add_parser(
        'reject',
        help='Reject a project and mark it as failed'
    )
    reject_parser.add_argument('project_id', help='Project ID to reject')
    reject_parser.add_argument('--notes', help='Optional rejection reason')
    reject_parser.add_argument('--user', default='admin', help='Decision maker name')
    
    # revise 命令
    revise_parser = subparsers.add_parser(
        'revise',
        help='Request revision for a project'
    )
    revise_parser.add_argument('project_id', help='Project ID to revise')
    revise_parser.add_argument('--notes', required=True, help='Revision instructions')
    revise_parser.add_argument('--user', default='admin', help='Decision maker name')
    
    # list 命令
    list_parser = subparsers.add_parser(
        'list',
        help='List all pending projects awaiting approval'
    )
    
    # status 命令
    status_parser = subparsers.add_parser(
        'status',
        help='Show detailed status of a project'
    )
    status_parser.add_argument('project_id', help='Project ID to query')
    
    return parser


async def main():
    """主函数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = AdminCLI()
    
    # 添加一些测试数据（在实际环境中，这些数据应该从 Blackboard 读取）
    cli.add_pending_project(
        project_id="proj_test_001",
        reason="Max retries exceeded",
        budget_info={
            "total": {"amount": 100.0, "currency": "USD"},
            "spent": {"amount": 85.0, "currency": "USD"},
            "estimated_remaining": {"amount": 15.0, "currency": "USD"}
        },
        context={
            "error_type": "APIError",
            "retry_count": 3,
            "last_error": "API timeout after 30s"
        }
    )
    
    # 执行命令
    if args.command == 'approve':
        await cli.publish_user_decision_event(
            project_id=args.project_id,
            action='approve',
            notes=args.notes,
            decided_by=args.user
        )
    
    elif args.command == 'reject':
        await cli.publish_user_decision_event(
            project_id=args.project_id,
            action='reject',
            notes=args.notes,
            decided_by=args.user
        )
    
    elif args.command == 'revise':
        await cli.publish_user_decision_event(
            project_id=args.project_id,
            action='revise',
            notes=args.notes,
            decided_by=args.user
        )
    
    elif args.command == 'list':
        cli.list_pending_projects()
    
    elif args.command == 'status':
        cli.show_project_status(args.project_id)


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
