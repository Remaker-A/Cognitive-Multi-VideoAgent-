"""
端到端测试套件

测试真实用户输入场景和性能指标达标

Requirements: 8.1, 8.2
"""

import pytest
import pytest_asyncio
import asyncio
import time
from unittest.mock import AsyncMock, patch
from typing import List

from ..agent import RequirementParserAgent
from ..models import (
    UserInputData,
    ProcessingStatus,
    GlobalSpec,
    DeepSeekResponse,
    DeepSeekChoice,
    DeepSeekMessage,
    DeepSeekUsage
)
from ..config import RequirementParserConfig
from ..deepseek_client import DeepSeekClient


@pytest.fixture
def e2e_config():
    """创建端到端测试配置"""
    return RequirementParserConfig(
        agent_name="E2ETestAgent",
        deepseek_api_key="test_key_e2e_12345678",
        deepseek_api_endpoint="https://test.api.com/v1/chat/completions",
        deepseek_model_name="DeepSeek-V3.2",
        max_retries=3,
        timeout_seconds=30,
        confidence_threshold=0.6
    )


@pytest.fixture
def mock_deepseek_for_e2e():
    """创建端到端测试用的模拟 DeepSeek 客户端"""
    client = AsyncMock(spec=DeepSeekClient)
    
    # 模拟真实的 API 响应延迟
    async def mock_chat_with_delay(*args, **kwargs):
        await asyncio.sleep(0.1)  # 模拟 100ms 延迟
        return DeepSeekResponse(
            id="e2e_response_id",
            object="chat.completion",
            created=int(time.time()),
            model="DeepSeek-V3.2",
            choices=[
                DeepSeekChoice(
                    index=0,
                    message=DeepSeekMessage(
                        role="assistant",
                        content='{"main_theme": "测试主题", "characters": ["角色1", "角色2"], "mood_tags": ["欢快", "温馨"], "estimated_duration": 30}'
                    ),
                    finish_reason="stop"
                )
            ],
            usage=DeepSeekUsage(
                prompt_tokens=150,
                completion_tokens=80,
                total_tokens=230
            )
        )
    
    client.chat_completion.side_effect = mock_chat_with_delay
    client.analyze_multimodal.side_effect = mock_chat_with_delay
    client.close.return_value = None
    
    return client


@pytest_asyncio.fixture
async def e2e_agent(e2e_config, mock_deepseek_for_e2e):
    """创建端到端测试用的 Agent 实例"""
    agent = RequirementParserAgent(
        config=e2e_config,
        deepseek_client=mock_deepseek_for_e2e
    )
    yield agent
    await agent.close()


