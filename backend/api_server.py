"""
VideoGen API Server
提供完整的视频生成 API 服务
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
from openai import OpenAI
import os
import httpx
import logging
import time
import asyncio

# ==================== FastAPI 应用初始化 ====================
app = FastAPI(
    title="VideoGen API",
    description="AI 视频生成系统 API",
    version="1.0.0"
)

# ==================== 日志配置 ====================
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("videogen.api")

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== 请求日志 ====================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info("request start method=%s path=%s", request.method, request.url.path)
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = int((time.time() - start_time) * 1000)
        logger.exception(
            "request error method=%s path=%s duration_ms=%s",
            request.method,
            request.url.path,
            duration_ms,
        )
        raise
    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "request end method=%s path=%s status=%s duration_ms=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# ==================== LLM 客户端初始化 ====================
TRUST_ENV = os.getenv("SOPHNET_TRUST_ENV", "").lower() in {"1", "true", "yes"}
LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    "HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg",
)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://www.sophnet.com/api/open-apis/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "DeepSeek-V3.2")

llm_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    http_client=httpx.Client(timeout=60.0, trust_env=TRUST_ENV),
)

# ==================== 数据模型 ====================
class RequirementInput(BaseModel):
    project_id: str
    requirement: Dict[str, Any]

class ScriptInput(BaseModel):
    project_id: str
    analysis: Optional[Dict[str, Any]] = None

class StoryboardInput(BaseModel):
    project_id: str
    script: Optional[Dict[str, Any]] = None

# ==================== LLM 客户端初始化 ====================
TRUST_ENV = os.getenv("SOPHNET_TRUST_ENV", "").lower() in {"1", "true", "yes"}
LLM_API_KEY = os.getenv(
    "LLM_API_KEY",
    "HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg",
)
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://www.sophnet.com/api/open-apis/v1")
MODEL_NAME = os.getenv("LLM_MODEL", "DeepSeek-V3.2")

llm_client = OpenAI(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    http_client=httpx.Client(timeout=60.0, trust_env=TRUST_ENV),
)

class ImageInput(BaseModel):
    project_id: str
    shot: int
    shot_info: Optional[Dict[str, Any]] = None  # 分镜详细信息

class VideoInput(BaseModel):
    project_id: str
    shot: int  # 镜头编号
    image_url: str  # 参考图 URL
    shot_info: Optional[Dict[str, Any]] = None  # 分镜详细信息

# ==================== 工具函数 ====================
def call_llm(system_prompt: str, user_prompt: str) -> str:
    """调用 LLM"""
    try:
        response = llm_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            timeout=180.0  # 添加 180 秒超时
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"LLM call failed: {e}")
        raise HTTPException(status_code=500, detail=f"LLM 调用失败: {str(e)}")


def _extract_task_id(data: Dict[str, Any]) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    output = data.get("output", {})
    if isinstance(output, dict):
        return output.get("taskId") or output.get("task_id")
    return data.get("taskId") or data.get("task_id")

def _extract_image_url(data: Dict[str, Any]) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    output = data.get("output", {})
    if isinstance(output, dict):
        url = output.get("url") or output.get("image_url") or output.get("imageUrl")
        if url:
            return url
        results = output.get("results")
        if isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict):
                return first.get("url") or first.get("image_url") or first.get("imageUrl")
    return None

def _extract_video_url(data: Dict[str, Any]) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    output = data.get("output", {})
    if isinstance(output, dict):
        url = output.get("url") or output.get("video_url") or output.get("videoUrl")
        if url:
            return url
    content = data.get("content", {})
    if isinstance(content, dict):
        return content.get("video_url") or content.get("url") or content.get("videoUrl")
    return None

def _extract_task_status(data: Dict[str, Any]) -> Optional[str]:
    if not isinstance(data, dict):
        return None
    output = data.get("output", {})
    status = None
    if isinstance(output, dict):
        status = output.get("taskStatus") or output.get("status")
    return status or data.get("taskStatus") or data.get("status")

async def _poll_image_task(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    base_url: str,
    task_id: str,
    poll_interval: float = 2.0,
    max_wait: float = 120.0,
) -> Dict[str, Any]:
    status_urls = [
        f"{base_url}/{task_id}",
        f"{base_url}?task_id={task_id}",
        f"{base_url}?taskId={task_id}",
    ]
    status_url = None
    deadline = time.monotonic() + max_wait
    last_error: Optional[str] = None

    while time.monotonic() < deadline:
        urls_to_try = [status_url] if status_url else status_urls
        response = None

        for url in urls_to_try:
            try:
                response = await client.get(url, headers=headers)
            except Exception as e:
                last_error = str(e)
                continue

            if response.status_code == 200:
                status_url = url
                break

            last_error = f"{response.status_code} {response.text[:200]}"

        if response is None or response.status_code != 200:
            await asyncio.sleep(poll_interval)
            continue

        try:
            data = response.json()
        except ValueError:
            return {"raw": response.text.strip()}

        status = _extract_task_status(data)
        if status:
            status_upper = str(status).upper()
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

        image_url = _extract_image_url(data)
        if status is None and image_url:
            return data

        await asyncio.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": last_error or "timeout"}

async def _poll_video_task(
    client: httpx.AsyncClient,
    headers: Dict[str, str],
    base_url: str,
    task_id: str,
    poll_interval: float = 3.0,
    max_wait: float = 240.0,
) -> Dict[str, Any]:
    status_urls = [
        f"{base_url}/{task_id}",
        f"{base_url}?task_id={task_id}",
        f"{base_url}?taskId={task_id}",
    ]
    status_url = None
    deadline = time.monotonic() + max_wait
    last_error: Optional[str] = None

    while time.monotonic() < deadline:
        urls_to_try = [status_url] if status_url else status_urls
        response = None

        for url in urls_to_try:
            try:
                response = await client.get(url, headers=headers)
            except Exception as e:
                last_error = str(e)
                continue

            if response.status_code == 200:
                status_url = url
                break

            last_error = f"{response.status_code} {response.text[:200]}"

        if response is None or response.status_code != 200:
            await asyncio.sleep(poll_interval)
            continue

        try:
            data = response.json()
        except ValueError:
            return {"raw": response.text.strip()}

        status = _extract_task_status(data)
        if status:
            status_upper = str(status).upper()
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

        video_url = _extract_video_url(data)
        if status is None and video_url and "/None" not in video_url:
            return data

        await asyncio.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": last_error or "timeout"}

# ==================== API 端点 ====================

@app.get("/")
async def root():
    """API 根路径"""
    return {
        "service": "VideoGen API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/api/analyze-requirement")
async def analyze_requirement(data: RequirementInput):
    """
    分析用户需求
    """
    req = data.requirement
    
    system_prompt = """你是一个专业的视频创意分析师。
