from sqlmodel import Session
from src.infrastructure.repositories.project_repository import ProjectRepository
from src.infrastructure.repositories.script_repository import ScriptRepository

class ProjectService:
    def __init__(self, session: Session):
        self.session = session
        self.project_repo = ProjectRepository(session)
        self.script_repo = ScriptRepository(session)

    def create_project(self, project_id: str, description: str, **kwargs) -> dict:
        # Check if exists
        existing = self.project_repo.get(project_id)
        if existing:
            return existing

        from src.domain.models import Project
        project = Project(id=project_id, description=description, **kwargs)
        return self.project_repo.create(project)

    def get_project_state(self, project_id: str) -> dict:
        project = self.project_repo.get(project_id)
        if not project:
            return None
            
        script = self.script_repo.get_by_project_id(project_id)
        
        state = {
            "requirement": {
                "description": project.description,
                "style": project.style,
                "duration": project.duration,
                "quality_tier": project.quality_tier
            },
            "analysis": project.analysis,  # If relation loaded, or need repo
            "script": script.dict() if script else None # simple parsing
            # ... other state
        }
        
        # Manually constructing complex nested state logic (or use Pydantic schemas)
        if script:
             state["script"] = {
                 "content": script.content,
                 "characters": [c.dict() for c in script.characters] if script.characters else []
             }
             
        # TODO: Add storyboard, assets etc.
        
        return state
