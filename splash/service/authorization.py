from enum import Enum
from typing import List
from ..users import User
from ..teams import Team


class AccessDenied(Exception):
    pass


class Action(Enum):
    CREATE = "create"
    RETRIEVE = "RETRIEVE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Checker():

    def can_do(self, user: User, resource, action, **kwargs) -> bool:
        raise NotImplementedError()


class TeamBasedChecker(Checker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: User, resource, action: Action, teams=List[Team], **kwargs):
        raise NotImplementedError
