"""
Negative Prompt 管理器

负责生成和管理 Negative Prompt。
"""

import logging
from typing import List, Dict, Any


logger = logging.getLogger(__name__)


class NegativeManager:
    """
    Negative Prompt 管理器
    
    生成和管理 negative prompts。
    """
    
    def __init__(self):
        """初始化管理器"""
        # 全局 negative prompts
        self.global_negatives = [
            "blurry",
            "distorted",
            "low quality",
            "deformed",
            "ugly",
            "bad anatomy",
            "poorly drawn",
            "bad proportions"
        ]
        
        # 类型特定的 negative prompts
        self.type_specific_negatives = {
            "character": [
                "multiple faces",
                "extra fingers",
                "fused fingers",
                "extra limbs",
                "missing limbs",
                "disfigured face"
            ],
            "action": [
                "static",
                "frozen pose",
                "stiff movement",
                "unnatural physics",
                "choppy animation"
            ],
            "environment": [
                "cluttered",
                "messy",
                "inconsistent perspective",
                "unrealistic lighting"
            ]
        }
    
    def build_negative_prompt(
        self,
        template,
        shot_spec: Dict[str, Any],
        quality_tier: str
    ) -> str:
        """
        构建 negative prompt
        
        Args:
            template: 模板对象
            shot_spec: Shot 规格
            quality_tier: 质量档位
            
        Returns:
            str: Negative prompt
        """
        negatives = []
        
        # 1. 添加模板 negative
        if template and template.negative_prompt:
            negatives.append(template.negative_prompt)
        
        # 2. 添加全局 negative
        negatives.extend(self.global_negatives)
        
        # 3. 根据质量档位调整
        if quality_tier == "DRAFT":
            # 草稿模式，减少 negative
            negatives = negatives[:8]
        elif quality_tier == "PREMIUM":
            # 顶级模式，添加更多 negative
            negatives.extend([
                "watermark",
                "text overlay",
                "signature",
                "username",
                "artifacts",
                "noise"
            ])
        
        # 4. 根据 shot 类型添加特定 negative
        shot_type = shot_spec.get("type", "").lower()
        
        if "character" in shot_type or "portrait" in shot_type:
            negatives.extend(self.type_specific_negatives["character"])
        
        if "action" in shot_type:
            negatives.extend(self.type_specific_negatives["action"])
        
        if "environment" in shot_type or "landscape" in shot_type:
            negatives.extend(self.type_specific_negatives["environment"])
        
        # 去重
        negatives = list(dict.fromkeys(negatives))
        
        # 组合
        negative_prompt = ", ".join(negatives)
        
        logger.debug(f"Built negative prompt with {len(negatives)} items")
        
        return negative_prompt
    
    def add_custom_negatives(self, negatives: List[str]) -> None:
        """
        添加自定义 negative prompts
        
        Args:
            negatives: 自定义 negative 列表
        """
        self.global_negatives.extend(negatives)
        # 去重
        self.global_negatives = list(dict.fromkeys(self.global_negatives))
