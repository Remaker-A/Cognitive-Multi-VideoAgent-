"""
Blackboard 工厂类

提供便捷的 Blackboard 实例创建方法
"""

import psycopg2.pool
import redis

from .blackboard import SharedBlackboard
from .config import BlackboardConfig


class BlackboardFactory:
    """Blackboard 工厂"""
    
    @staticmethod
    def create(config: BlackboardConfig = None) -> SharedBlackboard:
        """
        创建 Blackboard 实例
        
        Args:
            config: 配置对象，如果为 None 则从环境变量加载
            
        Returns:
            SharedBlackboard: Blackboard 实例
        """
        if config is None:
            config = BlackboardConfig.from_env()
        
        # 创建 PostgreSQL 连接池
        db_pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=config.db_min_conn,
            maxconn=config.db_max_conn,
            host=config.db_host,
            port=config.db_port,
            database=config.db_name,
            user=config.db_user,
            password=config.db_password
        )
        
        # 创建 Redis 连接池
        redis_pool = redis.ConnectionPool(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db,
            max_connections=config.redis_max_connections,
            decode_responses=config.redis_decode_responses
        )
        
        redis_client = redis.Redis(connection_pool=redis_pool)
        
        # 创建 S3 客户端（可选）
        s3_client = None
        if config.s3_endpoint:
            try:
                import boto3
                s3_client = boto3.client(
                    's3',
                    endpoint_url=config.s3_endpoint,
                    aws_access_key_id=config.s3_access_key,
                    aws_secret_access_key=config.s3_secret_key
                )
            except ImportError:
                print("Warning: boto3 not installed, S3 support disabled")
        
        return SharedBlackboard(db_pool, redis_client, s3_client)
    
    @staticmethod
    def create_for_testing() -> SharedBlackboard:
        """
        创建用于测试的 Blackboard 实例
        
        Returns:
            SharedBlackboard: 测试用 Blackboard 实例
        """
        config = BlackboardConfig(
            db_name="blackboard_test",
            redis_db=1  # 使用不同的 Redis 数据库
        )
        
        return BlackboardFactory.create(config)
