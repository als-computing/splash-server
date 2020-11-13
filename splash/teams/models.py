from typing import Dict, List
from pydantic import BaseModel, Extra


class NewTeam(BaseModel):
    name: str
    members: Dict[str, List[str]]  # uid, role

    class Config:
        extra = Extra.forbid


class Team(NewTeam):
    uid: str
