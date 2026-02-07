"""
EventManager 单元测试

测试事件数据完整性和 Blackboard 写入逻辑
Validates: Requirements 5.2, 5.5
"""

import pytest
from datetime import datetime

from src.agents.requirement_parser.event_manager import EventManager
from src.agents.requirement_parser.models import (
    GlobalSpec,
    StyleConfig,
    ConfidenceReport,
    ConfidenceLevel,
    ClarificationRequest,
    Money,
    EventType
)


@pytest.fixture
def event_manager():
    """创建 EventManager 实例"""
    return EventManager(agent_name="TestAgent")


@pytest.fixture
def sample_global_spec():
    """创建示例 GlobalSpec"""
    return GlobalSpec(
        title="Test Video",
        duration=30,
        aspect_ratio="16:9",
        quality_tier="balanced",
        resolution="1080x1920",
        fps=30,
        style=StyleConfig(
            tone="warm",
            palette=["#FF5733", "#33FF57"],
            visual_dna_version=1
        ),
        characters=["Alice", "Bob"],
        mood="happy",
        user_options={"theme": "adventure"}
    )


@pytest.fixture
def sample_confidence_report():
    """创建示例 ConfidenceReport"""
    return ConfidenceReport(
        overall_confidence=0.85,
        component_scores={
            "text_analysis": 0.9,
            "visual_style": 0.8
        },
        low_confidence_areas=["audio_mood"],
        clarification_requests=[
            ClarificationRequest(
                field_name="duration",
                current_value=30,
                reason="Duration not explicitly specified",
                suggestions=["15 seconds", "30 seconds", "60 seconds"],
                priority="medium"
            )
        ],
        recommendation="proceed"
    )


class TestEventManagerBasics:
    """测试 EventManager 基础功能"""
    
    def test_initialization(self, event_manager):
        """测试：EventManager 正确初始化"""
        assert event_manager.agent_name == "TestAgent"
        assert event_manager.get_event_count() == 0
        assert len(event_manager.get_published_events()) == 0
    
    def test_generate_event_id(self, event_manager):
        """测试：生成唯一的事件 ID"""
        event_id1 = event_manager.generate_event_id()
        event_id2 = event_manager.generate_event_id()
        
        assert event_id1.startswith("evt_")
        assert event_id2.startswith("evt_")
        assert event_id1 != event_id2
        assert len(event_id1) == 16  # "evt_" + 12 hex chars
    
    def test_generate_project_id(self, event_manager):
        """测试：生成唯一的项目 ID"""
        project_id1 = event_manager.generate_project_id()
        project_id2 = event_manager.generate_project_id()
        
        assert project_id1.startswith("proj_")
        assert project_id2.startswith("proj_")
        assert project_id1 != project_id2
        assert len(project_id1) == 17  # "proj_" + 12 hex chars


