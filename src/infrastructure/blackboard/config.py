"""
Blackboard 配置管理
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class BlackboardConfig:
    """Blackboard 配置"""
    
    # PostgreSQL 配置
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "blackboard"
    db_user: str = "postgres"
    db_password: str = "password"
    db_min_conn: int = 5
    db_max_conn: int = 20
    
    # Redis 配置
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_max_connections: int = 50
    redis_decode_responses: bool = True
    
    # 缓存配置
    cache_ttl: int = 3600  # 1 小时
    
    # S3/MinIO 配置
    s3_endpoint: Optional[str] = None
    s3_access_key: Optional[str] = None
    s3_secret_key: Optional[str] = None
    s3_bucket: str = "artifacts"
    
    @classmethod
    def from_env(cls) -> "BlackboardConfig":
        """从环境变量加载配置"""
        return cls(
            # PostgreSQL
            db_host=os.getenv("DB_HOST", "localhost"),
            db_port=int(os.getenv("DB_PORT", "5432")),
            db_name=os.getenv("DB_NAME", "blackboard"),
            db_user=os.getenv("DB_USER", "postgres"),
            db_password=os.getenv("DB_PASSWORD", "password"),
            db_min_conn=int(os.getenv("DB_MIN_CONN", "5")),
            db_max_conn=int(os.getenv("DB_MAX_CONN", "20")),
            
            # Redis
            redis_host=os.getenv("REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("REDIS_PORT", "6379")),
            redis_db=int(os.getenv("REDIS_DB", "0")),
            redis_max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
            
            # S3/MinIO
            s3_endpoint=os.getenv("S3_ENDPOINT"),
            s3_access_key=os.getenv("S3_ACCESS_KEY"),
            s3_secret_key=os.getenv("S3_SECRET_KEY"),
            s3_bucket=os.getenv("S3_BUCKET", "artifacts"),
        )
