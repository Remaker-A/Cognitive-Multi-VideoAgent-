#!/usr/bin/env python3
"""
VideoGen 环境验证脚本

验证所有必需服务是否正常运行
"""

import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 颜色输出
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'


def check_postgres():
    """检查PostgreSQL连接"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv('POSTGRES_HOST', 'localhost'),
            port=int(os.getenv('POSTGRES_PORT', 5432)),
            database=os.getenv('POSTGRES_DB', 'videogen'),
            user=os.getenv('POSTGRES_USER', 'videogen_user'),
            password=os.getenv('POSTGRES_PASSWORD')
        )
        cursor = conn.cursor()
        
        # 检查三层黑板表是否存在
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='public' AND table_name IN ('series', 'episodes', 'shots')
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        if len(tables) == 3:
            print(f"{GREEN}✅ PostgreSQL:{RESET} 连接成功，三层黑板表已创建 (series, episodes, shots)")
            return True
        else:
            print(f"{YELLOW}⚠️  PostgreSQL:{RESET} 连接成功，但缺少表: {set(['series', 'episodes', 'shots']) - set(tables)}")
            return False
    except ImportError:
        print(f"{RED}❌ PostgreSQL:{RESET} psycopg2未安装 (pip install psycopg2-binary)")
        return False
    except Exception as e:
        print(f"{RED}❌ PostgreSQL:{RESET} {e}")
        return False


def check_redis():
    """检查Redis连接"""
    try:
        import redis
        r = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=0,
            decode_responses=True
        )
        r.ping()
        
        # 测试基本操作
        r.set('videogen:health_check', '1', ex=10)
        value = r.get('videogen:health_check')
        
        if value == '1':
            print(f"{GREEN}✅ Redis:{RESET} 连接成功，读写正常")
            return True
        else:
            print(f"{YELLOW}⚠️  Redis:{RESET} 连接成功，但读写异常")
            return False
    except ImportError:
        print(f"{RED}❌ Redis:{RESET} redis未安装 (pip install redis)")
        return False
    except Exception as e:
        print(f"{RED}❌ Redis:{RESET} {e}")
        return False


def check_qdrant():
    """检查Qdrant Vector DB连接"""
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(
            host=os.getenv('QDRANT_HOST', 'localhost'),
            port=int(os.getenv('QDRANT_PORT', 6333))
        )
        
        collections = client.get_collections()
        collection_names = [c.name for c in collections.collections]
        
        # 检查face_embeddings集合是否存在
        if 'face_embeddings' in collection_names:
            print(f"{GREEN}✅ Qdrant:{RESET} 连接成功，face_embeddings集合已创建")
            return True
        else:
            print(f"{YELLOW}⚠️  Qdrant:{RESET} 连接成功，但face_embeddings集合未创建")
            print(f"   运行: python scripts/init_qdrant.py")
            return False
    except ImportError:
        print(f"{RED}❌ Qdrant:{RESET} qdrant-client未安装 (pip install qdrant-client)")
        return False
    except Exception as e:
        print(f"{RED}❌ Qdrant:{RESET} {e}")
        return False


def check_minio():
    """检查MinIO连接"""
    try:
        from minio import Minio
        
        endpoint = os.getenv('S3_ENDPOINT', 'localhost:9000').replace('http://', '').replace('https://', '')
        client = Minio(
            endpoint,
            access_key=os.getenv('S3_ACCESS_KEY', 'minioadmin'),
            secret_key=os.getenv('S3_SECRET_KEY', 'minioadmin123'),
            secure=False
        )
        
        # 检查buckets
        buckets = client.list_buckets()
        bucket_names = [b.name for b in buckets]
        
        required_buckets = ['videogen-artifacts', 'videogen-temp']
        missing_buckets = set(required_buckets) - set(bucket_names)
        
        if not missing_buckets:
            print(f"{GREEN}✅ MinIO:{RESET} 连接成功，所需buckets已创建")
            return True
        else:
            print(f"{YELLOW}⚠️  MinIO:{RESET} 连接成功，但缺少buckets: {missing_buckets}")
            print(f"   运行: python scripts/init_minio.py")
            return False
    except ImportError:
        print(f"{RED}❌ MinIO:{RESET} minio未安装 (pip install minio)")
        return False
    except Exception as e:
        print(f"{RED}❌ MinIO:{RESET} {e}")
        return False


def check_ai_apis():
    """检查AI API配置"""
    results = {}
    
    # OpenAI
    openai_key = os.getenv('OPENAI_API_KEY', '')
    if openai_key and openai_key != 'your_openai_api_key_here':
        print(f"{GREEN}✅ OpenAI:{RESET} API密钥已配置")
        results['openai'] = True
    else:
        print(f"{YELLOW}⚠️  OpenAI:{RESET} API密钥未配置")
        results['openai'] = False
    
    # Stability AI
    stability_key = os.getenv('STABILITY_API_KEY', '')
    if stability_key and stability_key != 'your_stability_api_key_here':
        print(f"{GREEN}✅ Stability AI:{RESET} API密钥已配置")
        results['stability'] = True
    else:
        print(f"{YELLOW}⚠️  Stability AI:{RESET} API密钥未配置")
        results['stability'] = False
    
    # Runway
    runway_key = os.getenv('RUNWAY_API_KEY', '')
    if runway_key and runway_key != 'your_runway_api_key_here':
        print(f"{GREEN}✅ Runway:{RESET} API密钥已配置")
        results['runway'] = True
    else:
        print(f"{YELLOW}⚠️  Runway:{RESET} API密钥未配置")
        results['runway'] = False
    
    return all(results.values())


def main():
    """主验证流程"""
    print("=" * 60)
    print("VideoGen 开发环境验证")
    print("=" * 60)
    print()
    
    print("📦 检查基础设施服务...")
    print("-" * 60)
    postgres_ok = check_postgres()
    redis_ok = check_redis()
    qdrant_ok = check_qdrant()
    minio_ok = check_minio()
    
    print()
    print("🤖 检查AI模型API配置...")
    print("-" * 60)
    ai_ok = check_ai_apis()
    
    print()
    print("=" * 60)
    
    # 统计结果
    infrastructure_checks = [postgres_ok, redis_ok, qdrant_ok, minio_ok]
    infrastructure_passed = sum(infrastructure_checks)
    
    print(f"基础设施: {infrastructure_passed}/4 通过")
    print(f"AI API配置: {'完整' if ai_ok else '不完整'}")
    
    print("=" * 60)
    
    if all(infrastructure_checks) and ai_ok:
        print(f"{GREEN}✅ 所有服务就绪！可以开始开发。{RESET}")
        return 0
    elif all(infrastructure_checks):
        print(f"{YELLOW}⚠️  基础设施就绪，但AI API未完全配置。{RESET}")
        print(f"   请在.env中配置API密钥后再开始使用AI功能。")
        return 0
    else:
        print(f"{RED}❌ 部分服务未就绪，请检查配置。{RESET}")
        print()
        print("💡 提示:")
        print("   1. 确保Docker服务已启动: docker-compose up -d")
        print("   2. 检查服务状态: docker-compose ps")
        print("   3. 查看服务日志: docker-compose logs")
        print("   4. 参考文档: docs/ENVIRONMENT_SETUP.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())
