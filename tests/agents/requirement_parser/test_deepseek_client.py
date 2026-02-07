"""
DeepSeekClient 单元测试和集成测试
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
import aiohttp
import asyncio
from typing import Dict, Any

from src.agents.requirement_parser.deepseek_client import DeepSeekClient
from src.agents.requirement_parser.models import (
    DeepSeekResponse,
    DeepSeekChoice,
    DeepSeekMessage,
    DeepSeekUsage,
    MultimodalAnalysisResponse
)
from src.agents.requirement_parser.exceptions import (
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError,
    MaxRetriesExceededError
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def client():
    """创建 DeepSeekClient 实例"""
    return DeepSeekClient(
        api_key="test_api_key",
        base_url="https://test.api.com/v1/chat/completions",
        model_name="DeepSeek-V3.2",
        timeout=30,
        max_retries=3
    )


@pytest.fixture
def sample_messages():
    """创建测试消息"""
    return [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "你好"}
    ]


@pytest.fixture
def mock_api_response():
    """创建模拟的 API 响应"""
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "model": "DeepSeek-V3.2",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "你好！我是 DeepSeek 助手。"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


# ============================================================================
# 单元测试 - 初始化和配置
# ============================================================================

class TestDeepSeekClientInitialization:
    """测试 DeepSeekClient 初始化"""
    
    def test_init_with_custom_params(self):
        """测试：使用自定义参数初始化"""
        # Arrange & Act
        client = DeepSeekClient(
            api_key="custom_key",
            base_url="https://custom.api.com",
            model_name="custom-model",
            timeout=60,
            max_retries=5
        )
        
        # Assert
        assert client.api_key == "custom_key"
        assert client.base_url == "https://custom.api.com"
        assert client.model_name == "custom-model"
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_init_with_default_params(self):
        """测试：使用默认参数初始化（从配置读取）"""
        # Arrange & Act
        client = DeepSeekClient()
        
        # Assert
        assert client.api_key is not None
        assert client.base_url is not None
        assert client.model_name is not None
        assert client.timeout > 0
        assert client.max_retries >= 0
    
    def test_session_lazy_initialization(self, client):
        """测试：session 延迟初始化"""
        # Assert
        assert client._session is None


# ============================================================================
# 单元测试 - chat_completion 方法
# ============================================================================

class TestChatCompletion:
    """测试 chat_completion 方法"""
    
    @pytest.mark.asyncio
    async def test_chat_completion_success(self, client, sample_messages, mock_api_response):
        """测试：成功调用 chat_completion"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        
        # Act
        response = await client.chat_completion(messages=sample_messages)
        
        # Assert
        assert isinstance(response, DeepSeekResponse)
        assert response.id == "chatcmpl-123"
        assert response.model == "DeepSeek-V3.2"
        assert len(response.choices) == 1
        assert response.choices[0].message.content == "你好！我是 DeepSeek 助手。"
        assert response.usage.total_tokens == 30
        
        # 验证 _make_request 被调用
        client._make_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_chat_completion_with_custom_params(self, client, sample_messages, mock_api_response):
        """测试：使用自定义参数调用 chat_completion"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        
        # Act
        response = await client.chat_completion(
            messages=sample_messages,
            model="custom-model",
            temperature=0.5,
            max_tokens=1000
        )
        
        # Assert
        assert isinstance(response, DeepSeekResponse)
        client._make_request.assert_called_once()
        
        # 验证请求参数
        call_args = client._make_request.call_args[0][0]
        assert call_args["model"] == "custom-model"
        assert call_args["temperature"] == 0.5
        assert call_args["max_tokens"] == 1000
    
    @pytest.mark.asyncio
    async def test_chat_completion_invalid_response_format(self, client, sample_messages):
        """测试：API 返回无效格式（choices中缺少必需字段）"""
        # Arrange - 返回一个choices中message字段格式错误的响应
        invalid_response = {
            "id": "test",
            "object": "chat.completion",
            "created": 123,
            "model": "test",
            "choices": [
                {
                    "index": 0,
                    "message": {},  # 缺少role和content字段
                    "finish_reason": "stop"
                }
            ],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        
        # Directly mock _make_request to return invalid response
        async def mock_make_request(payload):
            return invalid_response
        
        client._make_request = mock_make_request
        
        # Act & Assert
        with pytest.raises(DeepSeekAPIError) as exc_info:
            await client.chat_completion(messages=sample_messages)
        
        assert "Invalid API response format" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_chat_completion_empty_choices(self, client, sample_messages):
        """测试：API 返回空 choices"""
        # Arrange
        response_with_empty_choices = {
            "id": "test",
            "object": "chat.completion",
            "created": 123,
            "model": "test",
            "choices": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        client._make_request = AsyncMock(return_value=response_with_empty_choices)
        
        # Act
        response = await client.chat_completion(messages=sample_messages)
        
        # Assert
        assert len(response.choices) == 0


# ============================================================================
# 单元测试 - analyze_multimodal 方法
# ============================================================================

class TestAnalyzeMultimodal:
    """测试 analyze_multimodal 方法"""
    
    @pytest.mark.asyncio
    async def test_analyze_multimodal_text_only(self, client, mock_api_response):
        """测试：仅文本的多模态分析"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        
        # Act
        response = await client.analyze_multimodal(
            text="一个年轻的探险家在森林中寻找宝藏"
        )
        
        # Assert
        assert isinstance(response, MultimodalAnalysisResponse)
        assert response.analysis_text == "你好！我是 DeepSeek 助手。"
        assert response.confidence > 0
        assert response.tokens_used == 30
        assert response.model_used == "DeepSeek-V3.2"
    
    @pytest.mark.asyncio
    async def test_analyze_multimodal_with_images(self, client, mock_api_response):
        """测试：包含图片的多模态分析"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        images = ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        
        # Act
        response = await client.analyze_multimodal(
            text="分析这些图片的风格",
            images=images
        )
        
        # Assert
        assert isinstance(response, MultimodalAnalysisResponse)
        client._make_request.assert_called_once()
        
        # 验证图片 URL 被包含在请求中
        call_args = client._make_request.call_args[0][0]
        user_message = call_args["messages"][-1]["content"]
        assert "image1.jpg" in user_message
        assert "image2.jpg" in user_message
    
    @pytest.mark.asyncio
    async def test_analyze_multimodal_with_custom_system_prompt(self, client, mock_api_response):
        """测试：使用自定义系统提示"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        custom_prompt = "你是一个专业的视频分析师"
        
        # Act
        response = await client.analyze_multimodal(
            text="分析视频需求",
            system_prompt=custom_prompt
        )
        
        # Assert
        assert isinstance(response, MultimodalAnalysisResponse)
        
        # 验证系统提示被使用
        call_args = client._make_request.call_args[0][0]
        system_message = call_args["messages"][0]["content"]
        assert system_message == custom_prompt
    
    @pytest.mark.asyncio
    async def test_analyze_multimodal_no_choices(self, client):
        """测试：API 返回无 choices"""
        # Arrange
        response_no_choices = {
            "id": "test",
            "object": "chat.completion",
            "created": 123,
            "model": "test",
            "choices": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
        client._make_request = AsyncMock(return_value=response_no_choices)
        
        # Act & Assert
        with pytest.raises(DeepSeekAPIError) as exc_info:
            await client.analyze_multimodal(text="test")
        
        assert "No choices in API response" in str(exc_info.value)


# ============================================================================
# 单元测试 - _make_request 方法
# ============================================================================

class TestMakeRequest:
    """测试 _make_request 方法"""
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, client, mock_api_response):
        """测试：成功的 HTTP 请求"""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock()
        ))
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act
        result = await client._make_request({"test": "payload"})
        
        # Assert
        assert result == mock_api_response
        mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_rate_limit_error(self, client):
        """测试：触发限流错误（429）"""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(return_value={"error": "rate limit exceeded"})
        
        # Create a proper async context manager
        class MockContextManager:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, *args):
                pass
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = Mock(return_value=MockContextManager())
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act & Assert
        with pytest.raises(APIRateLimitError) as exc_info:
            await client._make_request({"test": "payload"})
        
        assert exc_info.value.status_code == 429
    
    @pytest.mark.asyncio
    async def test_make_request_server_error(self, client):
        """测试：服务器错误（500）"""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.json = AsyncMock(return_value={"error": "internal server error"})
        
        # Create a proper async context manager
        class MockContextManager:
            async def __aenter__(self):
                return mock_response
            async def __aexit__(self, *args):
                pass
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = Mock(return_value=MockContextManager())
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act & Assert
        with pytest.raises(DeepSeekAPIError) as exc_info:
            await client._make_request({"test": "payload"})
        
        assert exc_info.value.status_code == 500
        assert "Server error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_timeout(self, client):
        """测试：请求超时"""
        # Arrange
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = MagicMock(side_effect=asyncio.TimeoutError())
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act & Assert
        with pytest.raises(APITimeoutError) as exc_info:
            await client._make_request({"test": "payload"})
        
        assert "timeout" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_make_request_network_error(self, client):
        """测试：网络错误"""
        # Arrange
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.post = MagicMock(side_effect=aiohttp.ClientError("Connection failed"))
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act & Assert
        with pytest.raises(NetworkError) as exc_info:
            await client._make_request({"test": "payload"})
        
        assert "Network error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_make_request_headers(self, client):
        """测试：请求头正确设置"""
        # Arrange
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"test": "response"})
        
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_post = MagicMock(return_value=AsyncMock(
            __aenter__=AsyncMock(return_value=mock_response),
            __aexit__=AsyncMock()
        ))
        mock_session.post = mock_post
        
        # Mock _get_session to return our mock session
        client._get_session = AsyncMock(return_value=mock_session)
        
        # Act
        await client._make_request({"test": "payload"})
        
        # Assert
        call_kwargs = mock_post.call_args[1]
        headers = call_kwargs["headers"]
        assert headers["Authorization"] == f"Bearer {client.api_key}"
        assert headers["Content-Type"] == "application/json"