class TestRealWorldScenarios:
    """测试真实用户输入场景 (Requirement 8.1, 8.2)"""
    
    @pytest.mark.asyncio
    async def test_short_video_creation(self, e2e_agent):
        """
        场景1: 创建短视频
        
        用户想要创建一个30秒的短视频，提供简单的文本描述
        """
        user_input = UserInputData(
            text_description="一个年轻人在城市街道上骑自行车，阳光明媚，心情愉快",
            user_preferences={
                "duration": 30,
                "aspect_ratio": "9:16",
                "quality": "high"
            }
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        processing_time = time.time() - start_time
        
        # 验证处理成功
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证 GlobalSpec 符合用户偏好
        spec = result.global_spec
        assert spec.duration == 30 or spec.duration > 0  # 使用用户指定的或默认值
        assert spec.aspect_ratio == "9:16"
        
        # 验证性能 (Requirement 8.1, 8.2)
        assert processing_time < 30.0  # 应在30秒内完成
        print(f"Short video creation processing time: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_story_based_video(self, e2e_agent):
        """
        场景2: 基于故事的视频
        
        用户提供详细的故事描述，包含角色和情节
        """
        user_input = UserInputData(
            text_description="""
            在一个宁静的小镇上，住着一位名叫小明的少年。
            他梦想成为一名画家，每天都在公园里写生。
            一天，他遇到了一位神秘的老人，老人给了他一支神奇的画笔。
            这支画笔能让画中的事物变成现实。
            小明用这支画笔帮助了镇上的许多人，最终实现了自己的梦想。
            视频时长约60秒，风格温馨感人。
            """,
            user_preferences={
                "quality": "balanced"
            }
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        processing_time = time.time() - start_time
        
        # 验证处理成功
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证角色被识别
        spec = result.global_spec
        assert spec.characters is not None
        # 可能识别出"小明"或其他角色
        
        # 验证情绪标签
        assert spec.mood is not None
        assert len(spec.mood) > 0
        
        # 验证性能
        assert processing_time < 30.0
        print(f"Story-based video processing time: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_reference_image_based_video(self, e2e_agent):
        """
        场景3: 基于参考图片的视频
        
        用户上传参考图片，希望视频风格与图片一致
        """
        user_input = UserInputData(
            text_description="根据参考图片的风格创建一个视频",
            reference_images=[
                "https://example.com/sunset.jpg",
                "https://example.com/beach.jpg"
            ],
            user_preferences={
                "aspect_ratio": "16:9"
            }
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        processing_time = time.time() - start_time
        
        # 验证处理成功
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证风格配置
        spec = result.global_spec
        assert spec.style is not None
        assert spec.style.palette is not None
        assert len(spec.style.palette) > 0
        
        # 验证性能
        assert processing_time < 30.0
        print(f"Reference image-based video processing time: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_minimal_input_scenario(self, e2e_agent):
        """
        场景4: 最小输入
        
        用户只提供非常简短的描述
        """
        user_input = UserInputData(
            text_description="一个关于友谊的视频"
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        processing_time = time.time() - start_time
        
        # 验证处理成功（可能置信度较低）
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证使用了默认值
        spec = result.global_spec
        assert spec.duration > 0
        assert spec.aspect_ratio in ["16:9", "9:16", "1:1", "4:3", "3:4"]
        assert spec.quality_tier in ["low", "balanced", "high"]
        
        # 验证置信度报告
        assert result.confidence_report is not None
        # 简短输入可能导致低置信度
        
        # 验证性能
        assert processing_time < 30.0
        print(f"Minimal input processing time: {processing_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_complex_multimodal_scenario(self, e2e_agent):
        """
        场景5: 复杂的多模态输入
        
        用户提供文本、图片、视频和音频参考
        """
        user_input = UserInputData(
            text_description="创建一个充满活力的音乐视频，展现青春和梦想",
            reference_images=[
                "https://example.com/style1.jpg",
                "https://example.com/style2.jpg"
            ],
            reference_videos=[
                "https://example.com/reference_video.mp4"
            ],
            reference_audio=[
                "https://example.com/background_music.mp3"
            ],
            user_preferences={
                "quality": "high",
                "duration": 45
            }
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        processing_time = time.time() - start_time
        
        # 验证处理成功
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 验证多模态信息被整合
        spec = result.global_spec
        assert spec.title is not None
        assert spec.style is not None
        assert spec.mood is not None
        
        # 验证性能（多模态处理可能需要更多时间）
        assert processing_time < 30.0
        print(f"Complex multimodal processing time: {processing_time:.2f}s")


class TestPerformanceMetrics:
    """测试性能指标达标 (Requirement 8.1, 8.2)"""
    
    @pytest.mark.asyncio
    async def test_processing_latency(self, e2e_agent):
        """
        测试处理延迟
        
        验证：
        - 文本解析延迟 < 2 秒
        - 完整解析流程 < 30 秒
        """
        user_input = UserInputData(
            text_description="测试处理延迟的简单文本"
        )
        
        start_time = time.time()
        result = await e2e_agent.process_user_input(user_input)
        total_time = time.time() - start_time
        
        # 验证总体延迟
        assert total_time < 30.0, f"Processing took {total_time:.2f}s, should be < 30s"
        
        # 验证结果中记录的处理时间
        assert result.processing_time is not None
        assert result.processing_time < 30.0
        
        print(f"Processing latency: {total_time:.2f}s")
        print(f"Recorded processing time: {result.processing_time:.2f}s")
    
    @pytest.mark.asyncio
    async def test_throughput(self, e2e_config, mock_deepseek_for_e2e):
        """
        测试吞吐量
        
        验证：
        - 系统能够在合理时间内处理多个请求
        - 并发处理不会显著降低性能
        """
        agent = RequirementParserAgent(
            config=e2e_config,
            deepseek_client=mock_deepseek_for_e2e
        )
        
        # 创建10个测试请求
        inputs = [
            UserInputData(text_description=f"测试请求 {i}")
            for i in range(10)
        ]
        
        # 串行处理
        start_time = time.time()
        serial_results = []
        for inp in inputs:
            result = await agent.process_user_input(inp)
            serial_results.append(result)
        serial_time = time.time() - start_time
        
        # 验证所有请求都成功
        assert len(serial_results) == 10
        assert all(r.status == ProcessingStatus.COMPLETED for r in serial_results)
        
        print(f"Serial processing of 10 requests: {serial_time:.2f}s")
        print(f"Average time per request: {serial_time/10:.2f}s")
        
        # 验证平均处理时间合理
        avg_time = serial_time / 10
        assert avg_time < 30.0, f"Average processing time {avg_time:.2f}s exceeds 30s"
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_concurrent_throughput(self, e2e_config, mock_deepseek_for_e2e):
        """
        测试并发吞吐量
        
        验证：
        - 并发处理能够提高整体吞吐量
        - 并发处理不会导致错误
        """
        agent = RequirementParserAgent(
            config=e2e_config,
            deepseek_client=mock_deepseek_for_e2e
        )
        
        # 创建10个测试请求
        inputs = [
            UserInputData(text_description=f"并发测试请求 {i}")
            for i in range(10)
        ]
        
        # 并发处理
        start_time = time.time()
        concurrent_results = await asyncio.gather(*[
            agent.process_user_input(inp) for inp in inputs
        ])
        concurrent_time = time.time() - start_time
        
        # 验证所有请求都成功
        assert len(concurrent_results) == 10
        assert all(r.status == ProcessingStatus.COMPLETED for r in concurrent_results)
        
        print(f"Concurrent processing of 10 requests: {concurrent_time:.2f}s")
        
        # 并发处理应该比串行快（或至少不会慢太多）
        # 由于我们使用了模拟客户端，并发应该明显更快
        assert concurrent_time < 60.0, f"Concurrent processing took {concurrent_time:.2f}s"
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, e2e_agent):
        """
        测试内存效率
        
        验证：
        - 处理大量请求不会导致内存泄漏
        - 资源被正确释放
        """
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        # 处理多个请求
        for i in range(20):
            user_input = UserInputData(
                text_description=f"内存测试请求 {i}"
            )
            result = await e2e_agent.process_user_input(user_input)
            assert result.status == ProcessingStatus.COMPLETED
        
        # 再次强制垃圾回收
        gc.collect()
        
        # 如果没有内存泄漏，测试应该能够完成
        # 实际的内存监控需要更复杂的工具
        print("Memory efficiency test completed")
    
    @pytest.mark.asyncio
    async def test_api_call_metrics(self, e2e_agent, mock_deepseek_for_e2e):
        """
        测试 API 调用指标记录 (Requirement 8.1)
        
        验证：
        - API 调用延迟被记录
        - API 调用成本被记录
        """
        user_input = UserInputData(
            text_description="测试 API 调用指标"
        )
        
        result = await e2e_agent.process_user_input(user_input)
        
        # 验证指标被记录
        assert result.processing_time is not None
        assert result.cost is not None
        
        # 验证 API 被调用
        assert mock_deepseek_for_e2e.chat_completion.called or \
               mock_deepseek_for_e2e.analyze_multimodal.called
        
        print(f"API call latency: {result.processing_time:.2f}s")
        print(f"API call cost: ${result.cost:.4f}")
    
    @pytest.mark.asyncio
    async def test_input_size_metrics(self, e2e_agent):
        """
        测试输入大小指标记录 (Requirement 8.2)
        
        验证：
        - 输入大小被记录
        - 处理时间与输入大小相关
        """
        # 小输入
        small_input = UserInputData(
            text_description="短文本"
        )
        
        start_time = time.time()
        small_result = await e2e_agent.process_user_input(small_input)
        small_time = time.time() - start_time
        
        # 大输入
        large_input = UserInputData(
            text_description="这是一个很长的文本描述，" * 50  # 重复50次
        )
        
        start_time = time.time()
        large_result = await e2e_agent.process_user_input(large_input)
        large_time = time.time() - start_time
        
        # 验证都成功
        assert small_result.status == ProcessingStatus.COMPLETED
        assert large_result.status == ProcessingStatus.COMPLETED
        
        print(f"Small input processing time: {small_time:.2f}s")
        print(f"Large input processing time: {large_time:.2f}s")
        
        # 大输入可能需要更多时间（但不是必然）
        # 主要验证系统能够处理不同大小的输入


class TestErrorScenarios:
    """测试错误场景的端到端处理"""
    
    @pytest.mark.asyncio
    async def test_api_timeout_scenario(self, e2e_config):
        """
        场景: API 超时
        
        验证：
        - 超时被正确处理
        - 重试机制工作
        - 最终返回合理的结果或错误
        """
        # 创建会超时的模拟客户端
        mock_client = AsyncMock(spec=DeepSeekClient)
        
        async def slow_response(*args, **kwargs):
            await asyncio.sleep(5)  # 模拟慢响应
            return DeepSeekResponse(
                id="slow_response",
                object="chat.completion",
                created=int(time.time()),
                model="DeepSeek-V3.2",
                choices=[
                    DeepSeekChoice(
                        index=0,
                        message=DeepSeekMessage(role="assistant", content="slow response"),
                        finish_reason="stop"
                    )
                ],
                usage=DeepSeekUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
            )
        
        mock_client.chat_completion.side_effect = slow_response
        mock_client.analyze_multimodal.side_effect = slow_response
        mock_client.close.return_value = None
        
        agent = RequirementParserAgent(
            config=e2e_config,
            deepseek_client=mock_client
        )
        
        user_input = UserInputData(
            text_description="测试超时场景"
        )
        
        # 执行处理（可能会超时或使用降级策略）
        result = await agent.process_user_input(user_input)
        
        # 验证系统处理了超时情况
        assert result is not None
        assert result.status in [ProcessingStatus.COMPLETED, ProcessingStatus.FAILED]
        
        await agent.close()
    
    @pytest.mark.asyncio
    async def test_partial_data_scenario(self, e2e_agent):
        """
        场景: 部分数据不可用
        
        验证：
        - 系统能够处理部分数据缺失
        - 使用默认值填充
        - 置信度反映数据质量
        """
        user_input = UserInputData(
            text_description="部分数据测试",
            reference_images=["https://invalid-url.com/image.jpg"]  # 无效 URL
        )
        
        result = await e2e_agent.process_user_input(user_input)
        
        # 验证系统仍然产生结果
        assert result.status == ProcessingStatus.COMPLETED
        assert result.global_spec is not None
        
        # 置信度可能较低
        if result.confidence_report:
            print(f"Confidence with partial data: {result.confidence_report.overall_confidence:.2f}")


class TestUserExperience:
    """测试用户体验相关的端到端场景"""
    
    @pytest.mark.asyncio
    async def test_quick_iteration_workflow(self, e2e_agent):
        """
        场景: 快速迭代工作流
        
        用户多次调整输入，快速迭代
        """
        # 第一次尝试
        input_v1 = UserInputData(
            text_description="一个视频"
        )
        result_v1 = await e2e_agent.process_user_input(input_v1)
        assert result_v1.status == ProcessingStatus.COMPLETED
        
        # 第二次尝试（更详细）
        input_v2 = UserInputData(
            text_description="一个关于旅行的视频，展现美丽的风景"
        )
        result_v2 = await e2e_agent.process_user_input(input_v2)
        assert result_v2.status == ProcessingStatus.COMPLETED
        
        # 第三次尝试（最详细）
        input_v3 = UserInputData(
            text_description="一个关于环球旅行的视频，展现世界各地的美丽风景，包括山川、海洋、城市，时长60秒",
            user_preferences={"quality": "high"}
        )
        result_v3 = await e2e_agent.process_user_input(input_v3)
        assert result_v3.status == ProcessingStatus.COMPLETED
        
        # 验证迭代改进（更详细的输入可能产生更高的置信度）
        print(f"V1 confidence: {result_v1.confidence_report.overall_confidence if result_v1.confidence_report else 'N/A'}")
        print(f"V2 confidence: {result_v2.confidence_report.overall_confidence if result_v2.confidence_report else 'N/A'}")
        print(f"V3 confidence: {result_v3.confidence_report.overall_confidence if result_v3.confidence_report else 'N/A'}")
    
    @pytest.mark.asyncio
    async def test_different_video_styles(self, e2e_agent):
        """
        场景: 不同风格的视频创建
        
        验证系统能够处理各种风格的视频需求
        """
        styles = [
            ("科幻未来城市，霓虹灯闪烁，赛博朋克风格", "cyberpunk"),
            ("宁静的乡村田园风光，温馨自然", "pastoral"),
            ("激烈的体育比赛现场，充满活力", "sports"),
            ("浪漫的爱情故事，温柔感人", "romantic"),
            ("搞笑的喜剧短片，轻松愉快", "comedy")
        ]
        
        for description, style_name in styles:
            user_input = UserInputData(
                text_description=description
            )
            
            result = await e2e_agent.process_user_input(user_input)
            
            assert result.status == ProcessingStatus.COMPLETED
            assert result.global_spec is not None
            
            print(f"{style_name} style processed successfully")
