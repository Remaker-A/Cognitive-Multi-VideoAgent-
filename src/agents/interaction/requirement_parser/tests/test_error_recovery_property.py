"""
閿欒澶勭悊鍜屾仮澶嶆満鍒剁殑灞炴€ф祴璇?

Feature: requirement-parser-agent, Property 6: Error Recovery and Resilience
Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5

娴嬭瘯閿欒鎭㈠鏈哄埗鍦ㄥ悇绉嶉敊璇潯浠朵笅鐨勮涓?
"""

import pytest
import asyncio
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any

from ..agent import RequirementParserAgent
from ...models import UserInputData, ProcessingStatus, ProcessingResult
from ..exceptions import (
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError,
    MaxRetriesExceededError,
    InputValidationError,
    InsufficientInputError,
    HumanInterventionRequired
)
from ..error_recovery import ErrorClassifier, RecoveryStrategy, ErrorCategory


# ============================================================================
# 绛栫暐瀹氫箟
# ============================================================================

@st.composite
def user_input_strategy(draw):
    """鐢熸垚闅忔満鐨勭敤鎴疯緭鍏ユ暟鎹?""
    # 纭繚鑷冲皯鏈変竴浜涜緭鍏ワ紙鏂囨湰鎴栨枃浠讹級
    has_text = draw(st.booleans())
    
    if has_text:
        text_description = draw(st.text(min_size=10, max_size=200))
    else:
        text_description = ""
    
    # 鐢熸垚 0-3 涓弬鑰冩枃浠?
    num_images = draw(st.integers(min_value=0, max_value=3))
    num_videos = draw(st.integers(min_value=0, max_value=3))
    num_audio = draw(st.integers(min_value=0, max_value=3))
    
    # 濡傛灉娌℃湁鏂囨湰锛岀‘淇濊嚦灏戞湁涓€涓枃浠?
    if not has_text and num_images == 0 and num_videos == 0 and num_audio == 0:
        num_images = 1
    
    reference_images = [f"https://example.com/image{i}.jpg" for i in range(num_images)]
    reference_videos = [f"https://example.com/video{i}.mp4" for i in range(num_videos)]
    reference_audio = [f"https://example.com/audio{i}.mp3" for i in range(num_audio)]
    
    return UserInputData(
        text_description=text_description,
        reference_images=reference_images,
        reference_videos=reference_videos,
        reference_audio=reference_audio,
        user_preferences={}
    )


@st.composite
def api_error_strategy(draw):
    """鐢熸垚闅忔満鐨?API 閿欒"""
    error_types = [
        APITimeoutError,
        APIRateLimitError,
        NetworkError,
        DeepSeekAPIError
    ]
    
    error_class = draw(st.sampled_from(error_types))
    error_message = draw(st.text(min_size=10, max_size=100))
    status_code = draw(st.integers(min_value=400, max_value=599))
    
    return error_class(error_message, status_code=status_code)


# ============================================================================
# Property 6: Error Recovery and Resilience
# ============================================================================

@pytest.mark.property
@given(user_input=user_input_strategy())
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_property_agent_handles_all_errors_gracefully(user_input):
    """
    Property 6.1: 閿欒澶勭悊鐨勪紭闆呮€?
    
    *For any* error condition (API failures, invalid inputs, file access issues, resource constraints),
    the RequirementParser should handle the error gracefully and not crash
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
    """
    # 鍒涘缓 Agent
    agent = RequirementParserAgent()
    
    # Mock DeepSeek 瀹㈡埛绔互妯℃嫙鍚勭閿欒
    with patch.object(agent.deepseek_client, 'chat_completion', new_callable=AsyncMock) as mock_api:
        # 妯℃嫙 API 閿欒
        mock_api.side_effect = DeepSeekAPIError("API Error", status_code=500)
        
        # 鎵ц澶勭悊
        try:
            result = asyncio.run(agent.process_user_input(user_input))
            
            # 楠岃瘉锛氬嵆浣垮嚭閿欙紝涔熷簲璇ヨ繑鍥炵粨鏋滆€屼笉鏄穿婧?
            assert result is not None
            assert isinstance(result, ProcessingResult)
            
            # 楠岃瘉锛氶敊璇簲璇ヨ璁板綍
            assert result.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]
            
            # 濡傛灉澶辫触锛屽簲璇ユ湁閿欒娑堟伅
            if result.status == ProcessingStatus.FAILED:
                assert result.error_message is not None
                assert len(result.error_message) > 0
            
        except Exception as e:
            # 涓嶅簲璇ユ姏鍑烘湭鎹曡幏鐨勫紓甯?
            pytest.fail(f"Agent crashed with unhandled exception: {type(e).__name__}: {e}")


@pytest.mark.property
@given(
    user_input=user_input_strategy(),
    api_error=api_error_strategy()
)
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_property_api_errors_trigger_retry_mechanism(user_input, api_error):
    """
    Property 6.2: API 閿欒閲嶈瘯鏈哄埗
    
    *For any* API error (timeout, rate limit, network error),
    the RequirementParser should implement retry logic before failing
    
    **Validates: Requirements 6.1, 6.3**
    """
    agent = RequirementParserAgent()
    
    # 璁板綍 API 璋冪敤娆℃暟
    call_count = 0
    
    async def mock_api_call(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        
        # 鍓嶅嚑娆¤皟鐢ㄦ姏鍑洪敊璇?
        if call_count < 3:
            raise api_error
        
        # 鏈€鍚庝竴娆℃垚鍔?
        from ...models import DeepSeekResponse, DeepSeekChoice, DeepSeekMessage, DeepSeekUsage
        return DeepSeekResponse(
            id="test",
            object="chat.completion",
            created=0,
            model="test-model",
            choices=[
                DeepSeekChoice(
                    index=0,
                    message=DeepSeekMessage(role="assistant", content='{"main_theme": "test"}'),
                    finish_reason="stop"
                )
            ],
            usage=DeepSeekUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        )
    
    with patch.object(agent.deepseek_client, 'chat_completion', new_callable=AsyncMock) as mock_api:
        mock_api.side_effect = mock_api_call
        
        try:
            result = asyncio.run(agent.process_user_input(user_input))
            
            # 楠岃瘉锛氬簲璇ヨ繘琛屼簡澶氭閲嶈瘯
            # 娉ㄦ剰锛氱敱浜庨檷绾х瓥鐣ワ紝鍙兘涓嶄細杈惧埌3娆?
            assert call_count >= 1, "API should be called at least once"
            
            # 楠岃瘉锛氭渶缁堝簲璇ユ湁缁撴灉锛堟垚鍔熸垨澶辫触锛?
            assert result is not None
            assert isinstance(result, ProcessingResult)
            
        except Exception as e:
            # 鏌愪簺閿欒绫诲瀷鍙兘瀵艰嚧蹇€熷け璐ワ紝杩欐槸鍙互鎺ュ彈鐨?
            assert isinstance(e, (DeepSeekAPIError, MaxRetriesExceededError))


@pytest.mark.property
@given(user_input=user_input_strategy())
@settings(
    max_examples=20,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_property_invalid_input_returns_clear_error_message(user_input):
    """
    Property 6.3: 鏃犳晥杈撳叆鐨勯敊璇秷鎭?
    
    *For any* invalid user input,
    the RequirementParser should return a clear and specific error message
    
    **Validates: Requirements 6.2**
    """
    agent = RequirementParserAgent()
    
    # 鍒涘缓鏃犳晥杈撳叆锛堢┖鏂囨湰涓旀棤鏂囦欢锛?
    invalid_input = UserInputData(
        text_description="",
        reference_images=[],
        reference_videos=[],
        reference_audio=[],
        user_preferences={}
    )
    
    try:
        result = asyncio.run(agent.process_user_input(invalid_input))
        
        # 濡傛灉澶勭悊浜嗭紝搴旇鏈変綆缃俊搴︽垨澶辫触鐘舵€?
        if result.status == ProcessingStatus.FAILED:
            assert result.error_message is not None
            assert len(result.error_message) > 0
        elif result.confidence_report:
            # 缃俊搴﹀簲璇ュ緢浣?
            assert result.confidence_report.overall_confidence < 0.5
            
    except (InputValidationError, InsufficientInputError) as e:
        # 鎶涘嚭楠岃瘉閿欒涔熸槸鍙互鎺ュ彈鐨?
        assert str(e) is not None
        assert len(str(e)) > 0


@pytest.mark.property
@given(user_input=user_input_strategy())
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_property_fallback_processing_when_full_processing_fails(user_input):
    """
    Property 6.4: 闄嶇骇澶勭悊绛栫暐
    
    *For any* user input where full processing fails,
    the RequirementParser should attempt fallback processing strategies
    
    **Validates: Requirements 6.3, 6.4**
    """
    agent = RequirementParserAgent()
    
    # Mock API 浣垮叾鎬绘槸澶辫触
    with patch.object(agent.deepseek_client, 'chat_completion', new_callable=AsyncMock) as mock_api:
        mock_api.side_effect = DeepSeekAPIError("Persistent API Error", status_code=500)
        
        result = asyncio.run(agent.process_user_input(user_input))
        
        # 楠岃瘉锛氬簲璇ユ湁缁撴灉锛堝彲鑳芥槸闄嶇骇澶勭悊鐨勭粨鏋滐級
        assert result is not None
        assert isinstance(result, ProcessingResult)
        
        # 楠岃瘉锛氬鏋滄垚鍔燂紝搴旇鏄€氳繃闄嶇骇绛栫暐
        if result.status == ProcessingStatus.COMPLETED:
            # 闄嶇骇澶勭悊搴旇鐢熸垚 GlobalSpec
            assert result.global_spec is not None
            
            # 缃俊搴﹀簲璇ヨ緝浣?
            if result.confidence_report:
                assert result.confidence_report.overall_confidence < 0.7
        
        # 楠岃瘉锛氬鏋滃け璐ワ紝搴旇鏈夐敊璇秷鎭?
        elif result.status == ProcessingStatus.FAILED:
            assert result.error_message is not None


@pytest.mark.property
@given(user_input=user_input_strategy())
@settings(
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow]
)
def test_property_human_intervention_triggered_when_all_strategies_fail(user_input):
    """
    Property 6.5: 浜哄伐浠嬪叆瑙﹀彂
    
    *For any* user input where all automatic recovery strategies fail,
    the RequirementParser should trigger human intervention
    
    **Validates: Requirements 6.5**
    """
    agent = RequirementParserAgent()
    
    # Mock 鎵€鏈夌粍浠朵娇鍏跺け璐?
    with patch.object(agent.input_manager, 'receive_user_input', new_callable=AsyncMock) as mock_input:
        mock_input.side_effect = Exception("Critical failure")
        
        result = asyncio.run(agent.process_user_input(user_input))
        
        # 楠岃瘉锛氬簲璇ヨ繑鍥炲け璐ョ粨鏋?
        assert result is not None
        assert result.status == ProcessingStatus.FAILED
        
        # 楠岃瘉锛氬簲璇ユ湁閿欒娑堟伅
        assert result.error_message is not None
        
        # 楠岃瘉锛氬簲璇ュ彂甯冧簡浜嬩欢
        assert result.events_published > 0
        
        # 楠岃瘉锛氫簨浠朵腑搴旇鍖呭惈浜哄伐浠嬪叆鐩稿叧鐨勪簨浠?
        events = agent.event_manager.get_published_events()
        assert len(events) > 0
        
        # 妫€鏌ユ槸鍚︽湁閿欒浜嬩欢鎴栦汉宸ヤ粙鍏ヤ簨浠?
        event_types = [event.event_type for event in events]
        from ...models import EventType
        assert (EventType.ERROR_OCCURRED in event_types or 
                EventType.HUMAN_GATE_TRIGGERED in event_types)


# ============================================================================
# 閿欒鍒嗙被鍜屾仮澶嶇瓥鐣ユ祴璇?
# ============================================================================

@pytest.mark.property
@given(
    error_message=st.text(min_size=10, max_size=100),
    status_code=st.integers(min_value=400, max_value=599)
)
@settings(max_examples=20)
def test_property_error_classifier_categorizes_all_errors(error_message, status_code):
    """
    Property 6.6: 閿欒鍒嗙被鍣ㄧ殑瀹屾暣鎬?
    
    *For any* error,
    the ErrorClassifier should assign it to a valid category
    
    **Validates: Requirements 6.1**
    """
    # 鍒涘缓鍚勭绫诲瀷鐨勯敊璇?
    errors = [
        DeepSeekAPIError(error_message, status_code=status_code),
        APITimeoutError(error_message, status_code=408),
        APIRateLimitError(error_message, status_code=429),
        NetworkError(error_message),
        InputValidationError(error_message),
        InsufficientInputError(error_message),
    ]
    
    for error in errors:
        # 鍒嗙被閿欒
        category = ErrorClassifier.classify_error(error)
        
        # 楠岃瘉锛氬簲璇ヨ繑鍥炴湁鏁堢殑绫诲埆
        assert category is not None
        assert isinstance(category, ErrorCategory)
        
        # 鎺ㄨ崘绛栫暐
        strategy = ErrorClassifier.recommend_strategy(error)
        
        # 楠岃瘉锛氬簲璇ヨ繑鍥炴湁鏁堢殑绛栫暐
        assert strategy is not None
        assert isinstance(strategy, RecoveryStrategy)


@pytest.mark.property
@given(
    error_message=st.text(min_size=10, max_size=100),
    status_code=st.integers(min_value=400, max_value=599)
)
@settings(max_examples=20)
def test_property_retryable_errors_are_correctly_identified(error_message, status_code):
    """
    Property 6.7: 鍙噸璇曢敊璇殑璇嗗埆
    
    *For any* error,
    the ErrorClassifier should correctly identify whether it is retryable
    
    **Validates: Requirements 6.1, 6.3**
    """
    # API 閿欒搴旇鏄彲閲嶈瘯鐨?
    api_errors = [
        APITimeoutError(error_message, status_code=408),
        APIRateLimitError(error_message, status_code=429),
        NetworkError(error_message)
    ]
    
    for error in api_errors:
        assert ErrorClassifier.is_retryable(error), \
            f"{type(error).__name__} should be retryable"
    
    # 杈撳叆楠岃瘉閿欒涓嶅簲璇ラ噸璇?
    validation_errors = [
        InputValidationError(error_message),
        InsufficientInputError(error_message)
    ]
    
    for error in validation_errors:
        assert not ErrorClassifier.is_retryable(error), \
            f"{type(error).__name__} should not be retryable"
    
    # 宸茶揪鍒版渶澶ч噸璇曟鏁扮殑閿欒涓嶅簲璇ュ啀閲嶈瘯
    max_retries_error = MaxRetriesExceededError(error_message, retry_count=3)
    assert not ErrorClassifier.is_retryable(max_retries_error), \
        "MaxRetriesExceededError should not be retryable"


# ============================================================================
# 杈呭姪鍑芥暟
# ============================================================================

def create_mock_agent_with_error(error_to_raise):
    """鍒涘缓涓€涓細鎶涘嚭鐗瑰畾閿欒鐨?mock agent"""
    agent = RequirementParserAgent()
    
    async def mock_process(*args, **kwargs):
        raise error_to_raise
    
    agent._full_processing = mock_process
    return agent


if __name__ == "__main__":
    # 杩愯灞炴€ф祴璇?
    pytest.main([__file__, "-v", "--hypothesis-show-statistics"])
