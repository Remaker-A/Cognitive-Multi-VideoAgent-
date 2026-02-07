from typing import Optional, List
from sqlmodel import Session, select
from src.domain.models import Script, Character, Shot

class ScriptRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, script: Script) -> Script:
        self.session.add(script)
        self.session.commit()
        self.session.refresh(script)
        return script

    def get_by_project_id(self, project_id: str) -> Optional[Script]:
        statement = select(Script).where(Script.project_id == project_id)
        return self.session.exec(statement).first()

    def update(self, script: Script) -> Script:
        self.session.add(script)
        self.session.commit()
        self.session.refresh(script)
        return script

    def add_characters(self, characters: List[Character]):
        for char in characters:
            self.session.add(char)
        self.session.commit()
        
    def add_shots(self, shots: List[Shot]):
        for shot in shots:
            self.session.add(shot)
        self.session.commit()
