"""
DNA Manager - DNA Bank管理器

负责：
- Character DNA提取和存储
- Scene DNA管理
- Shot DNA复用检测
- Qdrant Vector DB集成
- Asset Registry更新
"""

from typing import Dict, Any, Optional, List
import numpy as np
from datetime import datetime

from src.infrastructure.blackboard import HierarchicalBlackboard


class DNAManager:
    """DNA Bank管理器"""
    
    def __init__(
        self,
        blackboard: HierarchicalBlackboard,
        qdrant_client=None,  # Qdrant客户端
        collection_name: str = 'face_embeddings'
    ):
        """
        初始化DNA Manager
        
        Args:
            blackboard: 三层黑板实例
            qdrant_client: Qdrant客户端（可选）
            collection_name: Qdrant collection名称
        """
        self.blackboard = blackboard
        self.qdrant = qdrant_client
        self.collection_name = collection_name
    
    # ========== Character DNA管理 ==========
    
    def extract_character_dna(
        self,
        series_id: str,
        character_id: str,
        reference_image_url: str,
        face_embedding: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        提取角色DNA
        
        Args:
            series_id: Series ID
            character_id: 角色ID
            reference_image_url: 参考图URL
            face_embedding: face embedding向量（512维）
            
        Returns:
            Dict: Character DNA
        """
        print(f"[DNAManager] 提取角色DNA: {character_id}")
        
        # 如果未提供embedding，这里应该调用face detection模型提取
        # 简化版：使用随机向量模拟
        if face_embedding is None:
            face_embedding = np.random.rand(512).astype(np.float32)
        
        # 构建Character DNA
        character_dna = {
            'character_id': character_id,
            'series_id': series_id,
            'face_embedding': face_embedding.tolist(),
            'reference_image_url': reference_image_url,
            'appearance_features': {
                'face_shape': 'oval',  # 实际应该从图像提取
                'hair_color': 'unknown',
                'eye_color': 'unknown',
                'distinctive_features': []
            },
            'locked': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 存储到Qdrant Vector DB
        if self.qdrant:
            self._store_face_embedding_to_qdrant(character_dna)
        
        # 更新Series Asset Registry
        self.blackboard.update_character_dna(series_id, character_id, character_dna)
        
        print(f"[DNAManager] 角色DNA已存储: {character_id}")
        
        return character_dna
    
    def _store_face_embedding_to_qdrant(self, character_dna: Dict[str, Any]):
        """存储face embedding到Qdrant"""
        try:
            from qdrant_client.models import PointStruct
            
            point = PointStruct(
                id=character_dna['character_id'],
                vector=character_dna['face_embedding'],
                payload={
                    'character_id': character_dna['character_id'],
                    'series_id': character_dna['series_id'],
                    'reference_image_url': character_dna['reference_image_url'],
                    'created_at': character_dna['created_at']
                }
            )
            
            self.qdrant.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"[DNAManager] Face embedding已存入Qdrant")
            
        except Exception as e:
            print(f"[DNAManager] Qdrant存储失败: {e}")
    
    def search_similar_faces(
        self,
        query_embedding: np.ndarray,
        series_id: Optional[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        搜索相似面孔
        
        Args:
            query_embedding: 查询embedding
            series_id: 限定Series（可选）
            limit: 返回数量
            
        Returns:
            List[Dict]: 相似角色列表
        """
        if not self.qdrant:
            print("[DNAManager] Qdrant未配置，无法搜索")
            return []
        
        try:
            # 构建过滤条件
            filter_conditions = None
            if series_id:
                from qdrant_client.models import Filter, FieldCondition, MatchValue
                filter_conditions = Filter(
                    must=[
                        FieldCondition(
                            key='series_id',
                            match=MatchValue(value=series_id)
                        )
                    ]
                )
            
            # 搜索
            results = self.qdrant.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=filter_conditions,
                limit=limit
            )
            
            similar_faces = []
            for result in results:
                similar_faces.append({
                    'character_id': result.payload['character_id'],
                    'series_id': result.payload['series_id'],
                    'similarity_score': result.score,
                    'reference_image_url': result.payload.get('reference_image_url')
                })
            
            return similar_faces
            
        except Exception as e:
            print(f"[DNAManager] 搜索失败: {e}")
            return []
    
    def get_character_dna(
        self,
        series_id: str,
        character_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        获取角色DNA
        
        Args:
            series_id: Series ID
            character_id: 角色ID
            
        Returns:
            Dict: Character DNA或None
        """
        asset_registry = self.blackboard.get_asset_registry(series_id)
        characters = asset_registry.get('characters', {})
        return characters.get(character_id)
    
    def lock_character_dna(self, series_id: str, character_id: str):
        """
        锁定角色DNA（后续必须复用）
        
        Args:
            series_id: Series ID
            character_id: 角色ID
        """
        character_dna = self.get_character_dna(series_id, character_id)
        if character_dna:
            character_dna['locked'] = True
            character_dna['updated_at'] = datetime.now().isoformat()
            self.blackboard.update_character_dna(series_id, character_id, character_dna)
            print(f"[DNAManager] 角色DNA已锁定: {character_id}")
    
    # ========== Scene DNA管理 ==========
    
    def extract_scene_dna(
        self,
        series_id: str,
        scene_id: str,
        reference_image_url: str,
        scene_description: str
    ) -> Dict[str, Any]:
        """
        提取场景DNA
        
        Args:
            series_id: Series ID
            scene_id: 场景ID
            reference_image_url: 参考图URL
            scene_description: 场景描述
            
        Returns:
            Dict: Scene DNA
        """
        print(f"[DNAManager] 提取场景DNA: {scene_id}")
        
        # 场景DNA包含：位置、光照、色调、氛围等
        scene_dna = {
            'scene_id': scene_id,
            'series_id': series_id,
            'reference_image_url': reference_image_url,
            'description': scene_description,
            'visual_features': {
                'dominant_colors': [],  # 主色调（实际应从图像提取）
                'lighting_type': 'unknown',  # 光照类型
                'time_of_day': 'unknown',
                'weather': 'unknown',
                'atmosphere': 'neutral'
            },
            'layout': {
                'type': 'unknown',  # indoor/outdoor
                'key_objects': [],  # 关键物体
                'spatial_layout': 'unknown'
            },
            'locked': False,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # 更新Series Asset Registry
        self.blackboard.update_scene_dna(series_id, scene_id, scene_dna)
        
        print(f"[DNAManager] 场景DNA已存储: {scene_id}")
        
        return scene_dna
    
    def get_scene_dna(
        self,
        series_id: str,
        scene_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取场景DNA"""
        asset_registry = self.blackboard.get_asset_registry(series_id)
        scenes = asset_registry.get('scenes', {})
        return scenes.get(scene_id)
    
    # ========== Shot DNA复用检测 ==========
    
    def find_reusable_shot(
        self,
        series_id: str,
        shot_spec: Dict[str, Any],
        min_similarity: float = 0.85
    ) -> Optional[Dict[str, Any]]:
        """
        查找可复用的Shot DNA
        
        Args:
            series_id: Series ID
            shot_spec: Shot规格
            min_similarity: 最小相似度阈值
            
        Returns:
            Dict: 可复用的Shot DNA或None
        """
        # 简化版：检查是否有完全相同的shot_spec
        # 实际应该使用embedding相似度匹配
        
        asset_registry = self.blackboard.get_asset_registry(series_id)
        shots = asset_registry.get('shots', {})
        
        # 提取关键特征进行匹配
        query_features = self._extract_shot_features(shot_spec)
        
        best_match = None
        best_score = 0.0
        
        for shot_id, shot_dna in shots.items():
            if shot_dna.get('locked', False):  # 只考虑锁定的DNA
                candidate_features = self._extract_shot_features(
                    shot_dna.get('shot_spec', {})
                )
                
                similarity = self._calculate_feature_similarity(
                    query_features,
                    candidate_features
                )
                
                if similarity > best_score and similarity >= min_similarity:
                    best_score = similarity
                    best_match = {
                        'shot_id': shot_id,
                        'shot_dna': shot_dna,
                        'similarity': similarity
                    }
        
        if best_match:
            print(f"[DNAManager] 找到可复用Shot: {best_match['shot_id']} (相似度: {best_score:.2f})")
        
        return best_match
    
    def _extract_shot_features(self, shot_spec: Dict[str, Any]) -> Dict[str, Any]:
        """提取Shot特征"""
        return {
            'action': shot_spec.get('action', ''),
            'location': shot_spec.get('location', ''),
            'timeOfDay': shot_spec.get('timeOfDay', ''),
            'shotType': shot_spec.get('camera', {}).get('shotType', ''),
            'characters': set(shot_spec.get('characters', []))
        }
    
    def _calculate_feature_similarity(
        self,
        features1: Dict[str, Any],
        features2: Dict[str, Any]
    ) -> float:
        """计算特征相似度（简化版）"""
        score = 0.0
        total_weight = 0.0
        
        # 地点匹配（权重0.3）
        if features1['location'] == features2['location']:
            score += 0.3
        total_weight += 0.3
        
        # 时间匹配（权重0.2）
        if features1['timeOfDay'] == features2['timeOfDay']:
            score += 0.2
        total_weight += 0.2
        
        # 镜头类型匹配（权重0.2）
        if features1['shotType'] == features2['shotType']:
            score += 0.2
        total_weight += 0.2
        
        # 角色匹配（权重0.3）
        chars1 = features1['characters']
        chars2 = features2['characters']
        if chars1 and chars2:
            intersection = len(chars1 & chars2)
            union = len(chars1 | chars2)
            char_similarity = intersection / union if union > 0 else 0
            score += 0.3 * char_similarity
        total_weight += 0.3
        
        return score / total_weight if total_weight > 0 else 0.0
    
    # ========== 统计和报告 ==========
    
    def get_dna_bank_statistics(self, series_id: str) -> Dict[str, Any]:
        """
        获取DNA Bank统计
        
        Args:
            series_id: Series ID
            
        Returns:
            Dict: 统计信息
        """
        asset_registry = self.blackboard.get_asset_registry(series_id)
        
        characters = asset_registry.get('characters', {})
        scenes = asset_registry.get('scenes', {})
        shots = asset_registry.get('shots', {})
        locked_assets = asset_registry.get('lockedAssets', [])
        
        return {
            'series_id': series_id,
            'total_characters': len(characters),
            'total_scenes': len(scenes),
            'total_shots': len(shots),
            'locked_assets': len(locked_assets),
            'characters_breakdown': {
                'locked': sum(1 for c in characters.values() if c.get('locked', False)),
                'unlocked': sum(1 for c in characters.values() if not c.get('locked', False))
            },
            'scene_breakdown': {
                'locked': sum(1 for s in scenes.values() if s.get('locked', False)),
                'unlocked': sum(1 for s in scenes.values() if not s.get('locked', False))
            }
        }