你的任务是分析用户的视频创作需求，提取核心信息。
请以 JSON 格式返回分析结果，包含以下字段：
- theme: 核心主题
- style: 视觉风格
- shots: 建议镜头数量
- duration: 总时长（秒）
- key_elements: 关键元素列表
"""
    
    user_prompt = f"""请分析以下视频创作需求：
描述：{req.get('description')}
时长：{req.get('duration')} 秒
质量档位：{req.get('quality_tier')}
风格：{req.get('style')}

请给出详细的分析结果。"""
    
    result = call_llm(system_prompt, user_prompt)

    # 解析 LLM 返回的 JSON
    import json
    import re

    try:
        # 提取 JSON 部分
        json_match = re.search(r'\{[\s\S]*\}', result)
        if json_match:
            json_str = json_match.group(0)
            analysis = json.loads(json_str)
            
            return {
                "success": True,
                "theme": analysis.get("theme", "视频创作"),
                "style": analysis.get("style", req.get('style', '现代')),
                "shots": analysis.get("shots", 8),
                "duration": analysis.get("duration", req.get('duration', 30)),
                "key_elements": analysis.get("key_elements", []),
                "analysis_detail": result
            }
    except Exception as e:
        print(f"JSON parse error: {e}")

    # 降级返回
    return {
        "success": True,
        "theme": "视频创作",
        "style": req.get('style', '现代'),
        "shots": 8,
        "duration": req.get('duration', 30),
        "key_elements": [],
        "analysis_detail": result
    }

@app.post("/api/generate-script")
async def generate_script(data: ScriptInput):
    """
    生成视频剧本（参考专业模板系统）
    """
    # 获取需求分析结果
    analysis = data.analysis if hasattr(data, 'analysis') and data.analysis else {}
    
    # 计算每镜头时长
    total_duration = analysis.get('duration', 30)
    shot_count = analysis.get('shots', 8)
    duration_per_shot = total_duration / shot_count
    
    system_prompt = """你是一个专业的电影剧本作家和导演。
