#!/usr/bin/env python3
"""
Qdrant Vector DB 初始化脚本

创建face_embeddings集合用于存储角色面部特征向量
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, CollectionStatus

load_dotenv()


def init_qdrant():
    """初始化Qdrant集合"""
    print("正在连接Qdrant...")
    
    client = QdrantClient(
        host=os.getenv('QDRANT_HOST', 'localhost'),
        port=int(os.getenv('QDRANT_PORT', 6333))
    )
    
    collection_name = os.getenv('QDRANT_COLLECTION_NAME', 'face_embeddings')
    
    # 检查集合是否已存在
    try:
        collection_info = client.get_collection(collection_name)
        print(f"✅ 集合 '{collection_name}' 已存在")
        print(f"   向量维度: {collection_info.config.params.vectors.size}")
        print(f"   距离度量: {collection_info.config.params.vectors.distance}")
        print(f"   向量数量: {collection_info.points_count}")
        return
    except Exception:
        pass
    
    # 创建集合
    print(f"创建集合 '{collection_name}'...")
    
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=512,  # CLIP face embedding维度
            distance=Distance.COSINE  # 余弦相似度
        )
    )
    
    print(f"✅ 集合 '{collection_name}' 创建成功！")
    print(f"   向量维度: 512")
    print(f"   距离度量: COSINE")
    print()
    print("💡 现在可以使用该集合存储face embeddings:")
    print(f"""
    from qdrant_client import QdrantClient
    from qdrant_client.models import PointStruct
    
    client = QdrantClient(host='localhost', port=6333)
    
    # 存储face embedding
    client.upsert(
        collection_name='{collection_name}',
        points=[
            PointStruct(
                id='char-001',
                vector=face_embedding_vector,  # 512维向量
                payload={{
                    'character_id': 'char-001',
                    'series_id': 'SERIES-001',
                    'name': '角色名称'
                }}
            )
        ]
    )
    
    # 搜索相似face
    results = client.search(
        collection_name='{collection_name}',
        query_vector=query_vector,
        limit=5
    )
    """)


if __name__ == '__main__':
    try:
        init_qdrant()
    except Exception as e:
        print(f"❌ 错误: {e}")
        print()
        print("请确保:")
        print("  1. Qdrant服务已启动: docker-compose up -d qdrant")
        print("  2. 配置正确: 检查.env中的QDRANT_HOST和QDRANT_PORT")
        exit(1)
