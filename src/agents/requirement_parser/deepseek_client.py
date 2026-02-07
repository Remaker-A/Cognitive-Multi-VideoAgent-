"""
DeepSeek API 客户端

负责封装对 DeepSeek-V3.2 模型的调用，提供多模态分析能力
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import asdict

from .config import config
from .models import (
    DeepSeekRequest,
    DeepSeekResponse,
    DeepSeekMessage,
    DeepSeekChoice,
    DeepSeekUsage,
    MultimodalAnalysisResponse
)
from .exceptions import (
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError,
    MaxRetriesExceededError
)
from .metrics_collector import global_metrics_collector, MetricsCollector
from .models import Money

logger = logging.getLogger(__name__)


class DeepSeekClient:
    """
    DeepSeek API 客户端
    
    封装对 DeepSeek-V3.2 模型的 HTTP 调用，提供：
    - 基础的 chat_completion 方法
    - 多模态分析接口
    - 自动重试和错误处理
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        初始化 DeepSeek 客户端
        
        Args:
            api_key: API 密钥，默认从配置读取
            base_url: API 端点，默认从配置读取
            model_name: 模型名称，默认从配置读取
            timeout: 请求超时时间（秒），默认从配置读取
            max_retries: 最大重试次数，默认从配置读取
            metrics_collector: 指标收集器，默认使用全局实例
        """
        self.api_key = api_key or config.deepseek_api_key
        self.base_url = base_url or config.deepseek_api_endpoint
        self.model_name = model_name or config.deepseek_model_name
        self.timeout = timeout or config.timeout_seconds
        self.max_retries = max_retries or config.max_retries
        self.metrics_collector = metrics_collector or global_metrics_collector
        
        # 创建 aiohttp session（延迟初始化）
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建 aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def close(self) -> None:
        """关闭 HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs
    ) -> DeepSeekResponse:
        """
        调用 DeepSeek 聊天完成 API
        
        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            model: 模型名称，默认使用配置的模型
            temperature: 温度参数（0-1），控制随机性
            max_tokens: 最大生成 token 数
            **kwargs: 其他 API 参数
        
        Returns:
            DeepSeekResponse: API 响应对象
        
        Raises:
            DeepSeekAPIError: API 调用失败
            APITimeoutError: 请求超时
            APIRateLimitError: 触发限流
            NetworkError: 网络错误
        """
        import time
        start_time = time.time()
        
        # 构建请求对象
        request = DeepSeekRequest(
            model=model or self.model_name,
            messages=[
                DeepSeekMessage(role=msg["role"], content=msg["content"])
                for msg in messages
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        logger.info(
            f"Calling DeepSeek API: model={request.model}, "
            f"messages_count={len(request.messages)}"
        )
        
        try:
            # 发送请求
            response_data = await self._make_request(asdict(request))
            
            # 解析响应
            try:
                response = DeepSeekResponse(
                    id=response_data.get("id", ""),
                    object=response_data.get("object", "chat.completion"),
                    created=response_data.get("created", 0),
                    model=response_data.get("model", request.model),
                    choices=[
                        DeepSeekChoice(
                            index=choice.get("index", 0),
                            message=DeepSeekMessage(
                                role=choice["message"]["role"],
                                content=choice["message"]["content"]
                            ),
                            finish_reason=choice.get("finish_reason", "stop")
                        )
                        for choice in response_data.get("choices", [])
                    ],
                    usage=DeepSeekUsage(
                        prompt_tokens=response_data.get("usage", {}).get("prompt_tokens", 0),
                        completion_tokens=response_data.get("usage", {}).get("completion_tokens", 0),
                        total_tokens=response_data.get("usage", {}).get("total_tokens", 0)
                    )
                )
                
                # 计算延迟和成本
                latency_ms = int((time.time() - start_time) * 1000)
                # 简化的成本计算：每1000 tokens约$0.001
                cost = Money(
                    amount=response.usage.total_tokens * 0.001 / 1000,
                    currency="USD"
                )
                
                # 记录 API 调用指标 (Requirement 8.1)
                self.metrics_collector.record_api_call(
                    endpoint=self.base_url,
                    model=response.model,
                    latency_ms=latency_ms,
                    cost=cost,
                    tokens_used=response.usage.total_tokens,
                    success=True,
                    error_type=None
                )
                
                logger.info(
                    f"DeepSeek API call successful: "
                    f"tokens={response.usage.total_tokens}, "
                    f"latency={latency_ms}ms, "
                    f"finish_reason={response.choices[0].finish_reason if response.choices else 'none'}"
                )
                
                return response
                
            except (KeyError, IndexError, TypeError) as e:
                logger.error(f"Failed to parse DeepSeek API response: {e}")
                
                # 记录解析错误
                latency_ms = int((time.time() - start_time) * 1000)
                self.metrics_collector.record_api_call(
                    endpoint=self.base_url,
                    model=request.model,
                    latency_ms=latency_ms,
                    cost=Money(amount=0.0, currency="USD"),
                    tokens_used=0,
                    success=False,
                    error_type="ParseError"
                )
                
                raise DeepSeekAPIError(
                    f"Invalid API response format: {e}",
                    response_data=response_data
                )
        
        except (DeepSeekAPIError, APITimeoutError, APIRateLimitError, NetworkError) as e:
            # 记录 API 调用失败指标
            latency_ms = int((time.time() - start_time) * 1000)
            self.metrics_collector.record_api_call(
                endpoint=self.base_url,
                model=request.model,
                latency_ms=latency_ms,
                cost=Money(amount=0.0, currency="USD"),
                tokens_used=0,
                success=False,
                error_type=type(e).__name__
            )
            raise
    
    async def analyze_multimodal(
        self,
        text: str,
        images: Optional[List[str]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> MultimodalAnalysisResponse:
        """
        多模态分析接口
        
        分析文本和图像输入，提取关键信息用于 GlobalSpec 生成
        
        Args:
            text: 文本描述
            images: 图像 URL 列表（可选）
            system_prompt: 系统提示词（可选）
            temperature: 温度参数
        
        Returns:
            MultimodalAnalysisResponse: 分析结果
        
        Raises:
            DeepSeekAPIError: API 调用失败
        """
        # 构建消息
        messages = []
        
        # 添加系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "你是一个专业的视频需求分析助手。"
                    "请分析用户的输入，提取关键信息，包括：主题、角色、场景、情绪、风格等。"
                    "以结构化的 JSON 格式返回分析结果。"
                )
            })
        
        # 添加用户输入
        user_content = text
        if images:
            user_content += f"\n\n参考图片: {', '.join(images)}"
        
        messages.append({"role": "user", "content": user_content})
        
        # 调用 API
        response = await self.chat_completion(
            messages=messages,
            temperature=temperature,
            max_tokens=2000
        )
        
        # 提取分析结果
        if not response.choices:
            raise DeepSeekAPIError("No choices in API response")
        
        analysis_text = response.choices[0].message.content
        
        # 构建分析响应
        return MultimodalAnalysisResponse(
            analysis_text=analysis_text,
            confidence=0.8,  # 默认置信度，后续可以通过更复杂的逻辑计算
            tokens_used=response.usage.total_tokens,
            model_used=response.model
        )
    
    async def _make_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        底层 HTTP 请求封装
        
        Args:
            payload: 请求负载
        
        Returns:
            API 响应数据
        
        Raises:
            DeepSeekAPIError: API 调用失败
            APITimeoutError: 请求超时
            APIRateLimitError: 触发限流
            NetworkError: 网络错误
        """
        session = await self._get_session()
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with session.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                response_data = await response.json()
                
                # 检查 HTTP 状态码
                if response.status == 200:
                    return response_data
                elif response.status == 429:
                    raise APIRateLimitError(
                        "API rate limit exceeded",
                        status_code=response.status,
                        response_data=response_data
                    )
                elif response.status >= 500:
                    raise DeepSeekAPIError(
                        f"Server error: {response.status}",
                        status_code=response.status,
                        response_data=response_data
                    )
                else:
                    raise DeepSeekAPIError(
                        f"API call failed with status {response.status}",
                        status_code=response.status,
                        response_data=response_data
                    )
        
        except asyncio.TimeoutError:
            logger.error(f"Request timeout after {self.timeout}s")
            raise APITimeoutError(
                f"Request timeout after {self.timeout}s",
                status_code=408
            )
        
        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            raise NetworkError(f"Network error: {e}")
    
    async def retry_with_exponential_backoff(
        self,
        func,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0
    ) -> Any:
        """
        使用指数退避策略重试函数
        
        Args:
            func: 要重试的异步函数
            initial_delay: 初始延迟（秒）
            backoff_factor: 退避因子
        
        Returns:
            函数执行结果
        
        Raises:
            MaxRetriesExceededError: 超过最大重试次数
        """
        delay = initial_delay
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                return await func()
            except (APITimeoutError, APIRateLimitError, NetworkError) as e:
                last_exception = e
                
                if attempt == self.max_retries - 1:
                    logger.error(
                        f"Max retries ({self.max_retries}) exceeded. Last error: {e}"
                    )
                    raise MaxRetriesExceededError(
                        f"Failed after {self.max_retries} attempts: {e}",
                        retry_count=self.max_retries
                    )
                
                logger.warning(
                    f"Attempt {attempt + 1}/{self.max_retries} failed: {e}. "
                    f"Retrying in {delay}s..."
                )
                
                await asyncio.sleep(delay)
                delay *= backoff_factor
        
        # 不应该到达这里，但为了类型检查
        raise MaxRetriesExceededError(
            f"Failed after {self.max_retries} attempts",
            retry_count=self.max_retries
        )
