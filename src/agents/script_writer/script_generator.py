"""
优化版剧本生成器

包含多轮优化、可行性检查和自动重写机制。
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional


logger = logging.getLogger(__name__)


class ScriptGenerator:
    """
    优化版剧本生成器
    
    特性：
    - 结构化 prompt 工程
    - 多阶段生成（outline -> details）
    - 可行性自动检查
    - 智能重写机制
    - 质量评分系统
    """
    
    def __init__(self, llm_client):
        """
        初始化生成器
        
        Args:
            llm_client: LLM 客户端
        """
        self.llm_client = llm_client
        self.max_retries = 3
        self.feasibility_threshold = 0.28
    
    async def generate_script(
        self,
        global_spec: Dict[str, Any],
        retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        生成剧本（优化版）
        
        Args:
            global_spec: 全局规格
            retry_count: 重试次数
            
        Returns:
            Dict: 剧本数据
        """
        logger.info(f"Generating script (attempt {retry_count + 1}/{self.max_retries + 1})")
        
        try:
            # 阶段 1: 生成大纲
            outline = await self._generate_outline(global_spec)
            
            # 阶段 2: 基于大纲生成详细剧本
            script = await self._generate_detailed_script(outline, global_spec)
            
            # 阶段 3: 可行性检查
            feasibility_score = self._check_feasibility(script)
            
            logger.info(f"Script feasibility score: {feasibility_score:.2f}")
            
            # 如果可行性太低，自动重写
            if feasibility_score < self.feasibility_threshold:
                if retry_count < self.max_retries:
                    logger.warning(f"Low feasibility ({feasibility_score:.2f}), retrying...")
                    return await self.generate_script(global_spec, retry_count + 1)
                else:
                    logger.error(f"Max retries reached, feasibility still low: {feasibility_score:.2f}")
            
            # 阶段 4: 后处理优化
            script = self._post_process(script, global_spec)
            
            return script
            
        except Exception as e:
            logger.error(f"Script generation failed: {e}", exc_info=True)
            
            if retry_count < self.max_retries:
                logger.info("Retrying due to error...")
                return await self.generate_script(global_spec, retry_count + 1)
            else:
                raise
    
    async def _generate_outline(self, global_spec: Dict[str, Any]) -> str:
        """
        阶段 1: 生成剧本大纲
        
        Args:
            global_spec: 全局规格
            
        Returns:
            str: 大纲文本
        """
        system_prompt = """You are a professional video scriptwriter.

Task: Create a brief outline for an AI-generated video.

Guidelines:
- Focus on visual storytelling
- Keep it simple and achievable
- Think in terms of scenes and shots
- Each scene should be 5-15 seconds
- Use concrete, visual descriptions

Output format: Text outline with numbered scenes."""
        
        user_prompt = f"""Create a video outline with these requirements:

Title: {global_spec.get('title', 'Untitled')}
Total Duration: {global_spec.get('duration', 30)} seconds
Style: {global_spec.get('style', 'cinematic')}
Mood: {global_spec.get('mood', 'neutral')}

User Description: {global_spec.get('description', 'No specific description')}

Requirements:
- 3-5 scenes
- Each scene 5-15 seconds
- Visual and concrete
- Achievable with AI generation

Create the outline now."""
        
        outline = await self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        logger.debug(f"Generated outline: {outline[:200]}...")
        
        return outline
    
    async def _generate_detailed_script(
        self,
        outline: str,
        global_spec: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        阶段 2: 基于大纲生成详细剧本
        
        Args:
            outline: 剧本大纲
            global_spec: 全局规格
            
        Returns:
            Dict: 详细剧本（JSON格式）
        """
        system_prompt = """You are a professional scriptwriter for AI video generation.

Task: Convert an outline into a detailed, structured script.

Critical Rules:
1. Visual-First: Use concrete visual descriptions, avoid abstract concepts
2. AI-Friendly: Each shot must be achievable with current image/video AI
3. Consistency: Maintain character and scene consistency
4. Duration: Respect target durations
5. Structure: Output MUST be valid JSON

JSON Format:
{
  "title": "...",
  "total_duration": 30,
  "scenes": [
    {
      "scene_id": "S001",
      "description": "Visual scene description",
      "duration_estimate": 10,
      "environment": "Location description",
      "characters": ["Character names"],
      "shots": [
        {
          "shot_id": "S001_001",
          "description": "Detailed visual description",
          "duration": 3-7,
          "characters": ["..."],
          "mood_tags": ["happy", "peaceful"],
          "dialogue": "Optional dialogue",
          "camera_notes": "Optional camera direction"
        }
      ]
    }
  ]
}

IMPORTANT: Output ONLY valid JSON, no markdown formatting."""
        
        user_prompt = f"""Convert this outline into a detailed script:

OUTLINE:
{outline}

SPECIFICATIONS:
- Total Duration: {global_spec.get('duration', 30)} seconds
- Style: {global_spec.get('style', 'cinematic')}
- Aspect Ratio: {global_spec.get('aspect_ratio', '9:16')}

REQUIREMENTS:
1. Each shot: 3-7 seconds
2. Use visual, concrete language
3. Include character descriptions if any
4. Add mood tags for each shot
5. Maintain visual consistency

Output the complete script in JSON format NOW."""
        
        # 使用 JSON mode（如果是 OpenAI）
        response_format = None
        if self.llm_client.provider == "openai":
            response_format = {"type": "json_object"}
        
        response = await self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.6,  # 稍低的温度以提高结构一致性
            max_tokens=3000,
            response_format=response_format
        )
        
        # 解析 JSON
        script = self._parse_json_response(response)
        
        return script
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        解析 JSON 响应
        
        Args:
            response: LLM 响应
            
        Returns:
            Dict: 解析后的数据
        """
        # 尝试直接解析
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # 尝试提取 JSON（可能包裹在 markdown 中）
        json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # 尝试查找 JSON 对象
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except json.JSONDecodeError:
                pass
        
        logger.error(f"Failed to parse JSON response: {response[:200]}...")
        raise ValueError("Invalid JSON response from LLM")
    
    def _check_feasibility(self, script: Dict[str, Any]) -> float:
        """
        检查剧本可行性
        
        评估标准：
        - 描述具体性（concrete vs abstract）
        - Shot 时长合理性
        - 视觉可实现性
        - 结构完整性
        
        Args:
            script: 剧本数据
            
        Returns:
            float: 可行性分数 (0.0 - 1.0)
        """
        score = 1.0
        issues = []
        
        scenes = script.get("scenes", [])
        if not scenes:
            return 0.0
        
        for scene in scenes:
            shots = scene.get("shots", [])
            
            if not shots:
                score -= 0.2
                issues.append(f"Scene {scene.get('scene_id')} has no shots")
                continue
            
            for shot in shots:
                # 检查描述
                description = shot.get("description", "")
                
                if not description or len(description) < 20:
                    score -= 0.1
                    issues.append(f"Shot {shot.get('shot_id')} has insufficient description")
                
                # 检查抽象词汇
                abstract_words = [
                    "idea", "concept", "feeling", "thought", "emotion",
                    "abstract", "intangible", "invisible", "metaphor"
                ]
                
                if any(word in description.lower() for word in abstract_words):
                    score -= 0.05
                    issues.append(f"Shot {shot.get('shot_id')} contains abstract concepts")
                
                # 检查时长
                duration = shot.get("duration", 0)
                if duration < 2 or duration > 10:
                    score -= 0.05
                    issues.append(f"Shot {shot.get('shot_id')} has unusual duration: {duration}s")
                
                # 检查必要字段
                if not shot.get("characters") and not shot.get("environment"):
                    score -= 0.03
        
        score = max(0.0, min(1.0, score))
        
        if issues:
            logger.warning(f"Feasibility issues found ({len(issues)}): {issues[:3]}")
        
        return score
    
    def _post_process(self, script: Dict[str, Any], global_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        后处理优化
        
        Args:
            script: 原始剧本
            global_spec: 全局规格
            
        Returns:
            Dict: 优化后的剧本
        """
        # 1. 标准化 shot IDs
        for i, scene in enumerate(script.get("scenes", [])):
            scene["scene_id"] = f"S{i+1:03d}"
            
            for j, shot in enumerate(scene.get("shots", [])):
                shot["shot_id"] = f"S{i+1:03d}_{j+1:03d}"
        
        # 2. 补充缺失字段
        for scene in script.get("scenes", [])):
            if "environment" not in scene:
                scene["environment"] = "unspecified"
            
            for shot in scene.get("shots", []):
                if "mood_tags" not in shot:
                    shot["mood_tags"] = ["neutral"]
                
                if "duration" not in shot:
                    shot["duration"] = 5
        
        # 3. 调整总时长匹配
        total_duration = sum(
            shot.get("duration", 0)
            for scene in script.get("scenes", [])
            for shot in scene.get("shots", [])
        )
        
        target_duration = global_spec.get("duration", 30)
        
        if abs(total_duration - target_duration) > 3:
            # 调整 shot 时长
            scale_factor = target_duration / total_duration
            
            for scene in script.get("scenes", []):
                for shot in scene.get("shots", []):
                    shot["duration"] = round(shot["duration"] * scale_factor, 1)
        
        script["total_duration"] = target_duration
        
        return script
    
    async def revise_script(
        self,
        original_script: Dict[str, Any],
        revision_notes: str
    ) -> Dict[str, Any]:
        """
        基于用户反馈修改剧本
        
        Args:
            original_script: 原始剧本
            revision_notes: 用户修改意见
            
        Returns:
            Dict: 修改后的剧本
        """
        system_prompt = """You are a professional scriptwriter revising a video script based on user feedback.

Task: Revise the script according to user notes while preserving structure and visual feasibility.

Guidelines:
- Address all user concerns
- Maintain JSON structure
- Keep descriptions visual and concrete
- Preserve character consistency
- Ensure AI generation feasibility"""
        
        user_prompt = f"""Revise this script based on user feedback:

ORIGINAL SCRIPT:
{json.dumps(original_script, indent=2)}

USER FEEDBACK:
{revision_notes}

REQUIREMENTS:
- Address all feedback points
- Maintain the same JSON structure
- Keep all shot IDs unchanged
- Ensure visual descriptions remain concrete
- Output ONLY the revised JSON

Provide the revised script now."""
        
        response_format = None
        if self.llm_client.provider == "openai":
            response_format = {"type": "json_object"}
        
        response = await self.llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000,
            response_format=response_format
        )
        
        revised_script = self._parse_json_response(response)
        
        return revised_script
