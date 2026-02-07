"""
Writers Room Coordinator - Writers Room协调器

负责协调4个Writers Room Agents的工作流：
1. Showrunner - 创建Series并设置风格指南
2. Bible Architect - 构建完整Series Bible
3. Story Architect - 规划整体故事结构
4. Episode Writer - 创作各集Script和Storyboard

实现端到端的多集剧集创作流程
"""

from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime

from src.infrastructure.event_bus import EventBus
from src.infrastructure.blackboard import HierarchicalBlackboard
from src.model_gateway import ModelGateway

from src.agents.cognitive.showrunner import ShowrunnerAgent
from src.agents.cognitive.bible_architect import BibleArchitectAgent
from src.agents.cognitive.story_architect import StoryArchitectAgent
from src.agents.cognitive.episode_writer import EpisodeWriterAgent


class WritersRoomCoordinator:
    """Writers Room协调器 - 协调4个Writers Room Agents的协作"""
    
    def __init__(
        self,
        blackboard: HierarchicalBlackboard,
        event_bus: EventBus,
        model_gateway: ModelGateway
    ):
        """
        初始化Writers Room Coordinator
        
        Args:
            blackboard: 三层黑板实例
            event_bus: 事件总线实例
            model_gateway: 模型网关实例
        """
        self.blackboard = blackboard
        self.event_bus = event_bus
        self.model_gateway = model_gateway
        
        # 初始化4个Writers Room Agents
        self.showrunner = ShowrunnerAgent(blackboard, event_bus, model_gateway)
        self.bible_architect = BibleArchitectAgent(blackboard, event_bus, model_gateway)
        self.story_architect = StoryArchitectAgent(blackboard, event_bus, model_gateway)
        self.episode_writer = EpisodeWriterAgent(blackboard, event_bus, model_gateway)
        
        print("[WritersRoom] Writers Room初始化完成")
        print("  - Showrunner: ✅")
        print("  - Bible Architect: ✅")
        print("  - Story Architect: ✅")
        print("  - Episode Writer: ✅")
    
    def create_series(
        self,
        user_input: str,
        series_spec: Dict[str, Any],
        total_budget: float = 1000.0
    ) -> Dict[str, Any]:
        """
        创建Series（完整流程）
        
        执行Writer's Room的完整工作流：
        1. Showrunner创建Series
        2. Bible Architect构建Bible
        3. Story Architect规划整体结构
        
        Args:
            user_input: 用户输入的剧集描述
            series_spec: Series规格
            total_budget: 总预算
            
        Returns:
            Dict: Series创建结果
        """
        print("\n" + "="*60)
        print("🎬 Writers Room: 开始创作新剧集")
        print("="*60)
        
        # Step 1: Showrunner创建Series
        print("\n[Step 1/3] Showrunner: 创建Series并设置风格指南...")
        
        showrunner_result = self.showrunner.handle_series_creation({
            'user_input': user_input,
            'series_spec': series_spec,
            'total_budget': total_budget
        })
        
        if not showrunner_result.get('success'):
            print("❌ Showrunner失败")
            return showrunner_result
        
        series_id = showrunner_result['series_id']
        print(f"✅ Series创建成功: {series_id}")
        
        # Step 2: Bible Architect构建Bible
        print("\n[Step 2/3] Bible Architect: 构建Series Bible...")
        
        # 模拟BIBLE_CREATED事件的payload
        bible_payload = {
            'series_id': series_id,
            'bible': showrunner_result['series'].get('show_bible', {})
        }
        
        bible_result = self.bible_architect.handle_series_bible_creation(bible_payload)
        
        if not bible_result.get('success'):
            print("❌ Bible Architect失败")
            return bible_result
        
        print(f"✅ Series Bible创建完成")
        
        # Step 3: Story Architect规划整体结构
        print("\n[Step 3/3] Story Architect: 规划整体故事结构...")
        
        story_payload = {
            'series_id': series_id,
            'bible': bible_result['bible']
        }
        
        story_result = self.story_architect.handle_series_outline_planning(story_payload)
        
        if not story_result.get('success'):
            print("❌ Story Architect失败")
            return story_result
        
        print(f"✅ 整体故事结构规划完成")
        
        print("\n" + "="*60)
        print("🎉 Writers Room: Series创建完成！")
        print("="*60)
        
        return {
            'success': True,
            'series_id': series_id,
            'series': self.blackboard.get_series(series_id),
            'character_arcs': story_result['character_arcs'],
            'plot_rhythm': story_result['plot_rhythm'],
            'episode_themes': story_result['episode_themes']
        }
    
    def create_episode(
        self,
        series_id: str,
        episode_number: int,
        custom_outline: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        创建单集Episode（完整流程）
        
        执行Episode创作的完整工作流：
        1. 创建Episode记录
        2. Story Architect生成Outline（或使用custom_outline）
        3. Episode Writer生成Script
        4. Episode Writer生成Storyboard
        
        Args:
            series_id: Series ID
            episode_number: Episode编号
            custom_outline: 自定义Outline（可选）
            
        Returns:
            Dict: Episode创建结果
        """
        print("\n" + "="*60)
        print(f"📝 Writers Room: 开始创作第{episode_number}集")
        print("="*60)
        
        # Step 1: 创建Episode记录
        print(f"\n[Step 1/4] 创建Episode记录...")
        
        series = self.blackboard.get_series(series_id)
        series_spec = series.get('series_spec', {})
        series_budget = series.get('series_budget', {})
        per_episode_cap = series_budget.get('perEpisodeCap', 100.0)
        
        episode_id = f"{series_id}-EP{episode_number:03d}"
        
        episode = self.blackboard.create_episode(
            episode_id=episode_id,
            episode_number=episode_number,
            series_id=series_id,
            episode_budget={
                'allocated': per_episode_cap,
                'used': 0.0,
                'predicted': per_episode_cap * 0.8
            }
        )
        
        print(f"✅ Episode记录创建: {episode_id}")
        
        # Step 2: Story Architect生成Outline（如果未提供）
        if not custom_outline:
            print(f"\n[Step 2/4] Story Architect: 生成Episode Outline...")
            
            outline_result = self.story_architect.handle_episode_outline_creation({
                'series_id': series_id,
                'episode_id': episode_id,
                'episode_number': episode_number
            })
            
            if not outline_result.get('success'):
                print("❌ Outline生成失败")
                return outline_result
            
            outline = outline_result['outline']
            print(f"✅ Outline生成完成")
        else:
            outline = custom_outline
            self.blackboard.update_outline(episode_id, outline)
            print(f"✅ 使用自定义Outline")
        
        # Step 3: Episode Writer生成Script
        print(f"\n[Step 3/4] Episode Writer: 生成Script...")
        
        script_result = self.episode_writer.handle_script_generation({
            'series_id': series_id,
            'episode_id': episode_id,
            'episode_number': episode_number,
            'outline': outline
        })
        
        if not script_result.get('success'):
            print("❌ Script生成失败")
            return script_result
        
        script = script_result['script']
        print(f"✅ Script生成完成: {len(script.get('scenes', []))}个场景")
        
        # Step 4: Episode Writer生成Storyboard
        print(f"\n[Step 4/4] Episode Writer: 生成Storyboard...")
        
        storyboard_result = self.episode_writer.handle_storyboard_generation({
            'series_id': series_id,
            'episode_id': episode_id,
            'episode_number': episode_number,
            'script': script
        })
        
        if not storyboard_result.get('success'):
            print("❌ Storyboard生成失败")
            return storyboard_result
        
        storyboard = storyboard_result['storyboard']
        print(f"✅ Storyboard生成完成: {storyboard['totalShots']}个镜头")
        
        print("\n" + "="*60)
        print(f"🎉 Writers Room: 第{episode_number}集创作完成！")
        print("="*60)
        
        return {
            'success': True,
            'episode_id': episode_id,
            'episode_number': episode_number,
            'outline': outline,
            'script': script,
            'storyboard': storyboard
        }
    
    def create_multi_episode_series(
        self,
        user_input: str,
        series_spec: Dict[str, Any],
        num_episodes: int = 3,
        total_budget: float = 1000.0
    ) -> Dict[str, Any]:
        """
        创建多集Series（端到端完整流程）
        
        这是Writers Room的完整演示：
        1. 创建Series（Showrunner → Bible Architect → Story Architect）
        2. 创建多个Episodes（Story Architect → Episode Writer）
        
        Args:
            user_input: 用户输入
            series_spec: Series规格
            num_episodes: 创建的集数
            total_budget: 总预算
            
        Returns:
            Dict: 完整创作结果
        """
        print("\n" + "🌟"*30)
        print(f"🎬 Writers Room: 启动{num_episodes}集剧集创作流程")
        print("🌟"*30)
        
        start_time = datetime.now()
        
        # Phase 1: 创建Series
        series_result = self.create_series(
            user_input=user_input,
            series_spec=series_spec,
            total_budget=total_budget
        )
        
        if not series_result.get('success'):
            return series_result
        
        series_id = series_result['series_id']
        
        # Phase 2: 创建多个Episodes
        episodes = []
        
        for ep_num in range(1, num_episodes + 1):
            print(f"\n{'─'*60}")
            print(f"正在创作第 {ep_num}/{num_episodes} 集...")
            print(f"{'─'*60}")
            
            episode_result = self.create_episode(
                series_id=series_id,
                episode_number=ep_num
            )
            
            if episode_result.get('success'):
                episodes.append(episode_result)
            else:
                print(f"⚠️  第{ep_num}集创作失败，跳过")
        
        # 统计
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        total_shots = sum(ep.get('storyboard', {}).get('totalShots', 0) for ep in episodes)
        total_scenes = sum(len(ep.get('script', {}).get('scenes', [])) for ep in episodes)
        
        print("\n" + "🌟"*30)
        print("🎉 Writers Room: 多集剧集创作完成！")
        print("🌟"*30)
        print(f"\n📊 创作统计:")
        print(f"  - Series ID: {series_id}")
        print(f"  - 成功创作集数: {len(episodes)}/{num_episodes}")
        print(f"  - 总场景数: {total_scenes}")
        print(f"  - 总镜头数: {total_shots}")
        print(f"  - 耗时: {duration:.1f}秒")
        print()
        
        return {
            'success': True,
            'series_id': series_id,
            'series': series_result['series'],
            'episodes': episodes,
            'statistics': {
                'num_episodes_created': len(episodes),
                'total_scenes': total_scenes,
                'total_shots': total_shots,
                'duration_seconds': duration
            }
        }
    
    def get_series_summary(self, series_id: str) -> Dict[str, Any]:
        """
        获取Series完整摘要
        
        Args:
            series_id: Series ID
            
        Returns:
            Dict: Series摘要信息
        """
        series = self.blackboard.get_series(series_id)
        episodes = self.blackboard.get_all_episodes(series_id)
        
        total_shots = 0
        total_scenes = 0
        
        for ep in episodes:
            ep_full = self.blackboard.get_episode(ep['episode_id'])
            script = ep_full.get('script', {})
            storyboard = ep_full.get('storyboard', {})
            
            total_scenes += len(script.get('scenes', []))
            total_shots += storyboard.get('totalShots', 0)
        
        bible = series.get('show_bible', {})
        
        return {
            'series_id': series_id,
            'title': series.get('series_spec', {}).get('title', ''),
            'status': series.get('status', ''),
            'total_episodes': len(episodes),
            'total_scenes': total_scenes,
            'total_shots': total_shots,
            'bible_summary': {
                'characters': len(bible.get('characters', [])),
                'world_rules': len(bible.get('worldRules', [])),
                'themes': bible.get('themes', [])
            },
            'budget': series.get('series_budget', {}),
            'created_at': series.get('created_at'),
            'updated_at': series.get('updated_at')
        }
