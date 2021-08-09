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


class NotAuthorized(Exception):
    pass


# decorator for checking admin status of a user
def authorize_admin_action(func):
    def wrapper(self, current_user: User, *args, **kwargs):
        if current_user.splash_md.admin is True:
            return func(self, current_user, *args, **kwargs)
        raise NotAuthorized('user is not an admin')
    return wrapper
