"""
预算检查器

负责任务执行前的预算检查和成本预测。
"""

import logging
from typing import Dict, Any

from ..blackboard.blackboard import SharedBlackboard


logger = logging.getLogger(__name__)


class BudgetChecker:
    """
    预算检查器
    
    Features:
    - 实时预算检查
    - 成本预测
    - 预算预警
    """
    
    def __init__(self, blackboard: SharedBlackboard):
        """
        初始化预算检查器
        
        Args:
            blackboard: Shared Blackboard 实例
        """
        self.blackboard = blackboard
    
    def check_budget(self, project_id: str, estimated_cost: float) -> bool:
        """
        检查预算是否充足
        
        Args:
            project_id: 项目 ID
            estimated_cost: 预估成本
            
        Returns:
            bool: 预算是否充足
        """
        try:
            budget = self.blackboard.get_budget(project_id)
            
            # 检查剩余预算
            remaining = budget['total'] - budget['used']
            
            if estimated_cost > remaining:
                logger.warning(
                    f"Insufficient budget for project {project_id}: "
                    f"need ${estimated_cost:.2f}, have ${remaining:.2f}"
                )
                return False
            
            # 预测最终成本
            predicted_total = self.predict_total_cost(project_id)
            
            # 如果预测超支 10%，触发预警
            if predicted_total > budget['total'] * 1.1:
                self.trigger_warning(
                    project_id,
                    f"Predicted cost ${predicted_total:.2f} exceeds budget ${budget['total']:.2f}"
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check budget: {e}")
            return False
    
    def predict_total_cost(self, project_id: str) -> float:
        """
        预测项目最终成本
        
        Args:
            project_id: 项目 ID
            
        Returns:
            float: 预测的总成本
        """
        try:
            budget = self.blackboard.get_budget(project_id)
            project = self.blackboard.get_project(project_id)
            
            # 获取已用成本
            used_cost = budget['used']
            
            # 获取项目进度
            shots = project.get('shots', {})
            total_shots = len(shots)
            completed_shots = sum(1 for shot in shots.values() if shot.get('status') == 'COMPLETED')
            
            if completed_shots == 0:
                # 如果还没有完成的 shot，使用保守估算
                return budget['total']
            
            # 基于已完成 shot 的平均成本预测
            progress = completed_shots / total_shots if total_shots > 0 else 0
            
            if progress > 0:
                predicted = used_cost / progress
            else:
                predicted = budget['total']
            
            logger.debug(f"Predicted total cost for {project_id}: ${predicted:.2f}")
            return predicted
            
        except Exception as e:
            logger.error(f"Failed to predict cost: {e}")
            return 0.0
    
    def get_budget_status(self, project_id: str) -> Dict[str, Any]:
        """
        获取预算状态
        
        Args:
            project_id: 项目 ID
            
        Returns:
            Dict: 预算状态信息
        """
        try:
            budget = self.blackboard.get_budget(project_id)
            predicted = self.predict_total_cost(project_id)
            
            return {
                "total": budget['total'],
                "used": budget['used'],
                "remaining": budget['total'] - budget['used'],
                "usage_percent": (budget['used'] / budget['total'] * 100) if budget['total'] > 0 else 0,
                "predicted_total": predicted,
                "predicted_overrun": max(0, predicted - budget['total']),
                "status": self._get_status_label(budget, predicted)
            }
            
        except Exception as e:
            logger.error(f"Failed to get budget status: {e}")
            return {}
    
    def _get_status_label(self, budget: Dict[str, Any], predicted: float) -> str:
        """获取预算状态标签"""
        usage_percent = (budget['used'] / budget['total'] * 100) if budget['total'] > 0 else 0
        
        if predicted > budget['total'] * 1.1:
            return "CRITICAL"  # 预测超支 10%
        elif usage_percent > 90:
            return "WARNING"   # 已用超过 90%
        elif usage_percent > 70:
            return "CAUTION"   # 已用超过 70%
        else:
            return "HEALTHY"
    
    def trigger_warning(self, project_id: str, reason: str) -> None:
        """
        触发预算预警
        
        Args:
            project_id: 项目 ID
            reason: 预警原因
        """
        logger.warning(f"Budget warning for {project_id}: {reason}")
        
        # TODO: 发布预警事件
        # event_bus.publish(Event(
        #     type=EventType.COST_OVERRUN_WARNING,
        #     project_id=project_id,
        #     payload={"reason": reason}
        # ))