class TestProjectCreatedEvent:
    """测试 PROJECT_CREATED 事件发布"""
    
    @pytest.mark.asyncio
    async def test_publish_project_created_basic(
        self,
        event_manager,
        sample_global_spec,
        sample_confidence_report
    ):
        """测试：发布基本的 PROJECT_CREATED 事件"""
        project_id = "proj_test_001"
        
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=sample_global_spec,
            confidence_report=sample_confidence_report
        )
        
        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.PROJECT_CREATED
        assert event.actor == "TestAgent"
        assert event.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_project_created_event_payload(
        self,
        event_manager,
        sample_global_spec,
        sample_confidence_report
    ):
        """测试：PROJECT_CREATED 事件 payload 包含完整数据"""
        project_id = "proj_test_002"
        
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=sample_global_spec,
            confidence_report=sample_confidence_report
        )
        
        # 验证 payload 结构
        assert "global_spec" in event.payload
        assert "confidence_report" in event.payload
        
        # 验证 GlobalSpec 数据
        global_spec_data = event.payload["global_spec"]
        assert global_spec_data["title"] == "Test Video"
        assert global_spec_data["duration"] == 30
        assert global_spec_data["aspect_ratio"] == "16:9"
        assert global_spec_data["quality_tier"] == "balanced"
        assert global_spec_data["fps"] == 30
        assert "style" in global_spec_data
        assert global_spec_data["style"]["tone"] == "warm"
        assert len(global_spec_data["style"]["palette"]) == 2
        assert global_spec_data["characters"] == ["Alice", "Bob"]
        assert global_spec_data["mood"] == "happy"
        
        # 验证 ConfidenceReport 数据
        confidence_data = event.payload["confidence_report"]
        assert confidence_data["overall_confidence"] == 0.85
        assert confidence_data["confidence_level"] == "high"  # ConfidenceLevel.HIGH.value is lowercase
        assert "component_scores" in confidence_data
        assert confidence_data["component_scores"]["text_analysis"] == 0.9
        assert "low_confidence_areas" in confidence_data
        assert "audio_mood" in confidence_data["low_confidence_areas"]
        assert confidence_data["recommendation"] == "proceed"
    
    @pytest.mark.asyncio
    async def test_project_created_with_cost_and_latency(
        self,
        event_manager,
        sample_global_spec,
        sample_confidence_report
    ):
        """测试：PROJECT_CREATED 事件包含成本和延迟信息"""
        project_id = "proj_test_003"
        cost = Money(amount=0.05, currency="USD")
        latency_ms = 1500
        causation_id = "evt_trigger_001"
        
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=sample_global_spec,
            confidence_report=sample_confidence_report,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms
        )
        
        assert event.causation_id == causation_id
        assert event.cost == cost
        assert event.cost.amount == 0.05
        assert event.cost.currency == "USD"
        assert event.latency_ms == 1500
    
    @pytest.mark.asyncio
    async def test_project_created_with_metadata(
        self,
        event_manager,
        sample_global_spec,
        sample_confidence_report
    ):
        """测试：PROJECT_CREATED 事件包含自定义元数据"""
        project_id = "proj_test_004"
        metadata = {
            "source": "web_ui",
            "user_id": "user_123",
            "session_id": "session_456"
        }
        
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=sample_global_spec,
            confidence_report=sample_confidence_report,
            metadata=metadata
        )
        
        assert event.metadata == metadata
        assert event.metadata["source"] == "web_ui"
        assert event.metadata["user_id"] == "user_123"


class TestErrorOccurredEvent:
    """测试 ERROR_OCCURRED 事件发布"""
    
    @pytest.mark.asyncio
    async def test_publish_error_occurred_basic(self, event_manager):
        """测试：发布基本的 ERROR_OCCURRED 事件"""
        project_id = "proj_test_005"
        error = ValueError("Test error message")
        
        event = await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error
        )
        
        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.ERROR_OCCURRED
        assert event.actor == "TestAgent"
    
    @pytest.mark.asyncio
    async def test_error_event_payload(self, event_manager):
        """测试：ERROR_OCCURRED 事件 payload 包含完整错误信息"""
        project_id = "proj_test_006"
        error = RuntimeError("Something went wrong")
        error_context = {
            "step": "preprocessing",
            "input_size": 1024,
            "retry_count": 3
        }
        
        event = await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error,
            error_context=error_context
        )
        
        # 验证 payload 结构
        assert "error_type" in event.payload
        assert "error_message" in event.payload
        assert "error_context" in event.payload
        assert "timestamp" in event.payload
        
        # 验证错误信息
        assert event.payload["error_type"] == "RuntimeError"
        assert event.payload["error_message"] == "Something went wrong"
        assert event.payload["error_context"] == error_context
        assert event.payload["error_context"]["step"] == "preprocessing"
    
    @pytest.mark.asyncio
    async def test_error_event_with_causation(self, event_manager):
        """测试：ERROR_OCCURRED 事件包含因果关系"""
        project_id = "proj_test_007"
        error = Exception("Test exception")
        causation_id = "evt_trigger_002"
        
        event = await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error,
            causation_id=causation_id
        )
        
        assert event.causation_id == causation_id


