# RequirementParser Agent 使用示例

本文档提供了 RequirementParser Agent 的各种使用场景和代码示例。

## 目录

- [基础示例](#基础示例)
- [高级用法](#高级用法)
- [错误处理](#错误处理)
- [性能优化](#性能优化)
- [集成示例](#集成示例)

## 基础示例

### 示例 1: 简单文本输入

最基本的使用场景，仅提供文本描述。

```python
import asyncio
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.requirement_parser.models import UserInputData

async def simple_text_example():
    """简单文本输入示例"""
    
    # 创建 Agent
    async with RequirementParserAgent() as agent:
        # 准备用户输入
        user_input = UserInputData(
            text_description="一个年轻的探险家在神秘森林中寻找宝藏，时长30秒"
        )
        
        # 处理输入
        result = await agent.process_user_input(user_input)
        
        # 检查结果
        if result.is_successful():
            print(f"✅ 处理成功!")
            print(f"项目标题: {result.global_spec.title}")
            print(f"视频时长: {result.global_spec.duration}秒")
            print(f"置信度: {result.confidence_report.overall_confidence:.2f}")
        else:
            print(f"❌ 处理失败: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(simple_text_example())
```

**输出示例**:
```
✅ 处理成功!
项目标题: 探险家寻宝
视频时长: 30秒
置信度: 0.75
```

### 示例 2: 多模态输入

包含文本、图片和音频的完整输入。

```python
async def multimodal_example():
    """多模态输入示例"""
    
    async with RequirementParserAgent() as agent:
        user_input = UserInputData(
            text_description="一个温馨的家庭聚餐场景，充满欢声笑语",
            reference_images=[
                "s3://my-bucket/reference/warm-lighting.jpg",
                "s3://my-bucket/reference/family-table.jpg"
            ],
            reference_audio=[
                "s3://my-bucket/reference/background-music.mp3"
            ],
            user_preferences={
                "quality_tier": "high",
                "aspect_ratio": "16:9"
            }
        )
        
        result = await agent.process_user_input(user_input)
        
        if result.is_successful():
            spec = result.global_spec
            print(f"项目: {spec.title}")
            print(f"风格色调: {spec.style.tone}")
            print(f"调色板: {', '.join(spec.style.palette)}")
            print(f"角色: {', '.join(spec.characters)}")
            print(f"情绪: {spec.mood}")
            print(f"处理时间: {result.processing_time:.2f}秒")
            print(f"成本: ${result.cost:.4f}")

asyncio.run(multimodal_example())
```

**输出示例**:
```
项目: 家庭聚餐
风格色调: warm
调色板: #FFA500, #FFD700, #FFFFFF
角色: 父亲, 母亲, 孩子
情绪: 温馨,欢乐
处理时间: 5.23秒
成本: $0.0150
```

### 示例 3: 自定义配置

使用自定义配置创建 Agent。

```python
from src.agents.requirement_parser.config import RequirementParserConfig

async def custom_config_example():
    """自定义配置示例"""
    
    # 创建自定义配置
    config = RequirementParserConfig(
        agent_name="CustomRequirementParser",
        max_retries=5,
        timeout_seconds=60,
        confidence_threshold=0.7,
        default_quality_tier="high",
        default_aspect_ratio="16:9"
    )
    
    # 使用自定义配置创建 Agent
    async with RequirementParserAgent(config=config) as agent:
        user_input = UserInputData(
            text_description="科幻未来城市，霓虹灯闪烁"
        )
        
        result = await agent.process_user_input(user_input)
        
        if result.is_successful():
            print(f"使用配置: {config.agent_name}")
            print(f"质量档位: {result.global_spec.quality_tier}")
            print(f"宽高比: {result.global_spec.aspect_ratio}")

asyncio.run(custom_config_example())
```

## 高级用法

### 示例 4: 批量处理

并发处理多个用户输入。

```python
async def batch_processing_example():
    """批量处理示例"""
    
    # 准备多个输入
    inputs = [
        UserInputData(text_description="探险家在森林中寻宝"),
        UserInputData(text_description="温馨的家庭聚餐"),
        UserInputData(text_description="激烈的体育比赛"),
        UserInputData(text_description="宁静的乡村田园"),
        UserInputData(text_description="科幻未来城市")
    ]
    
    async with RequirementParserAgent() as agent:
        # 并发处理所有输入
        tasks = [agent.process_user_input(inp) for inp in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 统计结果
        successful = sum(1 for r in results if isinstance(r, ProcessingResult) and r.is_successful())
        failed = len(results) - successful
        
        print(f"批量处理完成:")
        print(f"  成功: {successful}/{len(results)}")
        print(f"  失败: {failed}/{len(results)}")
        
        # 显示每个结果
        for i, result in enumerate(results):
            if isinstance(result, ProcessingResult) and result.is_successful():
                print(f"  [{i+1}] ✅ {result.global_spec.title}")
            else:
                print(f"  [{i+1}] ❌ 处理失败")

asyncio.run(batch_processing_example())
```

**输出示例**:
```
批量处理完成:
  成功: 5/5
  失败: 0/5
  [1] ✅ 探险家寻宝
  [2] ✅ 家庭聚餐
  [3] ✅ 体育比赛
  [4] ✅ 乡村田园
  [5] ✅ 未来城市
```

### 示例 5: 置信度处理

根据置信度采取不同行动。

```python
async def confidence_handling_example():
    """置信度处理示例"""
    
    async with RequirementParserAgent() as agent:
        user_input = UserInputData(
            text_description="一个视频"  # 模糊的输入
        )
        
        result = await agent.process_user_input(user_input)
        
        if result.is_successful():
            report = result.confidence_report
            
            print(f"置信度: {report.overall_confidence:.2f}")
            print(f"等级: {report.confidence_level.value}")
            print(f"建议: {report.recommendation}")
            
            if report.recommendation == "proceed":
                print("✅ 可以继续处理")
                
            elif report.recommendation == "clarify":
                print("⚠️ 建议澄清以下问题:")
                for req in report.clarification_requests:
                    print(f"  - {req.field}: {req.question}")
                    if req.suggestions:
                        print(f"    建议: {', '.join(req.suggestions)}")
                
            elif report.recommendation == "human_review":
                print("🔍 需要人工审核")
                print(f"低置信度区域: {', '.join(report.low_confidence_areas)}")

asyncio.run(confidence_handling_example())
```

**输出示例**:
```
置信度: 0.45
等级: LOW
建议: clarify
⚠️ 建议澄清以下问题:
  - title: 请提供更具体的项目标题或主题
    建议: 探险, 家庭, 科幻, 运动
  - style: 请描述期望的视觉风格
    建议: 现代简约, 复古怀旧, 科幻未来
  - duration: 请指定视频时长
```

### 示例 6: 流式处理

实时显示处理进度。

```python
async def streaming_example():
    """流式处理示例（模拟）"""
    
    async with RequirementParserAgent() as agent:
        user_input = UserInputData(
            text_description="一个年轻的探险家在神秘森林中寻找宝藏",
            reference_images=["s3://bucket/image1.jpg"]
        )
        
        print("开始处理...")
        print("  [1/5] 验证输入...")
        await asyncio.sleep(0.5)
        
        print("  [2/5] 预处理数据...")
        await asyncio.sleep(0.5)
        
        print("  [3/5] 调用 AI 分析...")
        result = await agent.process_user_input(user_input)
        
        print("  [4/5] 生成 GlobalSpec...")
        await asyncio.sleep(0.5)
        
        print("  [5/5] 评估置信度...")
        await asyncio.sleep(0.5)
        
        if result.is_successful():
            print(f"✅ 处理完成! 项目: {result.global_spec.title}")

asyncio.run(streaming_example())
```

## 错误处理

### 示例 7: 完整的错误处理

处理各种可能的错误情况。

```python
from src.agents.requirement_parser.exceptions import (
    RequirementParserError,
    DeepSeekAPIError,
    InputValidationError,
    HumanInterventionRequired,
    ConfigurationError
)

async def error_handling_example():
    """完整的错误处理示例"""
    
    try:
        async with RequirementParserAgent() as agent:
            user_input = UserInputData(
                text_description="一个视频项目"
            )
            
            result = await agent.process_user_input(user_input)
            
            if result.is_successful():
                print(f"✅ 成功: {result.global_spec.title}")
            else:
                print(f"❌ 失败: {result.error_message}")
    
    except InputValidationError as e:
        print(f"❌ 输入验证失败: {e}")
        print("请检查输入格式和内容")
    
    except DeepSeekAPIError as e:
        print(f"❌ API 调用失败: {e}")
        print("请检查:")
        print("  1. API Key 是否正确")
        print("  2. 网络连接是否正常")
        print("  3. API 配额是否充足")
    
    except HumanInterventionRequired as e:
        print(f"🔍 需要人工介入: {e}")
        print("置信度过低，建议人工审核")
    
    except ConfigurationError as e:
        print(f"❌ 配置错误: {e}")
        print("请检查环境变量配置")
    
    except RequirementParserError as e:
        print(f"❌ 处理错误: {e}")
    
    except Exception as e:
        print(f"❌ 未知错误: {e}")

asyncio.run(error_handling_example())
```

### 示例 8: 重试机制

自定义重试逻辑。

```python
async def retry_example():
    """重试机制示例"""
    
    max_attempts = 3
    
    for attempt in range(max_attempts):
        try:
            async with RequirementParserAgent() as agent:
                user_input = UserInputData(
                    text_description="一个视频项目"
                )
                
                result = await agent.process_user_input(user_input)
                
                if result.is_successful():
                    print(f"✅ 第 {attempt + 1} 次尝试成功")
                    break
                else:
                    print(f"⚠️ 第 {attempt + 1} 次尝试失败: {result.error_message}")
        
        except Exception as e:
            print(f"❌ 第 {attempt + 1} 次尝试出错: {e}")
            
            if attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # 指数退避
                print(f"等待 {wait_time} 秒后重试...")
                await asyncio.sleep(wait_time)
            else:
                print("已达到最大重试次数，放弃处理")

asyncio.run(retry_example())
```

## 性能优化

### 示例 9: 连接池复用

复用 Agent 实例以提高性能。

```python
async def connection_pool_example():
    """连接池复用示例"""
    
    # 创建一个长期存在的 Agent 实例
    agent = RequirementParserAgent()
    
    try:
        # 处理多个请求
        for i in range(10):
            user_input = UserInputData(
                text_description=f"视频项目 {i+1}"
            )
            
            result = await agent.process_user_input(user_input)
            
            if result.is_successful():
                print(f"[{i+1}] ✅ {result.global_spec.title}")
    
    finally:
        # 确保关闭 Agent
        await agent.close()

asyncio.run(connection_pool_example())
```

### 示例 10: 性能监控

监控处理性能和资源使用。

```python
import time
from typing import List

async def performance_monitoring_example():
    """性能监控示例"""
    
    class PerformanceMonitor:
        def __init__(self):
            self.results: List[ProcessingResult] = []
        
        def add_result(self, result: ProcessingResult):
            self.results.append(result)
        
        def print_statistics(self):
            if not self.results:
                print("没有数据")
                return
            
            successful = [r for r in self.results if r.is_successful()]
            failed = [r for r in self.results if not r.is_successful()]
            
            print(f"\n性能统计:")
            print(f"  总请求数: {len(self.results)}")
            print(f"  成功: {len(successful)} ({len(successful)/len(self.results)*100:.1f}%)")
            print(f"  失败: {len(failed)} ({len(failed)/len(self.results)*100:.1f}%)")
            
            if successful:
                times = [r.processing_time for r in successful]
                costs = [r.cost for r in successful]
                confidences = [r.confidence_report.overall_confidence for r in successful]
                
                print(f"\n  处理时间:")
                print(f"    平均: {sum(times)/len(times):.2f}秒")
                print(f"    最小: {min(times):.2f}秒")
                print(f"    最大: {max(times):.2f}秒")
                
                print(f"\n  成本:")
                print(f"    总计: ${sum(costs):.4f}")
                print(f"    平均: ${sum(costs)/len(costs):.4f}")
                
                print(f"\n  置信度:")
                print(f"    平均: {sum(confidences)/len(confidences):.2f}")
                print(f"    最小: {min(confidences):.2f}")
                print(f"    最大: {max(confidences):.2f}")
    
    monitor = PerformanceMonitor()
    
    async with RequirementParserAgent() as agent:
        # 处理多个请求
        inputs = [
            UserInputData(text_description=f"视频项目 {i+1}")
            for i in range(10)
        ]
        
        for user_input in inputs:
            result = await agent.process_user_input(user_input)
            monitor.add_result(result)
    
    monitor.print_statistics()

asyncio.run(performance_monitoring_example())
```

**输出示例**:
```
性能统计:
  总请求数: 10
  成功: 10 (100.0%)
  失败: 0 (0.0%)

  处理时间:
    平均: 3.45秒
    最小: 2.12秒
    最大: 5.67秒

  成本:
    总计: $0.1250
    平均: $0.0125

  置信度:
    平均: 0.72
    最小: 0.65
    最大: 0.85
```

## 集成示例

### 示例 11: FastAPI 集成

将 Agent 集成到 FastAPI 应用中。

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI(title="RequirementParser API")

# 全局 Agent 实例
agent: Optional[RequirementParserAgent] = None

@app.on_event("startup")
async def startup_event():
    """应用启动时创建 Agent"""
    global agent
    agent = RequirementParserAgent()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理 Agent"""
    global agent
    if agent:
        await agent.close()

class ProcessRequest(BaseModel):
    text_description: str
    reference_images: List[str] = []
    reference_videos: List[str] = []
    reference_audio: List[str] = []
    user_preferences: dict = {}

class ProcessResponse(BaseModel):
    success: bool
    project_id: Optional[str] = None
    title: Optional[str] = None
    duration: Optional[int] = None
    confidence: Optional[float] = None
    error_message: Optional[str] = None

@app.post("/api/v1/process", response_model=ProcessResponse)
async def process_requirement(request: ProcessRequest):
    """处理用户需求"""
    
    if not agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")
    
    try:
        user_input = UserInputData(
            text_description=request.text_description,
            reference_images=request.reference_images,
            reference_videos=request.reference_videos,
            reference_audio=request.reference_audio,
            user_preferences=request.user_preferences
        )
        
        result = await agent.process_user_input(user_input)
        
        if result.is_successful():
            return ProcessResponse(
                success=True,
                title=result.global_spec.title,
                duration=result.global_spec.duration,
                confidence=result.confidence_report.overall_confidence
            )
        else:
            return ProcessResponse(
                success=False,
                error_message=result.error_message
            )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "agent_ready": agent is not None}

# 运行: uvicorn main:app --reload
```

### 示例 12: 事件驱动集成

与事件总线集成。

```python
import json
from typing import Callable

class EventBusIntegration:
    """事件总线集成示例"""
    
    def __init__(self, agent: RequirementParserAgent):
        self.agent = agent
        self.event_handlers = {}
    
    def on_event(self, event_type: str, handler: Callable):
        """注册事件处理器"""
        self.event_handlers[event_type] = handler
    
    async def handle_user_input_event(self, event_data: dict):
        """处理用户输入事件"""
        
        # 解析事件数据
        user_input = UserInputData(
            text_description=event_data.get("text_description", ""),
            reference_images=event_data.get("reference_images", []),
            reference_videos=event_data.get("reference_videos", []),
            reference_audio=event_data.get("reference_audio", []),
            user_preferences=event_data.get("user_preferences", {})
        )
        
        # 处理输入
        result = await self.agent.process_user_input(
            user_input,
            causation_id=event_data.get("event_id")
        )
        
        # 触发相应的事件处理器
        if result.is_successful():
            if "project_created" in self.event_handlers:
                await self.event_handlers["project_created"](result)
        else:
            if "processing_failed" in self.event_handlers:
                await self.event_handlers["processing_failed"](result)

async def event_driven_example():
    """事件驱动集成示例"""
    
    async with RequirementParserAgent() as agent:
        integration = EventBusIntegration(agent)
        
        # 注册事件处理器
        async def on_project_created(result: ProcessingResult):
            print(f"✅ 项目创建: {result.global_spec.title}")
        
        async def on_processing_failed(result: ProcessingResult):
            print(f"❌ 处理失败: {result.error_message}")
        
        integration.on_event("project_created", on_project_created)
        integration.on_event("processing_failed", on_processing_failed)
        
        # 模拟接收事件
        event_data = {
            "event_id": "evt_123",
            "text_description": "一个视频项目",
            "reference_images": []
        }
        
        await integration.handle_user_input_event(event_data)

asyncio.run(event_driven_example())
```

## 测试示例

### 示例 13: 单元测试

使用 pytest 进行单元测试。

```python
import pytest
from src.agents.requirement_parser import RequirementParserAgent
from src.agents.requirement_parser.models import UserInputData

@pytest.mark.asyncio
async def test_simple_processing():
    """测试简单处理流程"""
    
    async with RequirementParserAgent() as agent:
        user_input = UserInputData(
            text_description="一个测试视频"
        )
        
        result = await agent.process_user_input(user_input)
        
        assert result.is_successful()
        assert result.global_spec is not None
        assert result.global_spec.title != ""
        assert result.confidence_report is not None

@pytest.mark.asyncio
async def test_multimodal_processing():
    """测试多模态处理"""
    
    async with RequirementParserAgent() as agent:
        user_input = UserInputData(
            text_description="温馨的家庭聚餐",
            reference_images=["s3://bucket/image.jpg"]
        )
        
        result = await agent.process_user_input(user_input)
        
        assert result.is_successful()
        assert len(result.global_spec.characters) > 0

# 运行: pytest test_examples.py -v
```

## 总结

这些示例涵盖了 RequirementParser Agent 的主要使用场景：

1. **基础用法**: 简单文本输入、多模态输入、自定义配置
2. **高级功能**: 批量处理、置信度处理、流式处理
3. **错误处理**: 完整的异常处理、重试机制
4. **性能优化**: 连接池复用、性能监控
5. **系统集成**: FastAPI 集成、事件驱动集成
6. **测试**: 单元测试示例

更多信息请参考：
- [API 文档](API.md)
- [README](README.md)
- [设计文档](.kiro/specs/requirement-parser-agent/design.md)
