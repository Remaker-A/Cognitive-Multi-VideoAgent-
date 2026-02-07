"""
模板库管理器

负责加载、管理和选择 Prompt 模板。
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


logger = logging.getLogger(__name__)


@dataclass
class Template:
    """Prompt 模板数据类"""
    template_id: str
    name: str
    category: str
    description: str
    base_prompt: str
    variables: List[Dict]
    variations: List[str]
    quality_modifiers: Dict[str, str]
    negative_prompt: str
    default_params: Dict
    tags: List[str]
    priority: int
    
    # 可选字段
    camera_settings: Dict = field(default_factory=dict)
    lighting_presets: Dict = field(default_factory=dict)
    usage_notes: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Template':
        """从字典创建模板"""
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            category=data["category"],
            description=data["description"],
            base_prompt=data["base_prompt"],
            variables=data["variables"],
            variations=data["variations"],
            quality_modifiers=data["quality_modifiers"],
            negative_prompt=data["negative_prompt"],
            default_params=data["default_params"],
            tags=data["tags"],
            priority=data["priority"],
            camera_settings=data.get("camera_settings", {}),
            lighting_presets=data.get("lighting_presets", {}),
            usage_notes=data.get("usage_notes", "")
        )


class TemplateLibrary:
    """
    模板库管理器
    
    负责加载和管理所有 Prompt 模板。
    """
    
    def __init__(self, templates_dir: str = None):
        """
        初始化模板库
        
        Args:
            templates_dir: 模板目录路径
        """
        if templates_dir is None:
            # 默认使用当前目录下的 templates
            templates_dir = Path(__file__).parent / "templates"
        
        self.templates_dir = Path(templates_dir)
        self.templates: Dict[str, Template] = {}
        self.load_templates()
    
    def load_templates(self) -> None:
        """加载所有模板文件"""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return
        
        template_files = list(self.templates_dir.glob("*.json"))
        
        for file_path in template_files:
            try:
                template = self.load_template(file_path)
                self.templates[template.template_id] = template
                logger.debug(f"Loaded template: {template.template_id}")
            except Exception as e:
                logger.error(f"Failed to load template {file_path}: {e}")
        
        logger.info(f"Loaded {len(self.templates)} templates from {self.templates_dir}")
    
    def load_template(self, file_path: Path) -> Template:
        """
        加载单个模板文件
        
        Args:
            file_path: 模板文件路径
            
        Returns:
            Template: 模板对象
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Template.from_dict(data)
    
    def get_template(self, template_id: str) -> Optional[Template]:
        """
        获取模板
        
        Args:
            template_id: 模板 ID
            
        Returns:
            Optional[Template]: 模板对象
        """
        return self.templates.get(template_id)
    
    def select_template(self, shot_type: str, mood_tags: List[str] = None) -> Optional[Template]:
        """
        基于 shot_type 和 mood_tags 选择最佳模板
        
        Args:
            shot_type: 镜头类型
            mood_tags: 情绪标签列表
            
        Returns:
            Optional[Template]: 最佳匹配的模板
        """
        if mood_tags is None:
            mood_tags = []
        
        candidates = []
        
        for template in self.templates.values():
            score = self.score_template(template, shot_type, mood_tags)
            candidates.append((template, score))
        
        if not candidates:
            logger.warning("No templates available")
            return None
        
        # 按分数排序
        candidates.sort(key=lambda x: x[1], reverse=True)
        
        best_template = candidates[0][0]
        logger.info(f"Selected template: {best_template.template_id} (score: {candidates[0][1]})")
        
        return best_template
    
    def score_template(self, template: Template, shot_type: str, mood_tags: List[str]) -> int:
        """
        计算模板匹配分数
        
        Args:
            template: 模板对象
            shot_type: 镜头类型
            mood_tags: 情绪标签
            
        Returns:
            int: 匹配分数
        """
        score = 0
        
        # 检查 tags 匹配
        for tag in mood_tags:
            if tag.lower() in [t.lower() for t in template.tags]:
                score += 10
        
        # 检查 category 匹配
        if shot_type and shot_type.upper() in template.category.upper():
            score += 50
        
        # 检查 shot_type 在模板名称中
        if shot_type and shot_type.lower() in template.name.lower():
            score += 30
        
        # 优先级加成
        score += template.priority
        
        return score
    
    def list_templates(self, category: str = None) -> List[Template]:
        """
        列出模板
        
        Args:
            category: 可选的类别过滤
            
        Returns:
            List[Template]: 模板列表
        """
        templates = list(self.templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category.upper()]
        
        return templates
