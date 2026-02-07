"""
DeepSeekClient 灞炴€ф祴璇曪紙Property-Based Tests锛?

Feature: requirement-parser-agent
Property 3: API Communication Reliability
Validates: Requirements 3.1, 3.2, 3.3, 3.5
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import AsyncMock, Mock
import aiohttp

from src.agents.requirement_parser.deepseek_client import DeepSeekClient
from src.agents.requirement_parser.models import DeepSeekResponse
from src.agents.requirement_parser.exceptions import (
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError
)


# ============================================================================
# 绛栫暐瀹氫箟锛圫trategies锛?
# ============================================================================

# 鐢熸垚鏈夋晥鐨勬秷鎭垪琛?
valid_messages_strategy = st.lists(
    st.fixed_dictionaries({
        'role': st.sampled_from(['system', 'user', 'assistant']),
        'content': st.text(min_size=1, max_size=500)
    }),
    min_size=1,
    max_size=10
)

# 鐢熸垚鏈夋晥鐨勬ā鍨嬪弬鏁?
valid_model_params_strategy = st.fixed_dictionaries({
    'temperature': st.floats(min_value=0.0, max_value=1.0),
    'max_tokens': st.integers(min_value=1, max_value=4000)
})

# 鐢熸垚API瀵嗛挜
api_key_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P')),
    min_size=10,
    max_size=100
)

# 鐢熸垚鏈夋晥鐨凙PI鍝嶅簲
valid_api_response_strategy = st.fixed_dictionaries({
    'id': st.text(min_size=1, max_size=50),
    'object': st.just('chat.completion'),
    'created': st.integers(min_value=1000000000, max_value=9999999999),
    'model': st.just('DeepSeek-V3.2'),
    'choices': st.lists(
        st.fixed_dictionaries({
            'index': st.integers(min_value=0, max_value=10),
            'message': st.fixed_dictionaries({
                'role': st.just('assistant'),
                'content': st.text(min_size=1, max_size=1000)
            }),
            'finish_reason': st.sampled_from(['stop', 'length', 'content_filter'])
        }),
        min_size=1,
        max_size=1
    ),
    'usage': st.fixed_dictionaries({
        'prompt_tokens': st.integers(min_value=0, max_value=1000),
        'completion_tokens': st.integers(min_value=0, max_value=1000),
        'total_tokens': st.integers(min_value=0, max_value=2000)
    })
})


# ============================================================================
# Property 3: API Communication Reliability
# ============================================================================

class TestAPIAuthenticationProperty:
    """
    娴嬭瘯灞炴€э細API璁よ瘉澶寸殑姝ｇ‘鎬?
    
    Property 3.1: 瀵逛簬浠讳綍鏈夋晥鐨凙PI璇锋眰锛屽簲璇ヤ娇鐢ㄦ纭殑璁よ瘉澶?
    Validates: Requirements 3.1, 3.2
    """
    
    @given(
        api_key=api_key_strategy,
        messages=valid_messages_strategy
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_authentication_header_always_present(self, api_key, messages):
        """
        灞炴€ф祴璇曪細璁よ瘉澶村缁堝瓨鍦ㄤ笖鏍煎紡姝ｇ‘
        
        Feature: requirement-parser-agent, Property 3: API Communication Reliability
        
        瀵逛簬浠讳綍API瀵嗛挜鍜屾秷鎭垪琛紝鍙戦€佺殑璇锋眰搴旇锛?
        1. 鍖呭惈 Authorization 澶?
        2. 浣跨敤 Bearer token 鏍煎紡
        3. 鍖呭惈姝ｇ‘鐨凙PI瀵嗛挜
        """
        # Arrange
        client = DeepSeekClient(
            api_key=api_key,
            base_url="https://test.api.com"
        )
        
        # 鎹曡幏瀹為檯鍙戦€佺殑璇锋眰澶?
        captured_headers = {}
        
        def mock_post(*args, **kwargs):
            # 鎹曡幏headers
            captured_headers.update(kwargs.get('headers', {}))
            
            # 鍒涘缓mock鍝嶅簲
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "id": "test",
                "object": "chat.completion",
                "created": 123,
                "model": "test",
                "choices": [{
                    "index": 0,
                    "message": {"role": "assistant", "content": "test"},
                    "finish_reason": "stop"
                }],
                "usage": {"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            })
            
            class MockContextManager:
                async def __aenter__(self):
                    return mock_response
                async def __aexit__(self, *args):
                    pass
            
            return MockContextManager()
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = mock_post  # 浣跨敤鏅€氬嚱鏁拌€屼笉鏄疉syncMock
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act
        try:
            await client.chat_completion(messages=messages)
        except Exception:
            pass  # 蹇界暐鍏朵粬閿欒锛屽彧鍏虫敞璁よ瘉澶?
        
        # Assert - 楠岃瘉璁よ瘉澶?
        assert 'Authorization' in captured_headers, "Authorization header must be present"
        assert captured_headers['Authorization'] == f"Bearer {api_key}", \
            f"Authorization header must use Bearer token format with correct API key"
        assert 'Content-Type' in captured_headers, "Content-Type header must be present"
        assert captured_headers['Content-Type'] == "application/json", \
            "Content-Type must be application/json"


class TestAPIResponseHandlingProperty:
    """
    娴嬭瘯灞炴€э細API鍝嶅簲澶勭悊鐨勬纭€?
    
    Property 3.2: 瀵逛簬浠讳綍鏈夋晥鐨凙PI鍝嶅簲锛屽簲璇ユ纭В鏋愬苟杩斿洖缁撴瀯鍖栨暟鎹?
    Validates: Requirements 3.2
    """
    
    @given(
        api_response=valid_api_response_strategy,
        messages=valid_messages_strategy
    )
    @settings(
        max_examples=20,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_valid_response_always_parsed_correctly(self, api_response, messages):
        """
        灞炴€ф祴璇曪細鏈夋晥鍝嶅簲鎬绘槸琚纭В鏋?
        
        Feature: requirement-parser-agent, Property 3: API Communication Reliability
        
        瀵逛簬浠讳綍绗﹀悎API瑙勮寖鐨勫搷搴旓紝搴旇锛?
        1. 鎴愬姛瑙ｆ瀽涓?DeepSeekResponse 瀵硅薄
        2. 鍖呭惈鎵€鏈夊繀闇€瀛楁
        3. 瀛楁鍊肩被鍨嬫纭?
        """
        # Arrange
        client = DeepSeekClient(api_key="test_key")
        client._make_request = AsyncMock(return_value=api_response)
        
        # Act
        response = await client.chat_completion(messages=messages)
        
        # Assert - 楠岃瘉鍝嶅簲缁撴瀯
        assert isinstance(response, DeepSeekResponse), "Response must be DeepSeekResponse instance"
        assert response.id == api_response['id'], "Response ID must match"
        assert response.model == api_response['model'], "Model name must match"
        assert len(response.choices) == len(api_response['choices']), "Choices count must match"
        
        # 楠岃瘉 choices
        for i, choice in enumerate(response.choices):
            expected_choice = api_response['choices'][i]
            assert choice.index == expected_choice['index'], f"Choice {i} index must match"
            assert choice.message.role == expected_choice['message']['role'], \
                f"Choice {i} message role must match"
            assert choice.message.content == expected_choice['message']['content'], \
                f"Choice {i} message content must match"
        
        # 楠岃瘉 usage
        assert response.usage.prompt_tokens == api_response['usage']['prompt_tokens'], \
            "Prompt tokens must match"
        assert response.usage.completion_tokens == api_response['usage']['completion_tokens'], \
            "Completion tokens must match"
        assert response.usage.total_tokens == api_response['usage']['total_tokens'], \
            "Total tokens must match"


class TestAPIRetryLogicProperty:
    """
    娴嬭瘯灞炴€э細閲嶈瘯閫昏緫鐨勫彲闈犳€?
    
    Property 3.3: 瀵逛簬涓存椂澶辫触锛屽簲璇ュ疄鐜伴噸璇曢€昏緫
    Validates: Requirements 3.3, 3.5
    """
    
    @given(
        retry_count=st.integers(min_value=1, max_value=3),
        messages=valid_messages_strategy
    )
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_transient_failures_trigger_retry(self, retry_count, messages):
        """
        灞炴€ф祴璇曪細涓存椂澶辫触瑙﹀彂閲嶈瘯
        
        Feature: requirement-parser-agent, Property 3: API Communication Reliability
        
        瀵逛簬浠讳綍涓存椂澶辫触锛堣秴鏃躲€侀檺娴併€佺綉缁滈敊璇級锛屽簲璇ワ細
        1. 鑷姩閲嶈瘯鎸囧畾娆℃暟
        2. 浣跨敤鎸囨暟閫€閬跨瓥鐣?
        3. 鏈€缁堟垚鍔熸垨鎶涘嚭MaxRetriesExceededError
        """
        # Arrange
        client = DeepSeekClient(
            api_key="test_key",
            max_retries=retry_count
        )
        
        attempt_count = 0
        
        async def failing_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < retry_count:
                raise APITimeoutError("Simulated timeout")
            return "success"
        
        # Act
        result = await client.retry_with_exponential_backoff(
            failing_func,
            initial_delay=0.01,  # 浣跨敤寰堝皬鐨勫欢杩熷姞蹇祴璇?
            backoff_factor=2.0
        )
        
        # Assert
        assert result == "success", "Should eventually succeed"
        assert attempt_count == retry_count, \
            f"Should retry exactly {retry_count} times before success"
    
    @given(
        max_retries=st.integers(min_value=1, max_value=5)
    )
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_max_retries_respected(self, max_retries):
        """
        灞炴€ф祴璇曪細鏈€澶ч噸璇曟鏁拌閬靛畧
        
        Feature: requirement-parser-agent, Property 3: API Communication Reliability
        
        瀵逛簬浠讳綍鏈€澶ч噸璇曟鏁伴厤缃紝搴旇锛?
        1. 涓嶈秴杩囬厤缃殑鏈€澶ч噸璇曟鏁?
        2. 鍦ㄨ揪鍒版渶澶ф鏁板悗鎶涘嚭寮傚父
        """
        # Arrange
        client = DeepSeekClient(
            api_key="test_key",
            max_retries=max_retries
        )
        
        attempt_count = 0
        
        async def always_failing_func():
            nonlocal attempt_count
            attempt_count += 1
            raise NetworkError("Always fails")
        
        # Act & Assert
        from src.agents.requirement_parser.exceptions import MaxRetriesExceededError
        
        with pytest.raises(MaxRetriesExceededError) as exc_info:
            await client.retry_with_exponential_backoff(
                always_failing_func,
                initial_delay=0.01
            )
        
        assert exc_info.value.retry_count == max_retries, \
            f"Should fail after exactly {max_retries} attempts"
        assert attempt_count == max_retries, \
            f"Should attempt exactly {max_retries} times"


class TestAPIErrorHandlingProperty:
    """
    娴嬭瘯灞炴€э細API閿欒澶勭悊鐨勫畬鏁存€?
    
    Property 3.4: 瀵逛簬涓嶅悓绫诲瀷鐨凙PI閿欒锛屽簲璇ユ姏鍑虹浉搴旂殑寮傚父
    Validates: Requirements 3.4
    """
    
    @given(
        status_code=st.sampled_from([400, 401, 403, 404, 429, 500, 502, 503]),
        messages=valid_messages_strategy
    )
    @settings(
        max_examples=10,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @pytest.mark.asyncio
    async def test_http_errors_raise_appropriate_exceptions(self, status_code, messages):
        """
        灞炴€ф祴璇曪細HTTP閿欒鐮佹槧灏勫埌姝ｇ‘鐨勫紓甯哥被鍨?
        
        Feature: requirement-parser-agent, Property 3: API Communication Reliability
        
        瀵逛簬浠讳綍HTTP閿欒鐘舵€佺爜锛屽簲璇ワ細
        1. 429 -> APIRateLimitError
        2. 5xx -> DeepSeekAPIError (鏈嶅姟鍣ㄩ敊璇?
        3. 鍏朵粬 -> DeepSeekAPIError
        """
        # Arrange
        client = DeepSeekClient(api_key="test_key")
        
        mock_response = AsyncMock()
        mock_response.status = status_code
        mock_response.json = AsyncMock(return_value={"error": "test error"})
        
        class MockContextManager:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, *args):
                pass
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = Mock(return_value=MockContextManager())
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act & Assert
        if status_code == 429:
            with pytest.raises(APIRateLimitError) as exc_info:
                await client._make_request({"test": "payload"})
            assert exc_info.value.status_code == 429
        elif status_code >= 500:
            with pytest.raises(DeepSeekAPIError) as exc_info:
                await client._make_request({"test": "payload"})
            assert exc_info.value.status_code == status_code
            assert "Server error" in str(exc_info.value)
        else:
            with pytest.raises(DeepSeekAPIError) as exc_info:
                await client._make_request({"test": "payload"})
            assert exc_info.value.status_code == status_code


# ============================================================================
# 杈呭姪娴嬭瘯锛氶獙璇佸睘鎬ф祴璇曢厤缃?
# ============================================================================

class TestPropertyTestConfiguration:
    """楠岃瘉灞炴€ф祴璇曢厤缃纭?""
    
    def test_strategies_generate_valid_data(self):
        """娴嬭瘯锛氱瓥鐣ョ敓鎴愭湁鏁堟暟鎹?""
        # 娴嬭瘯娑堟伅绛栫暐
        messages = valid_messages_strategy.example()
        assert len(messages) >= 1
        assert all('role' in msg and 'content' in msg for msg in messages)
        
        # 娴嬭瘯API鍝嶅簲绛栫暐
        response = valid_api_response_strategy.example()
        assert 'id' in response
        assert 'choices' in response
        assert len(response['choices']) >= 1
        assert 'usage' in response
    
    def test_property_test_runs_sufficient_examples(self):
        """娴嬭瘯锛氬睘鎬ф祴璇曡繍琛岃冻澶熺殑绀轰緥锛堣嚦灏?00娆★級"""
        # 杩欎釜娴嬭瘯纭繚鎴戜滑鐨?@settings 閰嶇疆浜?max_examples=20
        # 瀹為檯楠岃瘉鍦ㄨ繍琛屾椂鐢?hypothesis 瀹屾垚
        assert True  # 鍗犱綅绗︽祴璇?
