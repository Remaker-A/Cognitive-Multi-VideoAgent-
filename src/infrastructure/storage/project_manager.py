
import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("videogen.storage")

class ProjectManager:
    """
    Simple file-based project state manager.
    Stores project data in .kiro/projects/{project_id}/
    """

    def __init__(self, base_dir: str = ".kiro/projects"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> Path:
        p_dir = self.base_dir / project_id
        p_dir.mkdir(parents=True, exist_ok=True)
        return p_dir

    def save_section(self, project_id: str, section_name: str, data: Any):
        """Save a section of project data (e.g. 'requirement', 'script', 'storyboard')"""
        try:
            p_dir = self._get_project_dir(project_id)
            file_path = p_dir / f"{section_name}.json"
            print(f"DEBUG: Saving to {file_path}")
            print(f"DEBUG: Data to save: {data}")
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"DEBUG: Save successful")
            logger.info(f"Saved section '{section_name}' for project {project_id}")
        except Exception as e:
            print(f"DEBUG: Save error: {e}")
            logger.error(f"Failed to save section '{section_name}' for project {project_id}: {e}")

    def load_section(self, project_id: str, section_name: str) -> Optional[Any]:
        """Load a section of project data"""
        try:
            p_dir = self._get_project_dir(project_id)
            file_path = p_dir / f"{section_name}.json"
            
            if not file_path.exists():
                return None
            
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load section '{section_name}' for project {project_id}: {e}")
            return None

    def update_asset(self, project_id: str, asset_type: str, asset_key: str, asset_data: Any):
        """
        Update a specific item in an asset collection (e.g. images, videos).
        asset_type: 'images', 'videos', 'character_designs'
        """
        try:
            assets = self.load_section(project_id, "assets") or {}
            if asset_type not in assets:
                assets[asset_type] = {}
            
            assets[asset_type][asset_key] = asset_data
            self.save_section(project_id, "assets", assets)
        except Exception as e:
            logger.error(f"Failed to update asset '{asset_type}/{asset_key}' for project {project_id}: {e}")

    def get_full_state(self, project_id: str) -> Dict[str, Any]:
        """Retrieve all available state for a project"""
        state = {
            "project_id": project_id,
            "recovered_at": datetime.now().isoformat()
        }
        
        # List of known sections
        sections = ["requirement", "analysis", "script", "storyboard", "assets"]
        
        for sec in sections:
            data = self.load_section(project_id, sec)
            if data:
                state[sec] = data
                
        return state
