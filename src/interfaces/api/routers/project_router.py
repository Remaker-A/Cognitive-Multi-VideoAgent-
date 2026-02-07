from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from src.infrastructure.database import get_session
from src.application.services.project_service import ProjectService

router = APIRouter(prefix="/api/project", tags=["project"])

def get_project_service(session: Session = Depends(get_session)):
    return ProjectService(session)

@router.get("/{project_id}/state")
async def get_project_state(project_id: str, service: ProjectService = Depends(get_project_service)):
    state = service.get_project_state(project_id)
    if not state:
        # Fallback for new projects? Or 404
        return {"success": True, "state": {}}
    return {"success": True, "state": state}
