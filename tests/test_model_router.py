"""
ModelRouter 单元测试

测试模型选择、成本估算等核心功能。
"""

import pytest

from src.infrastructure.model_router import (
    Model, ModelType, QualityTier,
    ModelRegistry
)


class TestModel:
    """Model 数据模型测试"""
    
    def test_model_creation(self):
        """测试模型创建"""
        model = Model(
            model_id="sdxl",
            name="SDXL",
            type=ModelType.TEXT_TO_IMAGE,
            provider="stability",
            quality_tier=QualityTier.STANDARD,
            cost_per_unit=0.04
        )
        
        assert model.model_id == "sdxl"
        assert model.type == ModelType.TEXT_TO_IMAGE
        assert model.quality_tier == QualityTier.STANDARD
        assert model.cost_per_unit == 0.04
    
    def test_model_serialization(self):
        """测试模型序列化"""
        model = Model(
            model_id="sdxl",
            name="SDXL",
            type=ModelType.TEXT_TO_IMAGE,
            provider="stability",
            quality_tier=QualityTier.STANDARD
        )
        
        # 转换为字典
        model_dict = model.to_dict()
        assert model_dict["model_id"] == "sdxl"
        assert model_dict["type"] == "TEXT_TO_IMAGE"
        
        # 从字典创建
        model2 = Model.from_dict(model_dict)
        assert model2.model_id == model.model_id
        assert model2.type == model.type


class TestModelRegistry:
    """模型注册表测试"""
    
    def test_predefined_models_loaded(self):
        """测试预定义模型加载"""
        registry = ModelRegistry()
        
        # 应该加载了预定义模型
        assert len(registry.models) > 0
        
        # 检查特定模型
        sdxl = registry.get_model("sdxl")
        assert sdxl is not None
        assert sdxl.name == "SDXL"
    
    def test_register_model(self):
        """测试模型注册"""
        registry = ModelRegistry()
        
        new_model = Model(
            model_id="test-model",
            name="Test Model",
            type=ModelType.TEXT_TO_IMAGE,
            provider="test",
            quality_tier=QualityTier.STANDARD
        )
        
        result = registry.register_model(new_model)
        assert result is True
        
        # 验证模型已注册
        retrieved = registry.get_model("test-model")
        assert retrieved is not None
        assert retrieved.name == "Test Model"
    
    def test_list_models_by_type(self):
        """测试按类型列出模型"""
        registry = ModelRegistry()
        
        # 列出所有图像生成模型
        image_models = registry.list_models({
            "type": ModelType.TEXT_TO_IMAGE
        })
        
        assert len(image_models) > 0
        for model in image_models:
            assert model.type == ModelType.TEXT_TO_IMAGE
    
    def test_list_models_by_quality_tier(self):
        """测试按质量档位列出模型"""
        registry = ModelRegistry()
        
        # 列出所有标准质量模型
        standard_models = registry.list_models({
            "quality_tier": QualityTier.STANDARD
        })
        
        assert len(standard_models) > 0
        for model in standard_models:
            assert model.quality_tier == QualityTier.STANDARD
    
    def test_update_model(self):
        """测试模型更新"""
        registry = ModelRegistry()
        
        # 更新模型成本
        result = registry.update_model("sdxl", {
            "cost_per_unit": 0.05
        })
        assert result is True
        
        # 验证更新
        model = registry.get_model("sdxl")
        assert model.cost_per_unit == 0.05
    
    def test_deactivate_model(self):
        """测试模型停用"""
        registry = ModelRegistry()
        
        result = registry.deactivate_model("sdxl")
        assert result is True
        
        # 验证停用
        model = registry.get_model("sdxl")
        assert model.is_active is False


class TestQualityTier:
    """质量档位测试"""
    
    def test_quality_tier_ordering(self):
        """测试质量档位排序"""
        assert QualityTier.DRAFT < QualityTier.STANDARD
        assert QualityTier.STANDARD < QualityTier.HIGH
        assert QualityTier.HIGH < QualityTier.PREMIUM
    
    def test_quality_tier_values(self):
        """测试质量档位值"""
        assert QualityTier.DRAFT.value == 1
        assert QualityTier.STANDARD.value == 2
        assert QualityTier.HIGH.value == 3
        assert QualityTier.PREMIUM.value == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
