"""
RequirementParser Agent 主类

作为 LivingAgentPipeline 系统的入口层 Agent，负责解析用户多模态输入并生成标准化的 GlobalSpec。
"""

import asyncio
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .models import (
    UserInputData,
    ProcessedInput,
    GlobalSpec,
    ConfidenceReport,
    ProcessingResult,
    ProcessingStatus,
    Money,
    EventType
)
from .config import RequirementParserConfig, config
from .input_manager import InputManager
from .preprocessor import Preprocessor
from .multimodal_analyzer import MultimodalAnalyzer
from .global_spec_generator import GlobalSpecGenerator
from .confidence_evaluator import ConfidenceEvaluator
from .event_manager import EventManager
from .deepseek_client import DeepSeekClient
from .exceptions import (
    RequirementParserError,
    DeepSeekAPIError,
    APITimeoutError,
    APIRateLimitError,
    NetworkError,
    MaxRetriesExceededError,
    InputValidationError,
    InsufficientInputError,
    HumanInterventionRequired
)
from .logger import setup_logger
from .metrics_collector import MetricsCollector, global_metrics_collector

logger = setup_logger(__name__)


class RequirementParserAgent:
    """
    RequirementParser Agent 主类
    
    职责：
    - 作为事件订阅者处理用户输入事件
    - 协调所有组件完成需求解析流程
    - 实现三层错误恢复策略
    - 发布处理结果事件
    
    Requirements: 1.1, 2.1, 3.1, 4.1, 5.1, 6.1, 6.2, 6.3, 6.4, 6.5
    """
    
    def __init__(
        self,
        config: Optional[RequirementParserConfig] = None,
        deepseek_client: Optional[DeepSeekClient] = None,
        metrics_collector: Optional[MetricsCollector] = None
    ):
        """
        初始化 RequirementParser Agent
        
        Args:
            config: 配置对象，如果为None则使用默认配置
            deepseek_client: DeepSeek API 客户端，如果为None则创建新实例
            metrics_collector: 指标收集器，如果为None则使用全局实例
        """
        # 配置
        from .config import config as default_config
        self.config = config or default_config
        
        # 指标收集器
        self.metrics_collector = metrics_collector or global_metrics_collector
        
        # 初始化组件
        self.input_manager = InputManager()
        self.preprocessor = Preprocessor()
        
        # DeepSeek 客户端
        self.deepseek_client = deepseek_client or DeepSeekClient(
            api_key=self.config.deepseek_api_key,
            base_url=self.config.deepseek_api_endpoint,
            model_name=self.config.deepseek_model_name,
            timeout=self.config.timeout_seconds,
            max_retries=self.config.max_retries
        )
        
        # 多模态分析器
        self.multimodal_analyzer = MultimodalAnalyzer(self.deepseek_client)
        
        # GlobalSpec 生成器
        self.global_spec_generator = GlobalSpecGenerator(
            default_config=self.config.get_default_global_spec_config()
        )
        
        # 置信度评估器
        self.confidence_evaluator = ConfidenceEvaluator(self.config)
        
        # 事件管理器
        self.event_manager = EventManager(agent_name=self.config.agent_name)
        
        logger.info(
            f"{self.config.agent_name} initialized",
            extra={
                "config": {
                    "confidence_threshold": self.config.confidence_threshold,
                    "max_retries": self.config.max_retries,
                    "timeout_seconds": self.config.timeout_seconds
                }
            }
        )
    
    async def process_user_input(
        self,
        user_input: UserInputData,
        causation_id: Optional[str] = None
    ) -> ProcessingResult:
        """
        处理用户输入的主入口方法
        
        完整的处理流程：
        1. 接收和验证用户输入
        2. 预处理多模态数据
        3. 调用 DeepSeek API 进行分析
        4. 生成 GlobalSpec
        5. 评估置信度
        6. 发布事件和写入 Blackboard
        
        Args:
            user_input: 用户输入数据
            causation_id: 触发此处理的事件 ID（可选）
        
        Returns:
            ProcessingResult: 处理结果
        
        Requirements: 1.1, 2.1, 3.1, 4.1, 5.1
        """
        start_time = time.time()
        project_id = self.event_manager.generate_project_id()
        
        logger.info(
            f"Starting user input processing",
            extra={
                "project_id": project_id,
                "causation_id": causation_id,
                "has_text": bool(user_input.text_description),
                "images_count": len(user_input.reference_images),
                "videos_count": len(user_input.reference_videos),
                "audio_count": len(user_input.reference_audio)
            }
        )
        
        try:
            # Level 1: 尝试完整处理
            result = await self._full_processing(
                user_input=user_input,
                project_id=project_id,
                causation_id=causation_id,
                start_time=start_time
            )
            
            logger.info(
                f"User input processing completed successfully",
                extra={
                    "project_id": project_id,
                    "processing_time": time.time() - start_time,
                    "confidence": result.confidence_report.overall_confidence if result.confidence_report else None
                }
            )
            
            return result
        
        except Exception as e:
            logger.error(
                f"Full processing failed: {e}",
                extra={"project_id": project_id, "error_type": type(e).__name__}
            )
            
            # Level 2: 尝试降级处理
            try:
                result = await self._fallback_processing(
                    user_input=user_input,
                    project_id=project_id,
                    causation_id=causation_id,
                    start_time=start_time,
                    original_error=e
                )
                
                logger.warning(
                    f"Fallback processing succeeded",
                    extra={
                        "project_id": project_id,
                        "processing_time": time.time() - start_time
                    }
                )
                
                return result
            
            except Exception as fallback_error:
                logger.error(
                    f"Fallback processing also failed: {fallback_error}",
                    extra={"project_id": project_id, "error_type": type(fallback_error).__name__}
                )
                
                # Level 3: 升级到人工介入
                return await self._escalate_to_human(
                    user_input=user_input,
                    project_id=project_id,
                    causation_id=causation_id,
                    start_time=start_time,
                    error=fallback_error,
                    original_error=e
                )
    
    async def _full_processing(
        self,
        user_input: UserInputData,
        project_id: str,
        causation_id: Optional[str],
        start_time: float
    ) -> ProcessingResult:
        """
        完整处理流程（Level 1）
        
        Args:
            user_input: 用户输入
            project_id: 项目 ID
            causation_id: 因果关系 ID
            start_time: 开始时间
        
        Returns:
            ProcessingResult: 处理结果
        
        Raises:
            RequirementParserError: 处理失败
        """
        logger.debug(f"Starting full processing for project {project_id}")
        
        # 计算输入大小
        text_length = len(user_input.text_description) if user_input.text_description else 0
        input_size_bytes = text_length  # 简化计算，实际应包括文件大小
        
        try:
            # 1. 接收和验证用户输入 (Requirement 1.1)
            processed_input = await self.input_manager.receive_user_input(user_input)
            
            # 2. 预处理多模态数据 (Requirement 1.1, 1.2, 1.3, 1.4)
            processed_text = await self.preprocessor.process_text(processed_input.text)
            processed_images = await self.preprocessor.process_images(processed_input.images)
            processed_videos = await self.preprocessor.process_videos(processed_input.videos)
            processed_audio = await self.preprocessor.process_audio(processed_input.audio)
            
            # 3. 多模态分析 (Requirement 3.1)
            analysis = await self.multimodal_analyzer.analyze_all(
                text=processed_text,
                images=processed_images,
                videos=processed_videos,
                audio=processed_audio
            )
            
            # 4. 生成 GlobalSpec (Requirement 2.1)
            global_spec = await self.global_spec_generator.generate_spec(
                analysis=analysis,
                user_input=user_input
            )
            
            # 5. 评估置信度 (Requirement 4.1)
            confidence_report = await self.confidence_evaluator.evaluate_confidence(
                global_spec=global_spec,
                analysis=analysis,
                user_input=user_input
            )
            
            # 记录置信度指标 (Requirement 8.3)
            self.metrics_collector.record_confidence(
                project_id=project_id,
                overall_confidence=confidence_report.overall_confidence,
                confidence_level=confidence_report.confidence_level,
                component_scores=confidence_report.component_scores,
                recommendation=confidence_report.recommendation
            )
            
            # 6. 根据置信度决定后续行动 (Requirement 4.2)
            if confidence_report.recommendation == "human_review":
                # 置信度极低，需要人工审核
                raise HumanInterventionRequired(
                    "Confidence too low, human review required",
                    context={
                        "confidence": confidence_report.overall_confidence,
                        "low_confidence_areas": confidence_report.low_confidence_areas
                    }
                )
            
            elif confidence_report.recommendation == "clarify":
                # 需要澄清，发布澄清请求事件
                await self.event_manager.publish_human_clarification_required(
                    project_id=project_id,
                    confidence_report=confidence_report,
                    causation_id=causation_id
                )
            
            # 7. 写入 Blackboard (Requirement 5.5)
            await self.event_manager.write_global_spec_to_blackboard(
                project_id=project_id,
                global_spec=global_spec
            )
            
            # 8. 计算成本和延迟
            processing_time = time.time() - start_time
            latency_ms = int(processing_time * 1000)
            
            # 简单的成本估算（基于 token 使用）
            # 实际应用中应该从 DeepSeek API 响应中获取
            cost = Money(amount=0.01, currency="USD")
            
            # 记录处理指标 (Requirement 8.2)
            self.metrics_collector.record_processing(
                project_id=project_id,
                processing_stage="full",
                processing_time_ms=latency_ms,
                input_size_bytes=input_size_bytes,
                text_length=text_length,
                images_count=len(user_input.reference_images),
                videos_count=len(user_input.reference_videos),
                audio_count=len(user_input.reference_audio),
                success=True
            )
            
            # 9. 发布 PROJECT_CREATED 事件 (Requirement 5.1)
            await self.event_manager.publish_project_created(
                project_id=project_id,
                global_spec=global_spec,
                confidence_report=confidence_report,
                causation_id=causation_id,
                cost=cost,
                latency_ms=latency_ms
            )
            
            # 10. 返回处理结果
            return ProcessingResult(
                status=ProcessingStatus.COMPLETED,
                global_spec=global_spec,
                confidence_report=confidence_report,
                processing_time=processing_time,
                cost=cost.amount,
                events_published=self.event_manager.get_event_count()
            )
        
        except Exception as e:
            # 记录错误指标 (Requirement 8.4)
            self.metrics_collector.record_error(
                project_id=project_id,
                error_type=type(e).__name__,
                error_message=str(e),
                recovery_strategy=None,
                recovery_success=False
            )
            
            # 记录失败的处理指标
            processing_time = time.time() - start_time
            self.metrics_collector.record_processing(
                project_id=project_id,
                processing_stage="full",
                processing_time_ms=int(processing_time * 1000),
                input_size_bytes=input_size_bytes,
                text_length=text_length,
                images_count=len(user_input.reference_images),
                videos_count=len(user_input.reference_videos),
                audio_count=len(user_input.reference_audio),
                success=False
            )
            
            raise
    
    async def _fallback_processing(
        self,
        user_input: UserInputData,
        project_id: str,
        causation_id: Optional[str],
        start_time: float,
        original_error: Exception
    ) -> ProcessingResult:
        """
        降级处理流程（Level 2）
        
        当完整处理失败时，尝试以下降级策略：
        1. 仅处理文本输入
        2. 使用默认模板
        
        Args:
            user_input: 用户输入
            project_id: 项目 ID
            causation_id: 因果关系 ID
            start_time: 开始时间
            original_error: 原始错误
        
        Returns:
            ProcessingResult: 处理结果
        
        Raises:
            RequirementParserError: 降级处理也失败
        
        Requirements: 6.3
        """
        logger.warning(
            f"Attempting fallback processing for project {project_id}",
            extra={"original_error": str(original_error)}
        )
        
        # 记录错误和恢复尝试 (Requirement 8.4)
        self.metrics_collector.record_error(
            project_id=project_id,
            error_type=type(original_error).__name__,
            error_message=str(original_error),
            recovery_strategy="fallback",
            recovery_success=False  # 先标记为失败，成功后更新
        )
        
        # 策略1: 仅处理文本输入
        if user_input.text_description and len(user_input.text_description.strip()) > 0:
            try:
                logger.info("Fallback strategy 1: Text-only processing")
                result = await self._text_only_processing(
                    user_input=user_input,
                    project_id=project_id,
                    causation_id=causation_id,
                    start_time=start_time
                )
                
                # 更新恢复成功状态
                if self.metrics_collector.error_metrics:
                    self.metrics_collector.error_metrics[-1].recovery_success = True
                
                return result
            except Exception as e:
                logger.warning(f"Text-only processing failed: {e}")
        
        # 策略2: 使用默认模板
        logger.info("Fallback strategy 2: Template-based processing")
        result = await self._template_based_processing(
            user_input=user_input,
            project_id=project_id,
            causation_id=causation_id,
            start_time=start_time
        )
        
        # 更新恢复成功状态
        if self.metrics_collector.error_metrics:
            self.metrics_collector.error_metrics[-1].recovery_success = True
        
        return result
    
    async def _text_only_processing(
        self,
        user_input: UserInputData,
        project_id: str,
        causation_id: Optional[str],
        start_time: float
    ) -> ProcessingResult:
        """
        仅处理文本输入的降级策略
        
        Args:
            user_input: 用户输入
            project_id: 项目 ID
            causation_id: 因果关系 ID
            start_time: 开始时间
        
        Returns:
            ProcessingResult: 处理结果
        """
        # 仅处理文本
        processed_text = await self.preprocessor.process_text(user_input.text_description)
        
        # 仅分析文本
        text_analysis = await self.multimodal_analyzer.analyze_text_intent(processed_text)
        
        # 创建简化的综合分析
        from .models import SynthesizedAnalysis
        analysis = SynthesizedAnalysis(
            text_analysis=text_analysis,
            visual_style=None,
            motion_style=None,
            audio_mood=None,
            overall_theme=text_analysis.main_theme if text_analysis else "视频项目",
            confidence_scores={"text": 0.7}
        )
        
        # 生成 GlobalSpec
        global_spec = await self.global_spec_generator.generate_spec(
            analysis=analysis,
            user_input=user_input
        )
        
        # 评估置信度（会较低）
        confidence_report = await self.confidence_evaluator.evaluate_confidence(
            global_spec=global_spec,
            analysis=analysis,
            user_input=user_input
        )
        
        # 写入 Blackboard
        await self.event_manager.write_global_spec_to_blackboard(
            project_id=project_id,
            global_spec=global_spec
        )
        
        # 发布事件
        processing_time = time.time() - start_time
        latency_ms = int(processing_time * 1000)
        cost = Money(amount=0.005, currency="USD")  # 降级处理成本更低
        
        await self.event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms,
            metadata={"fallback_strategy": "text_only"}
        )
        
        return ProcessingResult(
            status=ProcessingStatus.COMPLETED,
            global_spec=global_spec,
            confidence_report=confidence_report,
            processing_time=processing_time,
            cost=cost.amount,
            events_published=self.event_manager.get_event_count()
        )
    
    async def _template_based_processing(
        self,
        user_input: UserInputData,
        project_id: str,
        causation_id: Optional[str],
        start_time: float
    ) -> ProcessingResult:
        """
        基于默认模板的降级策略
        
        Args:
            user_input: 用户输入
            project_id: 项目 ID
            causation_id: 因果关系 ID
            start_time: 开始时间
        
        Returns:
            ProcessingResult: 处理结果
        """
        from .models import StyleConfig
        
        # 使用默认模板创建 GlobalSpec
        default_config = self.config.get_default_global_spec_config()
        global_spec = GlobalSpec(
            title=user_input.text_description[:50] if user_input.text_description else "视频项目",
            duration=default_config.get("duration", 30),
            aspect_ratio=default_config.get("aspect_ratio", "9:16"),
            quality_tier=default_config.get("quality_tier", "balanced"),
            resolution=default_config.get("resolution", "1080x1920"),
            fps=default_config.get("fps", 30),
            style=StyleConfig(
                tone="natural",
                palette=["#FFFFFF", "#000000"],
                visual_dna_version=1
            ),
            characters=[],
            mood="neutral",
            user_options=user_input.user_preferences
        )
        
        # 创建低置信度报告
        from .models import ConfidenceReport, ConfidenceLevel
        confidence_report = ConfidenceReport(
            overall_confidence=0.3,
            confidence_level=ConfidenceLevel.LOW,
            component_scores={
                "text_clarity": 0.3,
                "style_consistency": 0.3,
                "completeness": 0.3,
                "user_input_quality": 0.3
            },
            low_confidence_areas=["text_clarity", "style_consistency", "completeness"],
            clarification_requests=[],
            recommendation="clarify"
        )
        
        # 写入 Blackboard
        await self.event_manager.write_global_spec_to_blackboard(
            project_id=project_id,
            global_spec=global_spec
        )
        
        # 发布澄清请求事件
        await self.event_manager.publish_human_clarification_required(
            project_id=project_id,
            confidence_report=confidence_report,
            causation_id=causation_id,
            metadata={"fallback_strategy": "template_based"}
        )
        
        # 发布项目创建事件
        processing_time = time.time() - start_time
        latency_ms = int(processing_time * 1000)
        cost = Money(amount=0.001, currency="USD")  # 模板处理成本最低
        
        await self.event_manager.publish_project_created(
            project_id=project_id,
            global_spec=global_spec,
            confidence_report=confidence_report,
            causation_id=causation_id,
            cost=cost,
            latency_ms=latency_ms,
            metadata={"fallback_strategy": "template_based"}
        )
        
        return ProcessingResult(
            status=ProcessingStatus.COMPLETED,
            global_spec=global_spec,
            confidence_report=confidence_report,
            processing_time=processing_time,
            cost=cost.amount,
            events_published=self.event_manager.get_event_count()
        )
    
    async def _escalate_to_human(
        self,
        user_input: UserInputData,
        project_id: str,
        causation_id: Optional[str],
        start_time: float,
        error: Exception,
        original_error: Exception
    ) -> ProcessingResult:
        """
        升级到人工介入（Level 3）
        
        当所有自动处理策略都失败时，触发人工介入流程
        
        Args:
            user_input: 用户输入
            project_id: 项目 ID
            causation_id: 因果关系 ID
            start_time: 开始时间
            error: 降级处理错误
            original_error: 原始错误
        
        Returns:
            ProcessingResult: 处理结果（失败状态）
        
        Requirements: 6.5
        """
        logger.error(
            f"Escalating to human intervention for project {project_id}",
            extra={
                "original_error": str(original_error),
                "fallback_error": str(error)
            }
        )
        
        # 构建错误上下文
        error_context = {
            "original_error": {
                "type": type(original_error).__name__,
                "message": str(original_error)
            },
            "fallback_error": {
                "type": type(error).__name__,
                "message": str(error)
            },
            "user_input_summary": {
                "has_text": bool(user_input.text_description),
                "text_length": len(user_input.text_description) if user_input.text_description else 0,
                "images_count": len(user_input.reference_images),
                "videos_count": len(user_input.reference_videos),
                "audio_count": len(user_input.reference_audio)
            },
            "suggested_actions": [
                "Review user input for clarity and completeness",
                "Check if API credentials are valid",
                "Verify network connectivity",
                "Consider manual GlobalSpec creation"
            ]
        }
        
        # 发布错误事件 (Requirement 5.4)
        await self.event_manager.publish_error_occurred(
            project_id=project_id,
            error=error,
            error_context=error_context,
            causation_id=causation_id,
            metadata={"escalation_level": "human_intervention"}
        )
        
        # 发布人工介入事件
        from .models import Event, EventType
        human_gate_event = Event(
            event_id=self.event_manager.generate_event_id(),
            project_id=project_id,
            event_type=EventType.HUMAN_GATE_TRIGGERED,
            actor=self.config.agent_name,
            payload={
                "error_context": error_context,
                "priority": "high"
            },
            causation_id=causation_id,
            timestamp=datetime.now().isoformat()
        )
        
        self.event_manager._published_events.append(human_gate_event)
        
        logger.info(
            f"Human intervention triggered for project {project_id}",
            extra={"event_id": human_gate_event.event_id}
        )
        
        # 返回失败结果
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            status=ProcessingStatus.FAILED,
            global_spec=None,
            confidence_report=None,
            error_message=f"Processing failed: {str(error)}. Human intervention required.",
            processing_time=processing_time,
            cost=0.0,
            events_published=self.event_manager.get_event_count()
        )
    
    async def close(self) -> None:
        """
        关闭 Agent 并清理资源
        """
        logger.info(f"Closing {self.config.agent_name}")
        
        # 关闭 DeepSeek 客户端
        if self.deepseek_client:
            await self.deepseek_client.close()
        
        logger.info(f"{self.config.agent_name} closed")
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()