你精通视觉叙事、镜头语言和电影制作。

参考以下专业维度创作剧本：

【角色维度】
- 角色外貌描述（面部特征、发型、服装）
- 角色动作和肢体语言
- 表情和微表情
- 角色之间的互动

【场景环境维度】
- 场景类型和空间布局
- 关键物体和背景元素
- 时间（时间段、季节）
- 天气和光线条件
- 色彩调色板
- 环境氛围

【镜头语言维度】
- 镜头类型（特写/近景/中景/远景/全景/鸟瞰等）
- 拍摄角度（平视/俯视/仰视/侧面等）
- 镜头运动（静止/推进/拉远/跟随/旋转/摇移/升降等）
- 画面构图

【风格与情绪维度】
- 艺术风格和视觉风格
- 情绪基调和氛围
- 叙事节奏

【动作与表演维度】
- 主要动作描述
- 次要动作和细节
- 动作的流畅性和连续性

【时间与连续性维度】
- 时间线定位
- 镜头间的状态衔接
- 连续性管理

请创作一个专业的视频剧本，确保：
1. 每个镜头都包含上述维度的详细描述
2. 镜头之间有逻辑连贯性和视觉连续性
3. 符合用户的原始需求和风格
4. 使用专业的电影术语
5. 描述具体且可执行

使用以下格式：

镜头 X：[镜头标题]

【场景】具体位置、空间布局、关键物体
【时间】时间段、天气、光线
【角色】外貌、服装、动作、表情
【镜头】类型、角度、运动
【氛围】色彩、情绪、风格
【声音】对白、旁白、音效（如有）
【转场】与下一镜头的连接方式
时长：X 秒

在剧本最后，请添加角色列表，使用以下格式：

=== 角色列表 ===
[角色名1]
[详细描述：外貌特征、性格特点、服装风格等]

[角色名2]
[详细描述：外貌特征、性格特点、服装风格等]
"""
    
    # 构建包含用户需求的 prompt
    user_prompt = f"""项目信息：
- 项目ID：{data.project_id}
- 核心主题：{analysis.get('theme', '未知')}
- 视觉风格：{analysis.get('style', '未知')}
- 建议镜头数：{shot_count}
- 总时长：{total_duration} 秒
- 每镜头时长：约 {duration_per_shot:.1f} 秒

创作要求：
1. 为每个镜头创作时，必须包含：
   - 【场景】：具体位置、空间布局、关键物体
   - 【时间】：时间段、天气、光线
   - 【角色】：外貌、服装、动作、表情
   - 【镜头】：类型、角度、运动
   - 【氛围】：色彩、情绪、风格
   - 【声音】：对白、旁白、音效（如有）
   - 【转场】：与下一镜头的连接方式

2. 确保镜头间的连贯性：
   - 视觉风格统一
   - 时间线清晰
   - 角色状态连续
   - 空间关系合理

3. 必须包含 {shot_count} 个镜头，每个镜头约 {duration_per_shot:.1f} 秒