# ============================================================================
# 单元测试 - 重试机制
# ============================================================================

class TestRetryMechanism:
    """测试重试机制"""
    
    @pytest.mark.asyncio
    async def test_retry_success_on_second_attempt(self, client):
        """测试：第二次尝试成功"""
        # Arrange
        attempt_count = 0
        
        async def mock_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise APITimeoutError("First attempt failed")
            return "success"
        
        # Act
        result = await client.retry_with_exponential_backoff(mock_func, initial_delay=0.1)
        
        # Assert
        assert result == "success"
        assert attempt_count == 2
    
    @pytest.mark.asyncio
    async def test_retry_max_retries_exceeded(self, client):
        """测试：超过最大重试次数"""
        # Arrange
        async def mock_func():
            raise APITimeoutError("Always fails")
        
        # Act & Assert
        with pytest.raises(MaxRetriesExceededError) as exc_info:
            await client.retry_with_exponential_backoff(mock_func, initial_delay=0.1)
        
        assert exc_info.value.retry_count == client.max_retries
    
    @pytest.mark.asyncio
    async def test_retry_exponential_backoff_timing(self, client):
        """测试：指数退避延迟"""
        # Arrange
        attempt_times = []
        
        async def mock_func():
            attempt_times.append(asyncio.get_event_loop().time())
            raise NetworkError("Network error")
        
        # Act
        try:
            await client.retry_with_exponential_backoff(
                mock_func,
                initial_delay=0.1,
                backoff_factor=2.0
            )
        except MaxRetriesExceededError:
            pass
        
        # Assert
        assert len(attempt_times) == client.max_retries
        
        # 验证延迟递增（允许一定误差）
        if len(attempt_times) >= 2:
            delay1 = attempt_times[1] - attempt_times[0]
            assert delay1 >= 0.08  # 0.1s with tolerance
    
    @pytest.mark.asyncio
    async def test_retry_only_retryable_errors(self, client):
        """测试：只重试可重试的错误"""
        # Arrange
        attempt_count = 0
        
        async def mock_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count == 1:
                raise APITimeoutError("Timeout")
            elif attempt_count == 2:
                raise APIRateLimitError("Rate limit")
            else:
                return "success"
        
        # Act
        result = await client.retry_with_exponential_backoff(mock_func, initial_delay=0.1)
        
        # Assert
        assert result == "success"
        assert attempt_count == 3


