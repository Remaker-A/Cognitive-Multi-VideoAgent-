"""
Episode Writer Agent - 单集编剧

负责：
- 将Outline转换为详细Script
- 场景（Scene）创作
- 对话（Dialogue）生成
- 分镜（Storyboard）生成
- Bible一致性检查
"""

from typing import Dict, Any, Optional, List
import json
from datetime import datetime

from src.infrastructure.event_bus import EventBus
from src.infrastructure.blackboard import HierarchicalBlackboard
from src.model_gateway import ModelGateway


class EpisodeWriterAgentContract:
    """Episode Writer Agent合约"""
    
    # 读权限
    READ_PERMISSIONS = [
        'series.series_spec',
        'series.show_bible',
        'episode.outline',
        'episode.script',
        'episode.storyboard'
    ]
    
    # 写权限
    WRITE_PERMISSIONS = [
        'episode.script',
        'episode.script.scenes',
        'episode.storyboard',
        'episode.storyboard.shots',
        'episode.status'
    ]
    
    # 触发事件
    TRIGGERS = [
        'EPISODE_OUTLINE_CREATED',
        'SCRIPT_GENERATION_REQUEST',
        'STORYBOARD_GENERATION_REQUEST'
    ]
    
    # 发布事件
    PUBLISHES = [
        'SCRIPT_CREATED',
        'SCENE_WRITTEN',
        'STORYBOARD_CREATED',
        'DIALOGUE_GENERATED',
        'BIBLE_CONSISTENCY_CHECK_REQUESTED'
    ]
    
    # Fallback策略
    FALLBACK_STRATEGIES = [
        {
            'trigger': 'LLM_GENERATION_FAILURE',
            'action': 'USE_TEMPLATE_SCENES',
            'description': '使用场景模板'
        },
        {
            'trigger': 'DIALOGUE_GENERATION_FAILURE',
            'action': 'USE_SIMPLE_DIALOGUE',
            'description': '使用简化对话'
        }
    ]
    
    # 依赖
    DEPENDENCIES = [
        'ModelGateway',
        'HierarchicalBlackboard',
        'EventBus',
        'StoryArchitectAgent',
        'BibleArchitectAgent'
    ]


class EpisodeWriterAgent:
    """Episode Writer Agent - 单集编剧"""
    
    def __init__(
        self,
        blackboard: HierarchicalBlackboard,
        event_bus: EventBus,
        model_gateway: ModelGateway
    ):
        """初始化Episode Writer Agent"""
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.model_gateway = model_gateway
        self.contract = EpisodeWriterAgentContract()
        
        # 订阅触发事件
        for trigger in self.contract.TRIGGERS:
            self.event_bus.subscribe(trigger, self._handle_event)
    
    def _handle_event(self, event: Dict[str, Any]):
        """处理触发事件"""
        event_type = event.get('type')
        
        if event_type == 'EPISODE_OUTLINE_CREATED':
            self.handle_script_generation(event.get('payload', {}))
        elif event_type == 'SCRIPT_GENERATION_REQUEST':
            self.handle_script_generation(event.get('payload', {}))
        elif event_type == 'STORYBOARD_GENERATION_REQUEST':
            self.handle_storyboard_generation(event.get('payload', {}))
    
    def handle_script_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理Script生成
        
        将Outline转换为详细的Scene Script
        
        Args:
            payload: Script生成请求
                - series_id: Series ID
                - episode_id: Episode ID
                - outline: Episode Outline
                
        Returns:
            Dict: Script生成结果
        """
        series_id = payload.get('series_id')
        episode_id = payload.get('episode_id')
        episode_number = payload.get('episode_number', 1)
        
        print(f"[EpisodeWriter] 为Episode {episode_number} 生成Script...")
        
        # 1. 获取上下文
        series = self.blackboard.get_series(series_id)
        episode = self.blackboard.get_episode(episode_id)
        
        bible = series.get('show_bible', {})
        outline = episode.get('outline', payload.get('outline', {}))
        series_spec = series.get('series_spec', {})
        
        # 2. 生成Scenes
        scenes = self._generate_scenes_from_outline(
            outline,
            bible,
            series_spec,
            episode_number
        )
        
        # 3. 为每个Scene生成对话
        for scene in scenes:
            scene['dialogue'] = self._generate_dialogue_for_scene(
                scene,
                bible,
                series_spec
            )
        
        # 4. 计算总时长
        total_duration = sum(scene.get('estimatedDuration', 0) for scene in scenes)
        
        # 5. 构建Script
        script = {
            'scenes': scenes,
            'totalDuration': total_duration,
            'status': 'draft',
            'version': 1,
            'createdBy': 'EpisodeWriter',
            'createdAt': datetime.now().isoformat()
        }
        
        # 6. 一致性检查
        consistency_check = self._check_bible_consistency(script, bible)
        if not consistency_check['consistent']:
            print(f"[EpisodeWriter] ⚠️  检测到{len(consistency_check['violations'])}个一致性问题")
            script['consistencyIssues'] = consistency_check['violations']
        
        # 7. 更新Episode Blackboard
        self.blackboard.update_script(episode_id, script)
        
        print(f"[EpisodeWriter] Script生成完成")
        print(f"  - 场景数: {len(scenes)}")
        print(f"  - 总时长: {total_duration}秒")
        print(f"  - 一致性: {'✅ 通过' if consistency_check['consistent'] else '⚠️  有问题'}")
        
        # 8. 发布事件
        self.event_bus.publish({
            'type': 'SCRIPT_CREATED',
            'payload': {
                'series_id': series_id,
                'episode_id': episode_id,
                'episode_number': episode_number,
                'script': script,
                'consistency_check': consistency_check
            },
            'timestamp': datetime.now().isoformat(),
            'actor': 'EpisodeWriterAgent'
        })
        
        return {'success': True, 'script': script}
    
    def _generate_scenes_from_outline(
        self,
        outline: Dict[str, Any],
        bible: Dict[str, Any],
        series_spec: Dict[str, Any],
        episode_number: int
    ) -> List[Dict[str, Any]]:
        """
        从Outline生成Scenes
        
        使用LLM将plotPoints扩展为详细场景
        """
        plot_points = outline.get('plotPoints', [])
        core_conflict = outline.get('coreConflict', '')
        character_arcs = outline.get('characterArcs', {})
        tone = bible.get('toneGuidelines', '')
        
        if not plot_points:
            print(f"[EpisodeWriter] Outline缺少plotPoints，使用默认场景")
            return self._get_default_scenes()
        
        scenes = []
        
        for idx, plot_point in enumerate(plot_points):
            scene_number = idx + 1
            
            prompt = f"""作为编剧，将以下情节点扩展为详细场景：

