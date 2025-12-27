"""
Configuration for Event Bus.
"""

from typing import Optional
from pydantic import BaseSettings, Field


class EventBusConfig(BaseSettings):
    """Event Bus configuration"""
    
    # Redis connection
    redis_url: str = Field(
        default="redis://localhost:6379",
        env="REDIS_URL",
        description="Redis connection URL"
    )
    
    redis_password: Optional[str] = Field(
        default=None,
        env="REDIS_PASSWORD",
        description="Redis password"
    )
    
    # Stream configuration
    stream_prefix: str = Field(
        default="event_stream",
        env="EVENT_STREAM_PREFIX",
        description="Prefix for Redis stream keys"
    )
    
    consumer_group: str = Field(
        default="agent_group",
        env="EVENT_CONSUMER_GROUP",
        description="Consumer group name"
    )
    
    # Performance tuning
    max_stream_length: int = Field(
        default=10000,
        env="EVENT_MAX_STREAM_LENGTH",
        description="Maximum number of events to keep in each stream"
    )
    
    consumer_batch_size: int = Field(
        default=10,
        env="EVENT_CONSUMER_BATCH_SIZE",
        description="Number of events to consume in each batch"
    )
    
    consumer_block_ms: int = Field(
        default=1000,
        env="EVENT_CONSUMER_BLOCK_MS",
        description="Milliseconds to block when waiting for events"
    )
    
    # Persistence
    enable_event_persistence: bool = Field(
        default=True,
        env="EVENT_ENABLE_PERSISTENCE",
        description="Enable event persistence to database"
    )
    
    event_retention_days: int = Field(
        default=30,
        env="EVENT_RETENTION_DAYS",
        description="Number of days to retain events"
    )
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global config instance
event_bus_config = EventBusConfig()