请基于以上信息，创作一个完整、专业、可执行的视频剧本。"""
    
    script_content = call_llm(system_prompt, user_prompt)
    
    # 提取角色列表
    import re
    characters = []
    
    # 查找角色列表部分
    character_section_match = re.search(r'===\s*角色列表\s*===\s*(.*?)(?:\n\n\n|\Z)', script_content, re.DOTALL)
    if character_section_match:
        character_text = character_section_match.group(1).strip()
        
        # 按空行分割不同角色
        character_blocks = re.split(r'\n\s*\n', character_text)
        
        for block in character_blocks:
            if not block.strip():
                continue
            
            lines = block.strip().split('\n')
            if len(lines) >= 1:
                # 第一行是角色名
                name = lines[0].strip()
                # 剩余行是描述
                description = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ''
                
                if name:
                    characters.append({
                        "name": name,
                        "description": description
                    })
    
    return {
        "success": True,
        "project_id": data.project_id,
        "content": script_content,
        "characters": characters,
        "metadata": {
            "total_shots": shot_count,
            "total_duration": total_duration,
            "duration_per_shot": round(duration_per_shot, 1),
            "theme": analysis.get('theme'),
            "style": analysis.get('style')
        },
        "created_at": datetime.now().isoformat()
    }

class ScriptUpdateInput(BaseModel):
    project_id: str
    content: str

@app.post("/api/update-script")
async def update_script(data: ScriptUpdateInput):
    """
    更新/保存编辑后的剧本
    """
    if not data.content or not data.content.strip():
        raise HTTPException(status_code=400, detail="剧本内容不能为空")
    
    # 这里可以添加保存到数据库的逻辑
    # 目前简单返回成功，由前端管理状态
    return {
        "success": True,
        "project_id": data.project_id,
        "content": data.content,
        "message": "剧本更新成功",
        "updated_at": datetime.now().isoformat()
    }


@app.post("/api/generate-storyboard")
async def generate_storyboard(data: StoryboardInput):
    """
    生成分镜脚本
    """
    system_prompt = """你是一个专业的电影分镜师和导演。
你的任务是将剧本转换为非常详细的分镜脚本，每个镜头都要包含完整的拍摄信息。

请严格按照以下 JSON 格式返回分镜数组（只返回 JSON，不要其他文字）：
[
  {
    "shot_id": "S001",
    "title": "镜头标题",
    "description": "详细的场景描述，包括环境、光线、氛围等",
    "scene": "具体场景位置和环境描述",
    "characters": "人物/主体及其动作描述",
    "action": "具体的动作和运动描述",
    "visual_elements": "关键视觉元素：色彩、构图、重点物体等",
    "dialogue": "对白或旁白（如有）",
    "narration": "画外音或解说词（如有）",
    "duration": 4,
    "camera": "机位类型：特写/近景/中景/远景/全景/鸟瞰等",
    "angle": "拍摄角度：平视/俯视/仰视/侧面等",
    "movement": "镜头运动：静止/推进/拉远/跟随/旋转/摇移/升降等",
    "transition": "转场效果：切/淡入淡出/叠化/划像等",
    "emotion": "情绪基调",
    "notes": "特殊说明或注意事项"
  }
]"""
    
    # 获取剧本内容
    script_content = ''
    if data.script and isinstance(data.script, dict):
        script_content = data.script.get('content', '')
    
    user_prompt = f"""项目ID：{data.project_id}

剧本内容：
{script_content[:1000] if script_content else '请根据项目需求生成分镜'}

