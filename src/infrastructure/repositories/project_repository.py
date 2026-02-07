from typing import Optional, List
from sqlmodel import Session, select
from src.domain.models import Project

class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project

    def get(self, project_id: str) -> Optional[Project]:
        return self.session.get(Project, project_id)

    def update(self, project: Project) -> Project:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
        
    def list(self) -> List[Project]:
        statement = select(Project)
        return self.session.exec(statement).all()
