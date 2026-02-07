# 改进的分镜生成端点代码
# 将此代码替换到 api_server.py 的 generate_storyboard 函数中

@app.post("/api/generate-storyboard")
async def generate_storyboard(data: StoryboardInput):
    """
    生成详细的分镜脚本
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
    script_content = data.script.get('content', '') if hasattr(data, 'script') and data.script else ''
    
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
