"""
自动修复策略

实现三层错误恢复机制。
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum


logger = logging.getLogger(__name__)


class FixLevel(int, Enum):
    """修复级别"""
    PROMPT_TUNING = 1
    MODEL_SWITCH = 2
    HUMAN_GATE = 3


class AutoFixStrategy:
    """
    自动修复策略
    
    实现三层错误恢复：
    1. Prompt Tuning（轻量级）
    2. Model Switch / Quality Downgrade（中等）
    3. HumanGate（重量级）
    """
    
    # 质量分数阈值
    LEVEL_1_THRESHOLD = 0.60  # >= 0.60: Prompt Tuning
    LEVEL_2_THRESHOLD = 0.40  # >= 0.40: Model Switch
    # < 0.40: HumanGate
    
    def __init__(self, blackboard, event_bus):
        """
        初始化修复策略
        
        Args:
            blackboard: Shared Blackboard 实例
            event_bus: Event Bus 实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        
        logger.info("AutoFixStrategy initialized")
    
    def determine_fix_level(
        self,
        qa_results: Dict[str, Any]
    ) -> FixLevel:
        """
        确定修复级别
        
        Args:
            qa_results: QA 检测结果
            
        Returns:
            FixLevel: 修复级别
        """
        # 获取总体分数
        overall_score = qa_results.get("overall_score", 0.0)
        
        if overall_score >= self.LEVEL_1_THRESHOLD:
            return FixLevel.PROMPT_TUNING
        elif overall_score >= self.LEVEL_2_THRESHOLD:
            return FixLevel.MODEL_SWITCH
        else:
            return FixLevel.HUMAN_GATE
    
    async def auto_fix(
        self,
        project_id: str,
        qa_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        自动修复入口
        
        Args:
            project_id: 项目 ID
            qa_results: QA 检测结果
            context: 上下文信息
            
        Returns:
            Dict: 修复结果
        """
        logger.info(f"Starting auto-fix for project {project_id}")
        
        # 确定修复级别
        fix_level = self.determine_fix_level(qa_results)
        
        logger.info(f"Fix level determined: Level {fix_level}")
        
        # 应用修复策略
        if fix_level == FixLevel.PROMPT_TUNING:
            return await self.apply_prompt_tuning(project_id, qa_results, context)
        
        elif fix_level == FixLevel.MODEL_SWITCH:
            return await self.apply_model_switch_or_downgrade(project_id, qa_results, context)
        
        elif fix_level == FixLevel.HUMAN_GATE:
            return await self.trigger_human_gate(project_id, qa_results, context)
        
        return {"success": False, "error": "Unknown fix level"}
    
    async def apply_prompt_tuning(
        self,
        project_id: str,
        qa_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 1: Prompt Tuning
        
        Args:
            project_id: 项目 ID
            qa_results: QA 检测结果
            context: 上下文信息
            
        Returns:
            Dict: 修复结果
        """
        logger.info("Applying Level 1: Prompt Tuning")
        
        try:
            shot_id = context.get("shot_id")
            
            # 分析失败原因
            failed_checks = self._get_failed_checks(qa_results)
            
            # 生成 prompt 调整建议
            adjustments = {
                "cfg_scale": None,
                "negative_prompts": [],
                "weight_adjustments": {}
            }
            
            # 根据失败的检测项调整
            if "clip_similarity" in failed_checks:
                adjustments["cfg_scale"] = 8.5  # 增加 CFG
                adjustments["negative_prompts"].append("inconsistent_style")
            
            if "face_identity" in failed_checks:
                adjustments["weight_adjustments"]["character_consistency"] = 1.3
                adjustments["negative_prompts"].append("different_face")
            
            if "palette_consistency" in failed_checks:
                adjustments["negative_prompts"].append("color_shift")
                adjustments["weight_adjustments"]["color_palette"] = 1.2
            
            # 发布修复请求事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.AUTO_FIX_REQUEST,
                actor="ConsistencyGuardian",
                payload={
                    "fix_level": 1,
                    "fix_type": "prompt_tuning",
                    "shot_id": shot_id,
                    "adjustments": adjustments,
                    "qa_results": qa_results
                }
            ))
            
            logger.info("Prompt tuning request published")
            
            return {
                "success": True,
                "fix_level": 1,
                "fix_type": "prompt_tuning",
                "adjustments": adjustments
            }
            
        except Exception as e:
            logger.error(f"Prompt tuning failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def apply_model_switch_or_downgrade(
        self,
        project_id: str,
        qa_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 2: Model Switch 或 Quality Downgrade
        
        Args:
            project_id: 项目 ID
            qa_results: QA 检测结果
            context: 上下文信息
            
        Returns:
            Dict: 修复结果
        """
        logger.info("Applying Level 2: Model Switch / Quality Downgrade")
        
        try:
            shot_id = context.get("shot_id")
            current_model = context.get("model", "sdxl-1.0")
            current_quality = context.get("quality_tier", "STANDARD")
            
            # 决策：切换模型还是降级质量
            strategy = self._decide_level2_strategy(qa_results, context)
            
            if strategy == "model_switch":
                # 切换到备用模型
                alternative_model = self._get_alternative_model(current_model)
                
                fix_action = {
                    "action": "model_switch",
                    "from_model": current_model,
                    "to_model": alternative_model
                }
                
            else:  # quality_downgrade
                # 降低质量档位
                downgraded_quality = self._downgrade_quality(current_quality)
                
                fix_action = {
                    "action": "quality_downgrade",
                    "from_quality": current_quality,
                    "to_quality": downgraded_quality
                }
            
            # 发布修复请求事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.AUTO_FIX_REQUEST,
                actor="ConsistencyGuardian",
                payload={
                    "fix_level": 2,
                    "fix_type": strategy,
                    "shot_id": shot_id,
                    "fix_action": fix_action,
                    "qa_results": qa_results
                }
            ))
            
            logger.info(f"Level 2 fix request published: {strategy}")
            
            return {
                "success": True,
                "fix_level": 2,
                "fix_type": strategy,
                "fix_action": fix_action
            }
            
        except Exception as e:
            logger.error(f"Level 2 fix failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    async def trigger_human_gate(
        self,
        project_id: str,
        qa_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Level 3: HumanGate
        
        Args:
            project_id: 项目 ID
            qa_results: QA 检测结果
            context: 上下文信息
            
        Returns:
            Dict: 修复结果
        """
        logger.warning("Triggering Level 3: HumanGate")
        
        try:
            shot_id = context.get("shot_id")
            
            # 准备人工审核信息
            review_info = {
                "project_id": project_id,
                "shot_id": shot_id,
                "qa_results": qa_results,
                "context": context,
                "reason": "Quality score too low, automatic fix failed",
                "severity": "high"
            }
            
            # 发布 HumanGate 事件
            from src.infrastructure.event_bus import Event, EventType
            
            await self.event_bus.publish(Event(
                project_id=project_id,
                type=EventType.HUMAN_GATE_TRIGGERED,
                actor="ConsistencyGuardian",
                payload={
                    "fix_level": 3,
                    "fix_type": "human_gate",
                    "review_info": review_info
                }
            ))
            
            logger.warning(f"HumanGate triggered for shot {shot_id}")
            
            return {
                "success": True,
                "fix_level": 3,
                "fix_type": "human_gate",
                "status": "awaiting_human_review",
                "review_info": review_info
            }
            
        except Exception as e:
            logger.error(f"HumanGate trigger failed: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def _get_failed_checks(self, qa_results: Dict[str, Any]) -> list:
        """获取失败的检测项"""
        failed = []
        
        checks = qa_results.get("checks", {})
        
        for check_name, check_result in checks.items():
            if not check_result.get("passed", True):
                failed.append(check_name)
        
        return failed
    
    def _decide_level2_strategy(
        self,
        qa_results: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """决定 Level 2 策略：模型切换 vs 质量降级"""
        # 简单策略：如果是模型问题，切换模型；否则降级质量
        failed_checks = self._get_failed_checks(qa_results)
        
        # 如果主要是视觉质量问题，尝试切换模型
        if "clip_similarity" in failed_checks or "face_identity" in failed_checks:
            return "model_switch"
        
        # 否则降级质量
        return "quality_downgrade"
    
    def _get_alternative_model(self, current_model: str) -> str:
        """获取备用模型"""
        # 模型备选方案
        alternatives = {
            "sdxl-1.0": "dalle3",
            "dalle3": "sdxl-1.0",
            "runway": "pika",
            "pika": "runway"
        }
        
        return alternatives.get(current_model, "sdxl-1.0")
    
    def _downgrade_quality(self, current_quality: str) -> str:
        """降级质量档位"""
        quality_levels = ["ULTRA", "HIGH", "STANDARD", "PREVIEW"]
        
        try:
            current_index = quality_levels.index(current_quality)
            
            # 降一级
            if current_index < len(quality_levels) - 1:
                return quality_levels[current_index + 1]
            
            return current_quality  # 已经是最低档
            
        except ValueError:
            return "STANDARD"  # 默认
