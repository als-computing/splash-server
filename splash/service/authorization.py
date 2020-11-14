from enum import Enum
from typing import List
from ..models.users import UserModel
from ..teams.models import Team
from ..teams.service import TeamsService


class AccessDenied(Exception):
    pass


class Action(Enum):
    CREATE = "create"
    RETRIEVE = "RETRIEVE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Checker():

    def can_do(self, user: UserModel, resource, action, **kwargs) -> bool:
        raise NotImplementedError()


class TeamBasedChecker(Checker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: UserModel, resource, action: Action, teams=List[Team], **kwargs):
        raise NotImplementedError