class TestHumanClarificationEvent:
    """测试 HUMAN_CLARIFICATION_REQUIRED 事件发布"""
    
    @pytest.mark.asyncio
    async def test_publish_human_clarification(
        self,
        event_manager,
        sample_confidence_report
    ):
        """测试：发布 HUMAN_CLARIFICATION_REQUIRED 事件"""
        project_id = "proj_test_008"
        
        event = await event_manager.publish_human_clarification_required(
            project_id=project_id,
            confidence_report=sample_confidence_report
        )
        
        assert event is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.HUMAN_CLARIFICATION_REQUIRED
        assert event.actor == "TestAgent"
    
    @pytest.mark.asyncio
    async def test_human_clarification_payload(
        self,
        event_manager,
        sample_confidence_report
    ):
        """测试：HUMAN_CLARIFICATION_REQUIRED 事件包含完整澄清请求"""
        project_id = "proj_test_009"
        
        event = await event_manager.publish_human_clarification_required(
            project_id=project_id,
            confidence_report=sample_confidence_report
        )
        
        # 验证 payload 结构
        assert "confidence_report" in event.payload
        confidence_data = event.payload["confidence_report"]
        
        # 验证置信度信息
        assert confidence_data["overall_confidence"] == 0.85
        assert confidence_data["confidence_level"] == "high"  # ConfidenceLevel.HIGH.value is lowercase
        assert "low_confidence_areas" in confidence_data
        assert "clarification_requests" in confidence_data
        
        # 验证澄清请求
        clarification_requests = confidence_data["clarification_requests"]
        assert len(clarification_requests) == 1
        assert clarification_requests[0]["field_name"] == "duration"
        assert clarification_requests[0]["current_value"] == 30
        assert clarification_requests[0]["reason"] == "Duration not explicitly specified"
        assert len(clarification_requests[0]["suggestions"]) == 3
        assert clarification_requests[0]["priority"] == "medium"


class TestBlackboardWrite:
    """测试 Blackboard 写入功能"""
    
    @pytest.mark.asyncio
    async def test_write_to_blackboard_basic(self, event_manager):
        """测试：基本的 Blackboard 写入"""
        project_id = "proj_test_010"
        path = "test_data"
        data = {"key": "value", "number": 42}
        
        write_request = await event_manager.write_to_blackboard(
            project_id=project_id,
            path=path,
            data=data
        )
        
        assert write_request is not None
        assert write_request.project_id == project_id
        assert write_request.path == path
        assert write_request.data == data
    
    @pytest.mark.asyncio
    async def test_write_to_blackboard_with_metadata(self, event_manager):
        """测试：带元数据的 Blackboard 写入"""
        project_id = "proj_test_011"
        path = "test_data"
        data = {"key": "value"}
        metadata = {"source": "test", "version": 1}
        
        write_request = await event_manager.write_to_blackboard(
            project_id=project_id,
            path=path,
            data=data,
            metadata=metadata
        )
        
        assert write_request.metadata == metadata
        assert write_request.metadata["source"] == "test"
    
    @pytest.mark.asyncio
    async def test_write_global_spec_to_blackboard(
        self,
        event_manager,
        sample_global_spec
    ):
        """测试：将 GlobalSpec 写入 Blackboard"""
        project_id = "proj_test_012"
        
        write_request = await event_manager.write_global_spec_to_blackboard(
            project_id=project_id,
            global_spec=sample_global_spec
        )
        
        # 验证写入请求
        assert write_request.project_id == project_id
        assert write_request.path == "global_spec"
        
        # 验证数据完整性
        assert "title" in write_request.data
        assert "duration" in write_request.data
        assert "aspect_ratio" in write_request.data
        assert "quality_tier" in write_request.data
        assert "resolution" in write_request.data
        assert "fps" in write_request.data
        assert "style" in write_request.data
        assert "characters" in write_request.data
        assert "mood" in write_request.data
        
        # 验证数据值
        assert write_request.data["title"] == "Test Video"
        assert write_request.data["duration"] == 30
        assert write_request.data["aspect_ratio"] == "16:9"
        
        # 验证元数据
        assert "written_by" in write_request.metadata
        assert write_request.metadata["written_by"] == "TestAgent"
        assert "timestamp" in write_request.metadata


