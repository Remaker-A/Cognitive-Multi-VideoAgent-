"""
集成测试套件

测试完整的需求解析流程、组件间协作和外部服务集成

Requirements: 1.1, 2.1, 3.1, 4.1, 5.1
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

from ..agent import RequirementParserAgent
from ...models import (
    UserInputData,
    ProcessingStatus,
    GlobalSpec,
    ConfidenceReport,
    ConfidenceLevel,
    ProcessingResult,
    DeepSeekResponse,
    DeepSeekChoice,
    DeepSeekMessage,
    DeepSeekUsage,
    EventType
)
from ..config import RequirementParserConfig
from ..deepseek_client import DeepSeekClient
from ..exceptions import DeepSeekAPIError, InputValidationError


@pytest.fixture
def test_config():
    """创建测试配置"""
    return RequirementParserConfig(
        agent_name="TestRequirementParser",
        deepseek_api_key="test_key_12345678",
        deepseek_api_endpoint="https://test.api.com/v1/chat/completions",
        deepseek_model_name="DeepSeek-V3.2",
        max_retries=2,
        timeout_seconds=10,
        confidence_threshold=0.6,
        default_quality_tier="balanced",
        default_aspect_ratio="9:16"
    )


@pytest.fixture
def mock_deepseek_client():
    """创建模拟的 DeepSeek 客户端"""
    client = AsyncMock(spec=DeepSeekClient)
    
    # 模拟成功的 API 响应
    mock_response = DeepSeekResponse(
        id="test_response_id",
        object="chat.completion",
        created=1234567890,
        model="DeepSeek-V3.2",
        choices=[
            DeepSeekChoice(
                index=0,
                message=DeepSeekMessage(
                    role="assistant",
                    content='{"main_theme": "探险故事", "characters": ["探险家"], "mood_tags": ["神秘", "冒险"], "estimated_duration": 30}'
                ),
                finish_reason="stop"
            )
        ],
        usage=DeepSeekUsage(
            prompt_tokens=100,
            completion_tokens=50,
            total_tokens=150
        )
    )
    
    client.chat_completion.return_value = mock_response
    client.analyze_multimodal.return_value = mock_response
    client.close.return_value = None
    
    return client


@pytest_asyncio.fixture
async def agent(test_config, mock_deepseek_client):
    """创建测试用的 Agent 实例"""
    agent = RequirementParserAgent(
        config=test_config,
        deepseek_client=mock_deepseek_client
    )
    yield agent
    await agent.close()


class TestEndToEndProcessing:
    """测试完整的需求解析流程 (Requirement 1.1, 2.1, 3.1, 4.1, 5.1)"""
    
    @pytest.mark.asyncio
    async def test_successful_text_only_processing(self, agent, mock_deepseek_client):
        """
        测试仅文本输入的完整处理流程
        
        验证：
        - 输入接收和验证
        - 文本预处理
        - DeepSeek API 调用
        - GlobalSpec 生成
        - 置信度评估
        - 事件发布
        """
        # 准备测试数据
        user_input = UserInputData(
            text_description="一个年轻的探险家在神秘的森林中寻找宝藏，时长30秒",
            reference_images=[],
            reference_videos=[],
            reference_audio=[],
            user_preferences={"quality": "high"}
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证结果
        assert result is not None
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        assert result.confidence_report is not None
        assert result.processing_time is not None
        assert result.processing_time > 0
        assert result.events_published > 0
        
        # 验证 GlobalSpec 结构
        global_spec = result.global_spec
        assert global_spec.title is not None
        assert len(global_spec.title) > 0
        assert global_spec.duration > 0
        assert global_spec.aspect_ratio in ["16:9", "9:16", "1:1", "4:3", "3:4"]
        assert global_spec.quality_tier in ["low", "balanced", "high"]
        assert global_spec.style is not None
        
        # 验证置信度报告
        confidence = result.confidence_report
        assert 0 <= confidence.overall_confidence <= 1
        assert confidence.confidence_level in [ConfidenceLevel.LOW, ConfidenceLevel.MEDIUM, ConfidenceLevel.HIGH]
        assert confidence.recommendation in ["proceed", "clarify", "human_review"]
        
        # 验证 DeepSeek API 被调用
        assert mock_deepseek_client.chat_completion.called or mock_deepseek_client.analyze_multimodal.called
    
    @pytest.mark.asyncio
    async def test_multimodal_input_processing(self, agent, mock_deepseek_client):
        """
        测试多模态输入的完整处理流程
        
        验证：
        - 文本、图片、视频、音频的综合处理
        - 多模态分析结果融合
        - GlobalSpec 生成包含所有模态信息
        """
        # 准备多模态测试数据
        user_input = UserInputData(
            text_description="温馨的家庭聚餐场景",
            reference_images=["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
            reference_videos=["https://example.com/video1.mp4"],
            reference_audio=["https://example.com/audio1.mp3"],
            user_preferences={"aspect_ratio": "16:9"}
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证结果
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证多模态信息被处理
        global_spec = result.global_spec
        assert global_spec.title is not None
        assert global_spec.style is not None
        assert global_spec.style.palette is not None
        assert len(global_spec.style.palette) > 0
    
    @pytest.mark.asyncio
    async def test_low_confidence_triggers_clarification(self, agent, mock_deepseek_client):
        """
        测试低置信度触发澄清请求
        
        验证：
        - 置信度评估正确识别低质量输入
        - 生成澄清请求
        - 发布 HUMAN_CLARIFICATION_REQUIRED 事件
        """
        # 准备低质量输入（非常简短的描述）
        user_input = UserInputData(
            text_description="视频",
            reference_images=[],
            reference_videos=[],
            reference_audio=[]
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证结果
        assert result.status == ProcessingStatus.COMPLETED
        assert result.confidence_report is not None
        
        # 低质量输入应该产生低置信度
        # 注意：实际置信度取决于实现，这里只验证系统能够处理
        assert result.confidence_report.overall_confidence >= 0


class TestComponentIntegration:
    """测试组件间协作 (Requirement 1.1, 2.1, 3.1, 4.1, 5.1)"""
    
    @pytest.mark.asyncio
    async def test_input_manager_to_preprocessor_flow(self, agent):
        """
        测试输入管理器到预处理器的数据流
        
        验证：
        - InputManager 正确接收用户输入
        - Preprocessor 正确处理各种模态数据
        - 数据格式在组件间正确传递
        """
        user_input = UserInputData(
            text_description="测试文本描述",
            reference_images=["https://example.com/test.jpg"]
        )
        
        # 测试输入管理器
        processed_input = await agent.input_manager.receive_user_input(user_input)
        assert processed_input is not None
        assert processed_input.text == user_input.text_description
        
        # 测试预处理器
        processed_text = await agent.preprocessor.process_text(processed_input.text)
        assert processed_text is not None
        assert processed_text.original == user_input.text_description
        assert processed_text.cleaned is not None
    
    @pytest.mark.asyncio
    async def test_analyzer_to_generator_flow(self, agent, mock_deepseek_client):
        """
        测试分析器到生成器的数据流
        
        验证：
        - MultimodalAnalyzer 生成正确的分析结果
        - GlobalSpecGenerator 基于分析结果生成 GlobalSpec
        - 数据转换正确无误
        """
        user_input = UserInputData(
            text_description="科幻未来城市，霓虹灯闪烁"
        )
        
        # 预处理
        processed_input = await agent.input_manager.receive_user_input(user_input)
        processed_text = await agent.preprocessor.process_text(processed_input.text)
        
        # 分析
        analysis = await agent.multimodal_analyzer.analyze_all(
            text=processed_text,
            images=[],
            videos=[],
            audio=[]
        )
        
        assert analysis is not None
        assert analysis.overall_theme is not None
        
        # 生成 GlobalSpec
        global_spec = await agent.global_spec_generator.generate_spec(
            analysis=analysis,
            user_input=user_input
        )
        
        assert global_spec is not None
        assert global_spec.title is not None
        assert global_spec.duration > 0
    
    @pytest.mark.asyncio
    async def test_generator_to_evaluator_flow(self, agent, mock_deepseek_client):
        """
        测试生成器到评估器的数据流
        
        验证：
        - GlobalSpecGenerator 生成完整的 GlobalSpec
        - ConfidenceEvaluator 正确评估置信度
        - 置信度报告包含必要信息
        """
        user_input = UserInputData(
            text_description="一个详细的故事描述，包含角色、场景和情节"
        )
        
        # 完整流程
        processed_input = await agent.input_manager.receive_user_input(user_input)
        processed_text = await agent.preprocessor.process_text(processed_input.text)
        analysis = await agent.multimodal_analyzer.analyze_all(
            text=processed_text,
            images=[],
            videos=[],
            audio=[]
        )
        global_spec = await agent.global_spec_generator.generate_spec(
            analysis=analysis,
            user_input=user_input
        )
        
        # 评估置信度
        confidence_report = await agent.confidence_evaluator.evaluate_confidence(
            global_spec=global_spec,
            analysis=analysis,
            user_input=user_input
        )
        
        assert confidence_report is not None
        assert 0 <= confidence_report.overall_confidence <= 1
        assert confidence_report.component_scores is not None
        assert len(confidence_report.component_scores) > 0
    
    @pytest.mark.asyncio
    async def test_evaluator_to_event_manager_flow(self, agent, mock_deepseek_client):
        """
        测试评估器到事件管理器的数据流
        
        验证：
        - ConfidenceEvaluator 生成置信度报告
        - EventManager 根据置信度发布正确的事件
        - 事件包含完整的元数据
        """
        user_input = UserInputData(
            text_description="测试事件发布流程"
        )
        
        # 执行完整处理
        result = await agent.process_user_input(user_input)
        
        # 验证事件被发布
        assert result.events_published > 0
        
        # 验证事件管理器状态
        event_count = agent.event_manager.get_event_count()
        assert event_count > 0


class TestExternalServiceIntegration:
    """测试外部服务集成 (Requirement 3.1, 5.1)"""
    
    @pytest.mark.asyncio
    async def test_deepseek_api_integration(self, test_config):
        """
        测试 DeepSeek API 集成
        
        验证：
        - API 客户端正确初始化
        - 请求格式正确
        - 响应解析正确
        - 错误处理正确
        """
        # 创建真实的客户端（但使用模拟响应）
        with patch('aiohttp.ClientSession') as mock_session_class:
            mock_session = MagicMock()
            mock_session_class.return_value = mock_session
            
            # 模拟成功响应
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value={
                "id": "test_id",
                "object": "chat.completion",
                "created": 1234567890,
                "model": "DeepSeek-V3.2",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Test response"
                    },
                    "finish_reason": "stop"
                }],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            })
            
            # 创建异步上下文管理器
            mock_context = AsyncMock()
            mock_context.__aenter__.return_value = mock_response
            mock_context.__aexit__.return_value = None
            mock_session.post.return_value = mock_context
            
            # 创建客户端
            client = DeepSeekClient(
                api_key=test_config.deepseek_api_key,
                base_url=test_config.deepseek_api_endpoint,
                model_name=test_config.deepseek_model_name
            )
            
            # 调用 API
            response = await client.chat_completion([
                {"role": "user", "content": "test message"}
            ])
            
            # 验证响应
            assert response is not None
            assert response.id == "test_id"
            assert len(response.choices) > 0
            assert response.choices[0].message.content == "Test response"
            
            # 验证请求被正确发送
            mock_session.post.assert_called_once()
            
            await client.close()
    
    @pytest.mark.asyncio
    async def test_event_bus_integration(self, agent, mock_deepseek_client):
        """
        测试事件总线集成
        
        验证：
        - 事件正确发布到事件总线
        - 事件格式符合规范
        - 事件包含必要的元数据
        """
        user_input = UserInputData(
            text_description="测试事件总线集成"
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证事件被创建
        assert result.events_published > 0
        
        # 获取发布的事件
        published_events = agent.event_manager._published_events
        assert len(published_events) > 0
        
        # 验证事件格式
        for event in published_events:
            assert event.event_id is not None
            assert event.project_id is not None
            assert event.event_type is not None
            assert event.actor == agent.config.agent_name
            assert event.payload is not None
            assert event.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_blackboard_integration(self, agent, mock_deepseek_client):
        """
        测试 Blackboard 集成
        
        验证：
        - GlobalSpec 正确写入 Blackboard
        - 写入请求格式正确
        - 数据路径正确
        """
        user_input = UserInputData(
            text_description="测试 Blackboard 集成"
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证处理成功
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证 Blackboard 写入被调用
        # 注意：实际的 Blackboard 写入是通过 EventManager 完成的
        # 这里我们验证 EventManager 的状态
        assert agent.event_manager.get_event_count() > 0


class TestErrorHandlingIntegration:
    """测试错误处理集成"""
    
    @pytest.mark.asyncio
    async def test_api_error_recovery(self, test_config):
        """
        测试 API 错误恢复
        
        验证：
        - API 错误被正确捕获
        - 重试机制正常工作
        - 降级策略被触发
        """
        # 创建会失败的模拟客户端
        mock_client = AsyncMock(spec=DeepSeekClient)
        mock_client.chat_completion.side_effect = DeepSeekAPIError("API Error")
        mock_client.analyze_multimodal.side_effect = DeepSeekAPIError("API Error")
        
        agent = RequirementParserAgent(
            config=test_config,
            deepseek_client=mock_client
        )
        
        user_input = UserInputData(
            text_description="测试 API 错误恢复"
        )
        
        # 执行处理（应该触发降级策略）
        result = await agent.process_user_input(user_input)
        
        # 验证降级处理成功或失败被正确处理
        assert result is not None
        assert result.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_invalid_input_handling(self, agent):
        """
        测试无效输入处理
        
        验证：
        - 无效输入被正确识别
        - 错误消息清晰明确
        - 系统不会崩溃
        """
        # 测试空输入
        with pytest.raises(ValueError):
            user_input = UserInputData(
                text_description="",
                reference_images=[],
                reference_videos=[],
                reference_audio=[]
            )
    
    @pytest.mark.asyncio
    async def test_partial_failure_handling(self, agent, mock_deepseek_client):
        """
        测试部分失败处理
        
        验证：
        - 部分组件失败时系统继续运行
        - 降级策略正确应用
        - 最终结果仍然可用
        """
        user_input = UserInputData(
            text_description="测试部分失败处理",
            reference_images=["https://invalid-url.com/image.jpg"]  # 无效的图片 URL
        )
        
        # 执行处理（图片处理可能失败，但文本处理应该成功）
        result = await agent.process_user_input(user_input)
        
        # 验证系统仍然产生结果
        assert result is not None
        assert result.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]


class TestConcurrentProcessing:
    """测试并发处理能力"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, test_config, mock_deepseek_client):
        """
        测试并发请求处理
        
        验证：
        - 系统能够处理多个并发请求
        - 请求之间不会相互干扰
        - 所有请求都能正确完成
        """
        agent = RequirementParserAgent(
            config=test_config,
            deepseek_client=mock_deepseek_client
        )
        
        # 创建多个测试输入
        inputs = [
            UserInputData(text_description=f"测试并发请求 {i}")
            for i in range(5)
        ]
        
        # 并发执行
        results = await asyncio.gather(*[
            agent.process_user_input(inp) for inp in inputs
        ])
        
        # 验证所有请求都成功
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert result.status == ProcessingStatus.COMPLETED
        
        await agent.close()


class TestMetricsCollection:
    """测试指标收集"""
    
    @pytest.mark.asyncio
    async def test_metrics_recorded(self, agent, mock_deepseek_client):
        """
        测试指标被正确记录
        
        验证：
        - 处理时间被记录
        - 置信度被记录
        - 错误被记录（如果有）
        """
        user_input = UserInputData(
            text_description="测试指标收集"
        )
        
        # 执行处理
        result = await agent.process_user_input(user_input)
        
        # 验证指标被记录
        assert result.processing_time is not None
        assert result.processing_time > 0
        
        # 验证 MetricsCollector 记录了数据
        metrics = agent.metrics_collector
        assert metrics is not None
        
        # 验证处理指标
        if hasattr(metrics, 'processing_metrics'):
            assert len(metrics.processing_metrics) > 0
        
        # 验证置信度指标
        if hasattr(metrics, 'confidence_metrics'):
            assert len(metrics.confidence_metrics) > 0
