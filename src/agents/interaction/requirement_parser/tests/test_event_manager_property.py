"""
EventManager 灞炴€ф祴璇?

Feature: requirement-parser-agent, Property 5: Event Publishing Consistency
Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
"""

import pytest
from hypothesis import given, strategies as st, settings
from hypothesis import assume

from src.agents.interaction.requirement_parser.event_manager import EventManager
from src.agents.interaction.requirement_parser.models import (
    GlobalSpec,
    StyleConfig,
    ConfidenceReport,
    ConfidenceLevel,
    ClarificationRequest,
    Money,
    EventType
)


# Hypothesis strategies for generating test data
@st.composite
def global_spec_strategy(draw):
    """鐢熸垚闅忔満鐨?GlobalSpec"""
    return GlobalSpec(
        title=draw(st.text(min_size=1, max_size=100)),
        duration=draw(st.integers(min_value=1, max_value=300)),
        aspect_ratio=draw(st.sampled_from(["16:9", "9:16", "1:1", "4:3"])),
        quality_tier=draw(st.sampled_from(["low", "balanced", "high"])),
        resolution=draw(st.sampled_from(["720x1280", "1080x1920", "1080x1080"])),
        fps=draw(st.sampled_from([24, 30, 60])),
        style=StyleConfig(
            tone=draw(st.text(min_size=1, max_size=50)),
            palette=draw(st.lists(st.text(min_size=1, max_size=20), min_size=1, max_size=5)),
            visual_dna_version=draw(st.integers(min_value=1, max_value=10))
        ),
        characters=draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10)),
        mood=draw(st.text(min_size=1, max_size=100)),
        user_options=draw(st.dictionaries(st.text(min_size=1, max_size=20), st.text(min_size=1, max_size=50)))
    )


@st.composite
def confidence_report_strategy(draw):
    """鐢熸垚闅忔満鐨?ConfidenceReport"""
    overall_confidence = draw(st.floats(min_value=0.0, max_value=1.0))
    
    return ConfidenceReport(
        overall_confidence=overall_confidence,
        component_scores=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.floats(min_value=0.0, max_value=1.0),
            min_size=0,
            max_size=5
        )),
        low_confidence_areas=draw(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5)),
        clarification_requests=draw(st.lists(
            st.builds(
                ClarificationRequest,
                field_name=st.text(min_size=1, max_size=20),
                current_value=st.text(min_size=0, max_size=50),
                reason=st.text(min_size=1, max_size=100),
                suggestions=st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=3),
                priority=st.sampled_from(["low", "medium", "high"])
            ),
            min_size=0,
            max_size=3
        )),
        recommendation=draw(st.sampled_from(["proceed", "clarify", "human_review"]))
    )


@st.composite
def money_strategy(draw):
    """鐢熸垚闅忔満鐨?Money"""
    return Money(
        amount=draw(st.floats(min_value=0.0, max_value=100.0)),
        currency=draw(st.sampled_from(["USD", "EUR", "CNY"]))
    )