请基于以上剧本，生成详细的分镜脚本。
要求：
1. 每个镜头都要有完整的场景、人物动作、视觉元素描述
2. 镜头之间要有逻辑连贯性
3. 包含具体的拍摄参数和技术要求
4. 只返回 JSON 数组，不要其他文字"""
    
    storyboard_content = call_llm(system_prompt, user_prompt)
    
    # 解析 LLM 返回的 JSON
    import json
    import re
    
    try:
        # 提取 JSON 数组
        json_match = re.search(r'\[[\s\S]*\]', storyboard_content)
        if json_match:
            json_str = json_match.group(0)
            shots = json.loads(json_str)
            
            return {
                "success": True,
                "project_id": data.project_id,
                "shots": shots,
                "total_shots": len(shots),
                "created_at": datetime.now().isoformat()
            }
    except Exception as e:
        print(f"Storyboard JSON parse error: {e}")
    
    # 降级：返回基本结构
    shots = []
    for i in range(8):
        shots.append({
            "shot_id": f"S{str(i+1).zfill(3)}",
            "title": f"镜头 {i+1}",
            "description": f"场景描述 {i+1}",
            "scene": "场景位置",
            "characters": "主体描述",
            "action": "动作描述",
            "visual_elements": "视觉元素",
            "duration": 4,
            "camera": "中景",
            "angle": "平视",
            "movement": "静止",
            "transition": "切",
            "emotion": "中性"
        })
    
    return {
        "success": True,
        "project_id": data.project_id,
        "shots": shots,
        "total_shots": len(shots),
        "created_at": datetime.now().isoformat(),
        "raw_content": storyboard_content
    }

@app.post("/api/generate-image")
async def generate_image(data: ImageInput):
    """
    生成单个镜头的图像
    使用 Qwen 图像生成模型
    """
    # 构建详细的 prompt
    if data.shot_info:
        # 使用分镜脚本的详细信息
        shot = data.shot_info
        prompt_parts = []
        
        # 场景描述
        if shot.get('scene'):
            prompt_parts.append(shot['scene'])
        
        # 人物/主体
        if shot.get('characters'):
            prompt_parts.append(shot['characters'])
        
        # 动作
        if shot.get('action'):
            prompt_parts.append(shot['action'])
        
        # 视觉元素
        if shot.get('visual_elements'):
            prompt_parts.append(shot['visual_elements'])
        
        # 拍摄参数
        camera_info = []
        if shot.get('camera'):
            camera_info.append(f"{shot['camera']}镜头")
        if shot.get('angle'):
            camera_info.append(f"{shot['angle']}角度")
        if camera_info:
            prompt_parts.append(', '.join(camera_info))
        
        # 情绪基调
        if shot.get('emotion'):
            prompt_parts.append(f"{shot['emotion']}氛围")
        
        # 组合 prompt
        prompt = ', '.join(prompt_parts)
        
        # 添加质量描述
        prompt += ", 专业电影摄影, 高质量, 4K分辨率, 电影级别画质"
    else:
        # 降级到简单 prompt
        prompt = f"专业电影镜头，高质量，4K分辨率，镜头 {data.shot}"
    
    print(f"Image generation prompt for shot {data.shot}: {prompt}")
    
    try:
        image_api_url = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"
        headers = {
            "Authorization": f"Bearer HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg",
            "Content-Type": "application/json"
        }

        # 调用 Qwen 图像生成 API
        async with httpx.AsyncClient(timeout=60.0, trust_env=TRUST_ENV) as client:
            response = await client.post(
                image_api_url,
                headers=headers,
                json={
                    "model": "qwen-image",
                    "input": {
                        "prompt": prompt
                    },
                    "parameters": {
                        "size": "1328*1328",
                        "seed": 42 + data.shot  # 每个镜头不同的 seed
                    }
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"图像生成失败: {response.text}"
                )

            result = response.json()
            task_id = _extract_task_id(result)
            image_url = _extract_image_url(result)

            if task_id and not image_url:
                logger.info("image task polling start task_id=%s", task_id)
                final_result = await _poll_image_task(
                    client,
                    headers,
                    image_api_url,
                    task_id,
                )
                task_status = _extract_task_status(final_result)
                image_url = _extract_image_url(final_result) or image_url
                logger.info("image task polling end task_id=%s status=%s", task_id, task_status)
            else:
                task_status = _extract_task_status(result)

            if not image_url:
                raise HTTPException(
                    status_code=502,
                    detail="图像生成完成但未返回可用的 image_url"
                )

            return {
                "success": True,
                "project_id": data.project_id,
                "shot": data.shot,
                "image_url": image_url,
                "prompt": prompt,
                "task_id": task_id,
                "task_status": task_status,
                "generated_at": datetime.now().isoformat()
            }
                
    except Exception as e:
        print(f"Image generation error: {e}")
        # 降级到占位图
        return {
            "success": False,
            "project_id": data.project_id,
            "shot": data.shot,
            "image_url": f"https://via.placeholder.com/1328x1328/1e293b/6366f1?text=Shot+{data.shot}",
            "error": str(e),
            "generated_at": datetime.now().isoformat()
        }

@app.post("/api/generate-video")
async def generate_video(data: VideoInput):
    """
    生成单个镜头的视频
    使用 Wan2.2 image-to-video 模型，基于参考图生成视频
    """
    # 构建详细的视频描述
    if data.shot_info:
        shot = data.shot_info
        prompt_parts = []
        
        # 动作描述（最重要）
        if shot.get('action'):
            prompt_parts.append(shot['action'])
        
        # 镜头运动
        if shot.get('movement') and shot.get('movement') != '静止':
            prompt_parts.append(f"镜头{shot['movement']}")
        
        # 场景描述
        if shot.get('scene'):
            prompt_parts.append(shot['scene'])
        
        # 人物/主体
        if shot.get('characters'):
            prompt_parts.append(shot['characters'])
        
        # 情绪基调
        if shot.get('emotion'):
            prompt_parts.append(f"{shot['emotion']}氛围")
        
        # 组合 prompt
        video_description = ', '.join(prompt_parts)
        video_description += ", 专业电影摄影, 高质量, 电影级别画质, 流畅的动作"
    else:
        video_description = f"专业视频制作，高质量，电影级别，镜头 {data.shot}"
    
    print(f"Video generation for shot {data.shot}")
    print(f"Image URL: {data.image_url}")
    print(f"Prompt: {video_description}")
    
    try:
        video_api_url = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/task"
        headers = {
            "Authorization": f"Bearer HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg",
            "Content-Type": "application/json"
        }

        # 调用 Wan2.2 image-to-video API
        async with httpx.AsyncClient(timeout=120.0, trust_env=TRUST_ENV) as client:
            response = await client.post(
                video_api_url,
                headers=headers,
                json={
                    "model": "Wan2.2-I2V-A14B",  # 使用 image-to-video 模型
                    "content": [
                        {
                            "type": "image_url",  # 使用图像作为输入
                            "image_url": {
                                "url": data.image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": video_description
                        }
                    ],
                    "parameters": {
                        "size": "1280*720",
                        "watermark": True,
                        "seed": 16 + data.shot  # 每个镜头不同的 seed
                    }
                }
            )

            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"视频生成失败: {response.text}"
                )

            task_id = None
            result = None
            try:
                result = response.json()
                task_id = _extract_task_id(result)
            except ValueError:
                task_id = response.text.strip() or None

            video_url = _extract_video_url(result) if result else None

            if task_id and not video_url:
                logger.info("video task polling start task_id=%s", task_id)
                final_result = await _poll_video_task(
                    client,
                    headers,
                    video_api_url,
                    task_id,
                )
                task_status = _extract_task_status(final_result)
                video_url = _extract_video_url(final_result) or video_url
                logger.info("video task polling end task_id=%s status=%s", task_id, task_status)
            else:
                task_status = _extract_task_status(result) if result else None

            if not video_url:
                raise HTTPException(
                    status_code=502,
                    detail="视频生成完成但未返回可用的 video_url"
                )

            return {
                "success": True,
                "project_id": data.project_id,
                "video_url": video_url,
                "description": video_description,
                "task_id": task_id,
                "task_status": task_status,
                "duration": 30,
                "resolution": "1280x720",
                "generated_at": datetime.now().isoformat()
            }
                
    except Exception as e:
        print(f"Video generation error: {e}")
        # 降级到示例视频
        return {
            "success": False,
            "project_id": data.project_id,
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "error": str(e),
            "duration": 30,
            "resolution": "1280x720",
            "generated_at": datetime.now().isoformat()
        }

# ==================== 运行服务器 ====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
