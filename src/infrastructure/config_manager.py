import os
import logging
from typing import Optional
from sqlmodel import Session, select
from src.infrastructure.database import engine
from src.domain.models import SystemConfig

logger = logging.getLogger(__name__)

class ConfigManager:
    """
    Configuration Manager
    
    Retrieves configuration from the database (SystemConfig table).
    If not found in DB, falls back to environment variables.
    """
    
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get configuration value.
        Priority: DB > Environment Variable > Default
        """
        # Try DB first
        try:
            with Session(engine) as session:
                config = session.get(SystemConfig, key)
                if config:
                    return config.value
        except Exception as e:
            logger.warning(f"Failed to read config from DB for key {key}: {e}")
            
        # Fallback to Env
        return os.getenv(key, default)
    
    @staticmethod
    def set(key: str, value: str, category: str = "general", description: str = ""):
        """
        Set configuration value in DB.
        """
        with Session(engine) as session:
            config = session.get(SystemConfig, key)
            if not config:
                config = SystemConfig(key=key, value=value, category=category, description=description)
            else:
                config.value = value
                config.category = category
                if description:
                    config.description = description
            
            session.add(config)
            session.commit()
            session.refresh(config)
            logger.info(f"Configuration updated: {key}")
            return config

    @staticmethod
    def get_all_public():
        """
        Get all configurations for UI display (masking sensitive keys if necessary, 
        though for local app we might send them back so user can see what's set).
        
        For this implementation, we will return values as is, assuming local single-user context.
        """
        with Session(engine) as session:
            configs = session.exec(select(SystemConfig)).all()
            return {c.key: c.value for c in configs}