class TestEventPublishingConsistency:
    """
    Property 5: Event Publishing Consistency
    
    For any completed or failed parsing operation, the RequirementParser should publish
    the appropriate event (PROJECT_CREATED or ERROR_OCCURRED) with complete metadata
    and causal relationships.
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    @pytest.mark.asyncio
    @given(
        global_spec=global_spec_strategy(),
        confidence_report=confidence_report_strategy(),
        cost=st.one_of(st.none(), money_strategy()),
        latency_ms=st.one_of(st.none(), st.integers(min_value=0, max_value=60000))
    )
    @settings(max_examples=20, deadline=None)
    async def test_project_created_event_completeness(
        self,
        global_spec,
        confidence_report,
        cost,
        latency_ms
    ):
        """
        灞炴€ф祴璇曪細PROJECT_CREATED 浜嬩欢鍖呭惈瀹屾暣鏁版嵁
        
        瀵逛簬浠讳綍鏈夋晥鐨?GlobalSpec 鍜?ConfidenceReport锛屽彂甯冪殑 PROJECT_CREATED 浜嬩欢
        搴旇鍖呭惈鎵€鏈夊繀闇€鐨勫瓧娈靛拰瀹屾暣鐨勫厓鏁版嵁銆?
        
        Validates: Requirements 5.1, 5.2, 5.3
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        causation_id = event_manager.generate_event_id()
        
        # Act
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms
        )
        
        # Assert - 楠岃瘉浜嬩欢鍩烘湰缁撴瀯
        assert event is not None
        assert event.event_id is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.PROJECT_CREATED
        assert event.actor == "RequirementParserAgent"
        
        # Assert - 楠岃瘉鍥犳灉鍏崇郴
        assert event.causation_id == causation_id
        
        # Assert - 楠岃瘉 payload 瀹屾暣鎬?
        assert "global_spec" in event.payload
        assert "confidence_report" in event.payload
        
        # Assert - 楠岃瘉 GlobalSpec 鏁版嵁瀹屾暣鎬?
        global_spec_data = event.payload["global_spec"]
        assert global_spec_data["title"] == global_spec.title
        assert global_spec_data["duration"] == global_spec.duration
        assert global_spec_data["aspect_ratio"] == global_spec.aspect_ratio
        
        # Assert - 楠岃瘉 ConfidenceReport 鏁版嵁瀹屾暣鎬?
        confidence_data = event.payload["confidence_report"]
        assert confidence_data["overall_confidence"] == confidence_report.overall_confidence
        assert confidence_data["recommendation"] == confidence_report.recommendation
        
        # Assert - 楠岃瘉鎴愭湰鍜屽欢杩熶俊鎭?
        if cost:
            assert event.cost == cost
        if latency_ms is not None:
            assert event.latency_ms == latency_ms
        
        # Assert - 楠岃瘉浜嬩欢琚褰?
        published_events = event_manager.get_published_events()
        assert len(published_events) == 1
        assert published_events[0].event_id == event.event_id
    
    @pytest.mark.asyncio
    @given(
        error_message=st.text(min_size=1, max_size=200),
        error_context=st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=1, max_size=100),
            min_size=0,
            max_size=5
        )
    )
    @settings(max_examples=20, deadline=None)
    async def test_error_event_completeness(self, error_message, error_context):
        """
        灞炴€ф祴璇曪細ERROR_OCCURRED 浜嬩欢鍖呭惈瀹屾暣閿欒淇℃伅
        
        瀵逛簬浠讳綍閿欒鎯呭喌锛屽彂甯冪殑 ERROR_OCCURRED 浜嬩欢搴旇鍖呭惈閿欒绫诲瀷銆?
        閿欒娑堟伅鍜屽畬鏁寸殑涓婁笅鏂囦俊鎭€?
        
        Validates: Requirements 5.4
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        causation_id = event_manager.generate_event_id()
        error = ValueError(error_message)
        
        # Act
        event = await event_manager.publish_error_occurred(
            project_id=project_id,
            error=error,
            error_context=error_context,
            causation_id=causation_id
        )
        
        # Assert - 楠岃瘉浜嬩欢鍩烘湰缁撴瀯
        assert event is not None
        assert event.event_id is not None
        assert event.event_id.startswith("evt_")
        assert event.project_id == project_id
        assert event.event_type == EventType.ERROR_OCCURRED
        assert event.actor == "RequirementParserAgent"
        
        # Assert - 楠岃瘉鍥犳灉鍏崇郴
        assert event.causation_id == causation_id
        
        # Assert - 楠岃瘉閿欒淇℃伅瀹屾暣鎬?
        assert "error_type" in event.payload
        assert "error_message" in event.payload
        assert "error_context" in event.payload
        assert "timestamp" in event.payload
        
        assert event.payload["error_type"] == "ValueError"
        assert event.payload["error_message"] == error_message
        assert event.payload["error_context"] == error_context
        
        # Assert - 楠岃瘉浜嬩欢琚褰?
        published_events = event_manager.get_published_events()
        assert len(published_events) == 1
        assert published_events[0].event_id == event.event_id
    
    @pytest.mark.asyncio
    @given(
        confidence_report=confidence_report_strategy()
    )
    @settings(max_examples=20, deadline=None)
    async def test_human_clarification_event_completeness(self, confidence_report):
        """
        灞炴€ф祴璇曪細HUMAN_CLARIFICATION_REQUIRED 浜嬩欢鍖呭惈瀹屾暣婢勬竻璇锋眰
        
        瀵逛簬浠讳綍浣庣疆淇″害鎯呭喌锛屽彂甯冪殑 HUMAN_CLARIFICATION_REQUIRED 浜嬩欢
        搴旇鍖呭惈瀹屾暣鐨勭疆淇″害鎶ュ憡鍜屾緞娓呰姹傘€?
        
        Validates: Requirements 5.4
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        causation_id = event_manager.generate_event_id()
        
        # Act
        event = await event_manager.publish_human_clarification_required(
            project_id=project_id,
            confidence_report=confidence_report,
            causation_id=causation_id
        )
        
        # Assert - 楠岃瘉浜嬩欢鍩烘湰缁撴瀯
        assert event is not None
        assert event.event_id is not None
        assert event.project_id == project_id
        assert event.event_type == EventType.HUMAN_CLARIFICATION_REQUIRED
        
        # Assert - 楠岃瘉缃俊搴︽姤鍛婂畬鏁存€?
        assert "confidence_report" in event.payload
        confidence_data = event.payload["confidence_report"]
        assert confidence_data["overall_confidence"] == confidence_report.overall_confidence
        assert "clarification_requests" in confidence_data
        assert len(confidence_data["clarification_requests"]) == len(confidence_report.clarification_requests)
    
    @pytest.mark.asyncio
    @given(
        global_spec=global_spec_strategy()
    )
    @settings(max_examples=20, deadline=None)
    async def test_blackboard_write_consistency(self, global_spec):
        """
        灞炴€ф祴璇曪細Blackboard 鍐欏叆鏁版嵁涓€鑷存€?
        
        瀵逛簬浠讳綍 GlobalSpec锛屽啓鍏?Blackboard 鐨勬暟鎹簲璇ヤ笌鍘熷鏁版嵁涓€鑷达紝
        骞跺寘鍚纭殑椤圭洰 ID 鍜岃矾寰勩€?
        
        Validates: Requirements 5.5
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        
        # Act
        write_request = await event_manager.write_global_spec_to_blackboard(
            project_id=project_id,
            global_spec=global_spec
        )
        
        # Assert - 楠岃瘉鍐欏叆璇锋眰缁撴瀯
        assert write_request is not None
        assert write_request.project_id == project_id
        assert write_request.path == "global_spec"
        
        # Assert - 楠岃瘉鏁版嵁瀹屾暣鎬?
        assert "title" in write_request.data
        assert "duration" in write_request.data
        assert "aspect_ratio" in write_request.data
        assert write_request.data["title"] == global_spec.title
        assert write_request.data["duration"] == global_spec.duration
        
        # Assert - 楠岃瘉鍏冩暟鎹?
        assert "written_by" in write_request.metadata
        assert write_request.metadata["written_by"] == "RequirementParserAgent"
    
    @pytest.mark.asyncio
    @given(
        event_count=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=10, deadline=None)
    async def test_multiple_events_tracking(self, event_count):
        """
        灞炴€ф祴璇曪細澶氫釜浜嬩欢鐨勮窡韪拰绠＄悊
        
        瀵逛簬浠绘剰鏁伴噺鐨勪簨浠跺彂甯冿紝EventManager 搴旇姝ｇ‘璺熻釜鎵€鏈夊凡鍙戝竷鐨勪簨浠讹紝
        骞舵彁渚涘噯纭殑浜嬩欢璁℃暟銆?
        
        Validates: Requirements 5.3
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        
        # Act - 鍙戝竷澶氫釜浜嬩欢
        for i in range(event_count):
            error = ValueError(f"Test error {i}")
            await event_manager.publish_error_occurred(
                project_id=project_id,
                error=error
            )
        
        # Assert - 楠岃瘉浜嬩欢璁℃暟
        assert event_manager.get_event_count() == event_count
        
        # Assert - 楠岃瘉鎵€鏈変簨浠堕兘琚褰?
        published_events = event_manager.get_published_events()
        assert len(published_events) == event_count
        
        # Assert - 楠岃瘉姣忎釜浜嬩欢閮芥湁鍞竴鐨?ID
        event_ids = [event.event_id for event in published_events]
        assert len(event_ids) == len(set(event_ids))  # 鎵€鏈?ID 閮芥槸鍞竴鐨?
        
        # Act - 娓呯┖浜嬩欢
        event_manager.clear_published_events()
        
        # Assert - 楠岃瘉娓呯┖鍚庤鏁颁负 0
        assert event_manager.get_event_count() == 0
    
    @pytest.mark.asyncio
    @given(
        global_spec=global_spec_strategy(),
        confidence_report=confidence_report_strategy()
    )
    @settings(max_examples=20, deadline=None)
    async def test_event_id_uniqueness(self, global_spec, confidence_report):
        """
        灞炴€ф祴璇曪細浜嬩欢 ID 鍞竴鎬?
        
        瀵逛簬浠讳綍浜嬩欢鍙戝竷鎿嶄綔锛岀敓鎴愮殑浜嬩欢 ID 搴旇鏄敮涓€鐨勩€?
        
        Validates: Requirements 5.1
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        
        # Act - 鍙戝竷澶氫釜浜嬩欢
        event1 = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report
        )
        
        event2 = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report
        )
        
        # Assert - 楠岃瘉浜嬩欢 ID 鍞竴鎬?
        assert event1.event_id != event2.event_id
        assert event1.event_id.startswith("evt_")
        assert event2.event_id.startswith("evt_")
    
    @pytest.mark.asyncio
    @given(
        global_spec=global_spec_strategy(),
        confidence_report=confidence_report_strategy()
    )
    @settings(max_examples=20, deadline=None)
    async def test_event_to_dict_serialization(self, global_spec, confidence_report):
        """
        灞炴€ф祴璇曪細浜嬩欢搴忓垪鍖栦竴鑷存€?
        
        瀵逛簬浠讳綍浜嬩欢锛宼o_dict() 鏂规硶搴旇杩斿洖鍖呭惈鎵€鏈夊繀闇€瀛楁鐨勫瓧鍏革紝
        骞朵笖鍙互姝ｇ‘搴忓垪鍖栥€?
        
        Validates: Requirements 5.2
        """
        # Arrange
        event_manager = EventManager()
        project_id = event_manager.generate_project_id()
        
        # Act
        event = await event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report
        )
        
        event_dict = event.to_dict()
        
        # Assert - 楠岃瘉瀛楀吀鍖呭惈鎵€鏈夊繀闇€瀛楁
        assert "event_id" in event_dict
        assert "project_id" in event_dict
        assert "event_type" in event_dict
        assert "actor" in event_dict
        assert "payload" in event_dict
        assert "timestamp" in event_dict
        assert "metadata" in event_dict
        
        # Assert - 楠岃瘉瀛楁鍊兼纭?
        assert event_dict["event_id"] == event.event_id
        assert event_dict["project_id"] == event.project_id
        assert event_dict["event_type"] == EventType.PROJECT_CREATED.value
        assert event_dict["actor"] == "RequirementParserAgent"
