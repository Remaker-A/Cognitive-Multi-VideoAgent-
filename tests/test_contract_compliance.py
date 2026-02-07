"""
契约遵守测试

测试事件、任务等数据结构是否符合契约定义。
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pytest
from datetime import datetime
from src.contracts import (
    EventType,
    TaskType,
    TaskStatus,
    Money,
    create_event,
    create_task,
    create_blackboard_request,
    create_blackboard_response,
    create_blackboard_error_response,
)


class TestEventContract:
    """测试事件契约"""
    
    def test_create_valid_event(self):
        """测试创建有效的事件"""
        event = create_event(
            event_id="evt_001",
            project_id="proj_001",
            event_type=EventType.IMAGE_GENERATED,
            actor="ImageGeneratorAgent",
            payload={"image_url": "s3://bucket/image.png"},
            cost=Money(amount=0.05, currency="USD"),
            latency_ms=1500,
        )
        
        assert event.event_id == "evt_001"
        assert event.project_id == "proj_001"
        assert event.type == EventType.IMAGE_GENERATED
        assert event.actor == "ImageGeneratorAgent"
        assert event.payload == {"image_url": "s3://bucket/image.png"}
        assert event.metadata.cost.amount == 0.05
        assert event.metadata.latency_ms == 1500
    
    def test_event_with_causation_id(self):
        """测试带因果链的事件"""
        event = create_event(
            event_id="evt_002",
            project_id="proj_001",
            event_type=EventType.QA_REPORT,
            actor="QAAgent",
            payload={"score": 0.95},
            causation_id="evt_001",  # 链接到上一个事件
        )
        
        assert event.causation_id == "evt_001"
    
    def test_event_with_blackboard_pointer(self):
        """测试带 Blackboard 指针的事件"""
        event = create_event(
            event_id="evt_003",
            project_id="proj_001",
            event_type=EventType.KEYFRAME_REQUESTED,
            actor="OrchestratorAgent",
            payload={"shot_id": "S01"},
            blackboard_pointer="/projects/proj_001/shots/S01/keyframes/mid",
        )
        
        assert event.blackboard_pointer == "/projects/proj_001/shots/S01/keyframes/mid"
    
    def test_event_serialization(self):
        """测试事件序列化"""
        event = create_event(
            event_id="evt_004",
            project_id="proj_001",
            event_type=EventType.PROJECT_CREATED,
            actor="SystemAgent",
            payload={"name": "Test Project"},
        )
        
        # 转换为字典
        event_dict = event.dict()
        assert isinstance(event_dict, dict)
        assert event_dict["event_id"] == "evt_004"
        assert event_dict["type"] == "PROJECT_CREATED"
        
        # 转换为 JSON
        event_json = event.json()
        assert isinstance(event_json, str)
        assert "evt_004" in event_json


class TestTaskContract:
    """测试任务契约"""
    
    def test_create_valid_task(self):
        """测试创建有效的任务"""
        task = create_task(
            task_id="task_001",
            task_type=TaskType.GENERATE_KEYFRAME,
            assigned_to="ImageGeneratorAgent",
            input_data={"prompt": "A beautiful sunset", "shot_id": "S01"},
            priority=3,
            estimated_cost=Money(amount=0.10, currency="USD"),
        )
        
        assert task.task_id == "task_001"
        assert task.type == TaskType.GENERATE_KEYFRAME
        assert task.assigned_to == "ImageGeneratorAgent"
        assert task.status == TaskStatus.PENDING
        assert task.priority == 3
        assert task.input == {"prompt": "A beautiful sunset", "shot_id": "S01"}
        assert task.estimated_cost.amount == 0.10
    
    def test_task_with_dependencies(self):
        """测试带依赖的任务"""
        task = create_task(
            task_id="task_002",
            task_type=TaskType.GENERATE_PREVIEW_VIDEO,
            assigned_to="VideoGeneratorAgent",
            input_data={"shot_id": "S01"},
            dependencies=["task_001"],  # 依赖于关键帧生成任务
        )
        
        assert task.dependencies == ["task_001"]
    
    def test_task_with_lock(self):
        """测试需要锁的任务"""
        task = create_task(
            task_id="task_003",
            task_type=TaskType.UPDATE_DNA_BANK,
            assigned_to="DNAAgent",
            input_data={"character": "Alice"},
            requires_lock=True,
            lock_key="dna_bank",
        )
        
        assert task.requires_lock is True
        assert task.lock_key == "dna_bank"
    
    def test_task_with_causation_event(self):
        """测试带因果事件的任务"""
        task = create_task(
            task_id="task_004",
            task_type=TaskType.WRITE_SCRIPT,
            assigned_to="ScriptWriterAgent",
            input_data={"theme": "Adventure"},
            causation_event_id="evt_001",
        )
        
        assert task.causation_event_id == "evt_001"
    
    def test_task_priority_validation(self):
        """测试任务优先级验证"""
        # 有效优先级
        task = create_task(
            task_id="task_005",
            task_type=TaskType.GENERATE_MUSIC,
            assigned_to="MusicAgent",
            input_data={},
            priority=5,
        )
        assert task.priority == 5
        
        # 无效优先级应该抛出异常
        with pytest.raises(Exception):
            create_task(
                task_id="task_006",
                task_type=TaskType.GENERATE_MUSIC,
                assigned_to="MusicAgent",
                input_data={},
                priority=10,  # 超出范围 [1, 5]
            )


class TestBlackboardRPCContract:
    """测试 Blackboard RPC 契约"""
    
    def test_create_valid_request(self):
        """测试创建有效的 RPC 请求"""
        request = create_blackboard_request(
            request_id="req_001",
            method="get_project",
            params={"project_id": "proj_001"},
        )
        
        assert request.id == "req_001"
        assert request.method == "get_project"
        assert request.params == {"project_id": "proj_001"}
    
    def test_create_valid_response(self):
        """测试创建有效的 RPC 响应"""
        response = create_blackboard_response(
            request_id="req_001",
            result={"project": {"id": "proj_001", "name": "Test"}},
        )
        
        assert response.id == "req_001"
        assert response.ok is True
        assert response.result == {"project": {"id": "proj_001", "name": "Test"}}
    
    def test_create_error_response(self):
        """测试创建错误响应"""
        error_response = create_blackboard_error_response(
            request_id="req_002",
            error_code="NOT_FOUND",
            error_message="Project not found",
            error_details={"project_id": "proj_999"},
        )
        
        assert error_response.id == "req_002"
        assert error_response.ok is False
        assert error_response.error.code == "NOT_FOUND"
        assert error_response.error.message == "Project not found"
        assert error_response.error.details == {"project_id": "proj_999"}


class TestMoneyContract:
    """测试金额契约"""
    
    def test_valid_money(self):
        """测试有效的金额"""
        money = Money(amount=10.50, currency="USD")
        assert money.amount == 10.50
        assert money.currency == "USD"
    
    def test_negative_amount_validation(self):
        """测试负金额验证"""
        with pytest.raises(Exception):
            Money(amount=-5.0, currency="USD")
    
    def test_currency_code_validation(self):
        """测试货币代码验证"""
        # 有效的 3 字符货币代码
        money = Money(amount=100.0, currency="EUR")
        assert money.currency == "EUR"
        
        # 无效的货币代码长度
        with pytest.raises(Exception):
            Money(amount=100.0, currency="US")  # 太短
        
        with pytest.raises(Exception):
            Money(amount=100.0, currency="USDD")  # 太长


class TestEnumContracts:
    """测试枚举契约"""
    
    def test_event_type_enum(self):
        """测试事件类型枚举"""
        assert EventType.PROJECT_CREATED == "PROJECT_CREATED"
        assert EventType.IMAGE_GENERATED == "IMAGE_GENERATED"
        assert EventType.ERROR_DETECTED == "ERROR_DETECTED"
    
    def test_task_type_enum(self):
        """测试任务类型枚举"""
        assert TaskType.WRITE_SCRIPT == "WRITE_SCRIPT"
        assert TaskType.GENERATE_KEYFRAME == "GENERATE_KEYFRAME"
        assert TaskType.RUN_VISUAL_QA == "RUN_VISUAL_QA"
    
    def test_task_status_enum(self):
        """测试任务状态枚举"""
        assert TaskStatus.PENDING == "PENDING"
        assert TaskStatus.RUNNING == "RUNNING"
        assert TaskStatus.COMPLETED == "COMPLETED"
        assert TaskStatus.FAILED == "FAILED"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
