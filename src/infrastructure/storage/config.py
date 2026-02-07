"""
Storage Service 配置管理
"""

import os
from dataclasses import dataclass


@dataclass
class StorageConfig:
    """Storage Service 配置"""
    
    # S3 配置
    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_bucket_name: str = "artifacts"
    s3_region: str = "us-east-1"
    
    # 缓存配置
    enable_cache: bool = True
    cache_ttl_days: int = 30
    
    # URL 配置
    signed_url_expires_in: int = 3600  # 1 小时
    
    @classmethod
    def from_env(cls) -> "StorageConfig":
        """从环境变量加载配置"""
        return cls(
            s3_endpoint_url=os.getenv("S3_ENDPOINT_URL", "http://localhost:9000"),
            s3_access_key=os.getenv("S3_ACCESS_KEY", "minioadmin"),
            s3_secret_key=os.getenv("S3_SECRET_KEY", "minioadmin"),
            s3_bucket_name=os.getenv("S3_BUCKET_NAME", "artifacts"),
            s3_region=os.getenv("S3_REGION", "us-east-1"),
            enable_cache=os.getenv("STORAGE_ENABLE_CACHE", "true").lower() == "true",
            cache_ttl_days=int(os.getenv("STORAGE_CACHE_TTL_DAYS", "30")),
            signed_url_expires_in=int(os.getenv("STORAGE_SIGNED_URL_EXPIRES", "3600")),
        )