class TestEventTracking:
    """测试事件跟踪功能"""
    
    @pytest.mark.asyncio
    async def test_event_tracking(self, event_manager):
        """测试：事件被正确跟踪"""
        project_id = "proj_test_013"
        error = ValueError("Test error")
        
        # 初始状态
        assert event_manager.get_event_count() == 0
        
        # 发布第一个事件
        await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error
        )
        
        assert event_manager.get_event_count() == 1
        
        # 发布第二个事件
        await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error
        )
        
        assert event_manager.get_event_count() == 2
        
        # 获取事件列表
        events = event_manager.get_published_events()
        assert len(events) == 2
        assert all(e.event_type == EventType.ERROR_OCCURRED for e in events)
    
    @pytest.mark.asyncio
    async def test_clear_published_events(self, event_manager):
        """测试：清空已发布的事件"""
        project_id = "proj_test_014"
        error = ValueError("Test error")
        
        # 发布一些事件
        await event_manager.publish_error_occurred(project_id=project_id, error=error)
        await event_manager.publish_error_occurred(project_id=project_id, error=error)
        
        assert event_manager.get_event_count() == 2
        
        # 清空事件
        event_manager.clear_published_events()
        
        assert event_manager.get_event_count() == 0
        assert len(event_manager.get_published_events()) == 0
    
    @pytest.mark.asyncio
    async def test_get_published_events_returns_copy(self, event_manager):
        """测试：get_published_events 返回副本，不影响原始列表"""
        project_id = "proj_test_015"
        error = ValueError("Test error")
        
        await event_manager.publish_error_occurred(project_id=project_id, error=error)
        
        # 获取事件列表
        events1 = event_manager.get_published_events()
        events2 = event_manager.get_published_events()
        
        # 修改副本不应影响原始列表
        events1.clear()
        
        assert len(events2) == 1
        assert event_manager.get_event_count() == 1


class TestEventSerialization:
    """测试事件序列化"""
    
    @pytest.mark.asyncio
    async def test_event_to_dict(
        self,
        event_manager,
        sample_global_spec,
        sample_confidence_report
    ):
        """测试：事件可以正确序列化为字典"""
        project_id = "proj_test_016"
        cost = Money(amount=0.03, currency="USD")
        latency_ms = 2000
        causation_id = "evt_trigger_003"
        
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=sample_global_spec,
            confidence_report=sample_confidence_report,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms
        )
        
        event_dict = event.to_dict()
        
        # 验证字典包含所有必需字段
        assert "event_id" in event_dict
        assert "project_id" in event_dict
        assert "event_type" in event_dict
        assert "actor" in event_dict
        assert "payload" in event_dict
        assert "timestamp" in event_dict
        assert "metadata" in event_dict
        assert "causation_id" in event_dict
        assert "cost" in event_dict
        assert "latency_ms" in event_dict
        
        # 验证字段值
        assert event_dict["event_id"] == event.event_id
        assert event_dict["project_id"] == project_id
        assert event_dict["event_type"] == "PROJECT_CREATED"
        assert event_dict["actor"] == "TestAgent"
        assert event_dict["causation_id"] == causation_id
        assert event_dict["latency_ms"] == 2000
        
        # 验证成本序列化
        assert "amount" in event_dict["cost"]
        assert "currency" in event_dict["cost"]
        assert event_dict["cost"]["amount"] == 0.03
        assert event_dict["cost"]["currency"] == "USD"
