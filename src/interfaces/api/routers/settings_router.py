from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from src.infrastructure.config_manager import ConfigManager
from src.domain.models import SystemConfig

router = APIRouter(prefix="/api/settings", tags=["Settings"])

class SettingItem(BaseModel):
    key: str
    value: str
    category: str = "general"
    description: str = ""

class SettingsUpdateResponse(BaseModel):
    success: bool
    message: str
    config: Dict[str, str]

@router.get("", response_model=Dict[str, str])
async def get_settings():
    """
    Get all system settings.
    SENSITIVE DATA WARNING: Currently returns API Keys as-is. 
    Ensure this is only used in a secure/local environment.
    """
    try:
        return ConfigManager.get_all_public()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("", response_model=SettingsUpdateResponse)
async def update_settings(settings: List[SettingItem]):
    """
    Update multiple system settings.
    """
    try:
        updated = {}
        for item in settings:
            ConfigManager.set(item.key, item.value, item.category, item.description)
            updated[item.key] = item.value
            
        return SettingsUpdateResponse(
            success=True,
            message="Settings updated successfully",
            config=updated
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
