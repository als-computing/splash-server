from enum import Enum
from typing import List
from ..models.teams import Team
from ..models.users import UserModel
from ..service.teams_service import TeamsService


class Action(Enum):
    CREATE = "create"
    RETRIEVE = "RETRIEVE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"


class Checker():

    def can_do(self, user: UserModel, resource, action) -> bool:
        raise NotImplementedError()


class TeamBasedChecker(Checker):
    def __init__(self, teams_service: TeamsService):
        super().__init__()
        self._teams_service = teams_service

    def get_user_teams(self, user: UserModel) -> List[Team]:
        teams = self._teams_service.get_user_teams(user.uid)


class TeamRunChecker(TeamBasedChecker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: UserModel, run, action: Action):
        if action == Action.RETRIEVE:
            # This rule is simple...check if the user
            # is a member the team that matches the run
            for team in self.get_user_teams(user):
                if team.name == run['team']:
                    return True
        return False