# ============================================================================
# 单元测试 - Session 管理
# ============================================================================

class TestSessionManagement:
    """测试 Session 管理"""
    
    @pytest.mark.asyncio
    async def test_get_session_creates_new_session(self, client):
        """测试：获取 session 时创建新 session"""
        # Act
        session = await client._get_session()
        
        # Assert
        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)
        assert not session.closed
    
    @pytest.mark.asyncio
    async def test_get_session_reuses_existing_session(self, client):
        """测试：重用已存在的 session"""
        # Arrange
        session1 = await client._get_session()
        
        # Act
        session2 = await client._get_session()
        
        # Assert
        assert session1 is session2
    
    @pytest.mark.asyncio
    async def test_close_session(self, client):
        """测试：关闭 session"""
        # Arrange
        session = await client._get_session()
        
        # Act
        await client.close()
        
        # Assert
        assert session.closed
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """测试：异步上下文管理器"""
        # Act & Assert
        async with DeepSeekClient(api_key="test") as client:
            assert client is not None
            session = await client._get_session()
            assert not session.closed
        
        # Session 应该被关闭
        assert session.closed


# ============================================================================
# 集成测试（需要真实 API 或 Mock Server）
# ============================================================================

class TestIntegration:
    """集成测试"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_chat_completion_flow(self, client, mock_api_response):
        """测试：完整的 chat_completion 流程"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        
        messages = [
            {"role": "system", "content": "你是一个助手"},
            {"role": "user", "content": "你好"}
        ]
        
        # Act
        response = await client.chat_completion(messages=messages)
        
        # Assert
        assert response.id == "chatcmpl-123"
        assert len(response.choices) > 0
        assert response.usage.total_tokens > 0
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_full_multimodal_analysis_flow(self, client, mock_api_response):
        """测试：完整的多模态分析流程"""
        # Arrange
        client._make_request = AsyncMock(return_value=mock_api_response)
        
        # Act
        response = await client.analyze_multimodal(
            text="一个年轻的探险家在森林中寻找宝藏",
            images=["https://example.com/forest.jpg"]
        )
        
        # Assert
        assert isinstance(response, MultimodalAnalysisResponse)
        assert response.analysis_text is not None
        assert response.tokens_used > 0