**情节点 {scene_number}**: {plot_point.get('description', '')}
**地点**: {plot_point.get('location', '未指定')}

剧集上下文：
- 整体语气：{tone}
- 核心冲突：{core_conflict}

请创建包含以下元素的场景描述：
1. **场景描述**（50-100字）- 视觉画面和氛围
2. **关键动作**（2-3个）- 角色的具体行为
3. **情感基调** - 本场景的情绪氛围

用JSON格式返回：
{{
  "sceneId": "scene-{episode_number:02d}-{scene_number:02d}",
  "sceneNumber": {scene_number},
  "location": "地点",
  "timeOfDay": "白天/夜晚/黄昏",
  "description": "场景描述",
  "actions": ["动作1", "动作2"],
  "emotionalTone": "情感基调",
  "estimatedDuration": 30
}}"""

            try:
                response = self.model_gateway.call_llm(
                    model='gpt-4-turbo-preview',
                    messages=[
                        {'role': 'system', 'content': '你是一位专业编剧。只返回JSON。'},
                        {'role': 'user', 'content': prompt}
                    ],
                    temperature=0.8,
                    max_tokens=400,
                    response_format={"type": "json_object"}
                )
                
                content = response.get('content', '').strip()
                scene = json.loads(content)
                
                # 添加原始plotPoint信息
                scene['plotPoint'] = plot_point
                scenes.append(scene)
                
            except Exception as e:
                print(f"[EpisodeWriter] Scene {scene_number}生成失败: {e}")
                # Fallback: 使用简化场景
                scenes.append({
                    'sceneId': f"scene-{episode_number:02d}-{scene_number:02d}",
                    'sceneNumber': scene_number,
                    'location': plot_point.get('location', '未指定'),
                    'timeOfDay': '白天',
                    'description': plot_point.get('description', ''),
                    'actions': ['待定'],
                    'emotionalTone': '中性',
                    'estimatedDuration': 30,
                    'plotPoint': plot_point
                })
        
        return scenes
    
    def _get_default_scenes(self) -> List[Dict[str, Any]]:
        """默认场景模板"""
        return [
            {
                'sceneId': 'scene-01-01',
                'sceneNumber': 1,
                'location': '主场景',
                'timeOfDay': '白天',
                'description': '开场场景',
                'actions': ['建立情境'],
                'emotionalTone': '平和',
                'estimatedDuration': 30
            }
        ]
    
    def _generate_dialogue_for_scene(
        self,
        scene: Dict[str, Any],
        bible: Dict[str, Any],
        series_spec: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        为场景生成对话
        
        Args:
            scene: 场景信息
            bible: Series Bible
            series_spec: Series规格
            
        Returns:
            List[Dict]: 对话列表
        """
        # 简化版：生成基础对话结构
        # 实际应该根据场景动作和角色性格生成
        
        characters = bible.get('characters', [])
        if not characters:
            return []
        
        # 为场景中的主要动作生成对话
        dialogues = []
        actions = scene.get('actions', [])
        
        for idx, action in enumerate(actions[:2]):  # 最多2段对话
            if characters:
                char = characters[idx % len(characters)]
                dialogues.append({
                    'lineNumber': idx + 1,
                    'character': char['name'],
                    'text': f"（关于{action}的对话）",
                    'emotion': scene.get('emotionalTone', '中性'),
                    'action': action
                })
        
        return dialogues
    
    def _check_bible_consistency(
        self,
        script: Dict[str, Any],
        bible: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        检查Script与Bible的一致性
        
        Args:
            script: 剧本
            bible: Series Bible
            
        Returns:
            Dict: 一致性检查结果
        """
        violations = []
        
        # 1. 检查角色一致性
        bible_characters = {c['name']: c for c in bible.get('characters', [])}
        
        for scene in script.get('scenes', []):
            for dialogue in scene.get('dialogue', []):
                char_name = dialogue.get('character', '')
                if char_name and char_name not in bible_characters:
                    violations.append({
                        'type': 'UNKNOWN_CHARACTER',
                        'scene': scene['sceneId'],
                        'character': char_name,
                        'message': f'角色{char_name}未在Bible中定义'
                    })
        
        # 2. 检查禁忌
        taboos = bible.get('taboos', [])
        script_text = json.dumps(script, ensure_ascii=False).lower()
        
        for taboo in taboos:
            taboo_keywords = taboo.lower().split()
            for keyword in taboo_keywords:
                if keyword in script_text and len(keyword) > 3:
                    violations.append({
                        'type': 'TABOO_VIOLATION',
                        'taboo': taboo,
                        'message': f'可能违反禁忌: {taboo}'
                    })
                    break
        
        # 3. 发布一致性检查请求事件（供BibleArchitect深度检查）
        if violations:
            self.event_bus.publish({
                'type': 'BIBLE_CONSISTENCY_CHECK_REQUESTED',
                'payload': {
                    'content': script,
                    'content_type': 'script',
                    'preliminary_violations': violations
                },
                'timestamp': datetime.now().isoformat(),
                'actor': 'EpisodeWriterAgent'
            })
        
        return {
            'consistent': len(violations) == 0,
            'violations': violations
        }
    
    def handle_storyboard_generation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理Storyboard生成
        
        将Script转换为Storyboard(Shot级别规划)
        
        Args:
            payload: Storyboard生成请求
                - series_id: Series ID
                - episode_id: Episode ID
                - script: Script数据
                
        Returns:
            Dict: Storyboard生成结果
        """
        series_id = payload.get('series_id')
        episode_id = payload.get('episode_id')
        episode_number = payload.get('episode_number', 1)
        
        print(f"[EpisodeWriter] 为Episode {episode_number} 生成Storyboard...")
        
        # 1. 获取Script和Outline
        episode = self.blackboard.get_episode(episode_id)
        script = episode.get('script', payload.get('script', {}))
        outline = episode.get('outline', {})
        
        if not script or not script.get('scenes'):
            print(f"[EpisodeWriter] Script为空,无法生成Storyboard")
            return {'success': False, 'reason': 'Script为空'}
        
        # 2. 获取分镜数约束
        target_shot_count = outline.get('target_shot_count', 0)
        shot_allocation = outline.get('plot_point_shot_allocation', {})
        
        # 3. 为每个Scene生成Shots(带约束)
        all_shots = []
        shot_counter = 1
        
        for idx, scene in enumerate(script.get('scenes', [])):
            # 获取该scene对应的分镜数约束
            target_shots_for_scene = shot_allocation.get(f"plot_point_{idx + 1}", 0)
            
            scene_shots = self._generate_shots_for_scene(
                scene,
                shot_counter,
                episode_number,
                target_shot_count=target_shots_for_scene  # 新增参数
            )
            all_shots.extend(scene_shots)
            shot_counter += len(scene_shots)
        
        # 4. 构建Storyboard
        actual_shot_count = len(all_shots)
        deviation = actual_shot_count - target_shot_count if target_shot_count > 0 else 0
        
        storyboard = {
            'shots': all_shots,
            'totalShots': actual_shot_count,
            'target_shot_count': target_shot_count,  # 新增
            'shot_count_deviation': deviation,  # 新增
            'totalDuration': sum(shot.get('duration', 0) for shot in all_shots),
            'status': 'draft',
            'version': 1,
            'createdBy': 'EpisodeWriter',
            'createdAt': datetime.now().isoformat()
        }
        
        # 5. 验证分镜数偏差
        if target_shot_count > 0:
            deviation_rate = abs(deviation) / target_shot_count
            if deviation_rate > 0.2:
                warning_msg = f"⚠️ 分镜数偏差较大: 目标{target_shot_count} vs 实际{actual_shot_count} (偏差{deviation_rate:.1%})"
                print(f"[EpisodeWriter] {warning_msg}")
                storyboard['adjustment_reason'] = "based on scene complexity"
            else:
                print(f"[EpisodeWriter] ✅ 分镜数符合预期: 目标{target_shot_count} vs 实际{actual_shot_count}")
        
        # 6. 更新Episode Blackboard
        self.blackboard.update_storyboard(episode_id, storyboard)
        
        print(f"[EpisodeWriter] Storyboard生成完成")
        print(f"  - 总镜头数: {len(all_shots)}")
        print(f"  - 总时长: {storyboard['totalDuration']}秒")
        
        # 7. 发布事件
        self.event_bus.publish({
            'type': 'STORYBOARD_CREATED',
            'payload': {
                'series_id': series_id,
                'episode_id': episode_id,
                'episode_number': episode_number,
                'storyboard': storyboard
            },
            'timestamp': datetime.now().isoformat(),
            'actor': 'EpisodeWriterAgent'
        })
        
        return {'success': True, 'storyboard': storyboard}
    
    def _generate_shots_for_scene(
        self,
        scene: Dict[str, Any],
        start_shot_number: int,
        episode_number: int,
        target_shot_count: int = 0  # 新增参数: 目标分镜数约束
    ) -> List[Dict[str, Any]]:
        """
        为Scene生成Shots
        
        将场景分解为多个镜头,参考目标分镜数约束
        
        Args:
            scene: 场景信息
            start_shot_number: 起始镜头编号
            episode_number: Episode编号
            target_shot_count: 目标分镜数(来自Outline的分配)
        
        Returns:
            List[Dict]: 生成的镜头列表
        """
        shots = []
        scene_id = scene.get('sceneId', 'scene-unknown')
        scene_duration = scene.get('estimatedDuration', 30)
        actions = scene.get('actions', [])
        num_actions = len(actions)
        
        # 智能决定分镜数
        if target_shot_count > 0:
            # 优先使用目标分镜数
            num_shots = target_shot_count
        elif num_actions > 0:
            # 退化到原逻辑: 每个action一个shot
            num_shots = num_actions
        else:
            # 默认1个establishing shot
            num_shots = 1
            actions = ['establishing shot']
        
        # 确保至少有1个镜头
        num_shots = max(num_shots, 1)
        
        # 生成shots
        shot_duration = scene_duration / num_shots if num_shots > 0 else scene_duration
        
        for idx in range(num_shots):
            shot_number = start_shot_number + idx
            
            # 智能分配action
            if num_actions > 0:
                if idx < num_actions:
                    action = actions[idx]
                else:
                    # 镜头数多于action数,复用最后一个action或使用连续动作
                    action = actions[-1] if actions else "continuing action"
            else:
                action = "establishing shot" if idx == 0 else "continuation"
            
            shot = {
                'shotId': f"shot-{episode_number:02d}-{shot_number:03d}",
                'shotNumber': shot_number,
                'sceneId': scene_id,
                'duration': int(shot_duration),
                'shotType': self._determine_shot_type(idx, num_shots),
                'camera': {
                    'angle': 'eye_level',
                    'movement': 'static',
                    'lens': '35mm'
                },
                'action': action,
                'location': scene.get('location', ''),
                'timeOfDay': scene.get('timeOfDay', '白天'),
                'characters': [],  # 待填充
                'description': f"{action} at {scene.get('location', '')}"
            }
            
            shots.append(shot)
        
        return shots
    
    def _determine_shot_type(self, shot_index: int, total_shots: int) -> str:
        """确定镜头类型"""
        if shot_index == 0:
            return 'wide'  # 第一个镜头用wide shot建立场景
        elif shot_index == total_shots - 1:
            return 'medium'  # 最后一个镜头用medium shot
        else:
            return 'close_up'  # 中间镜头用close_up突出细节
