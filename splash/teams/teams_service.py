from typing import Dict, List

from . import NewTeam, Team
from ..users import User
from ..service.base import MongoService


class TeamsService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def create(self, current_user: User, team: NewTeam) -> str:
        return super().create(current_user, team.dict())

    def retrieve_one(self, current_user: User, uid: str) -> Team:
        team = super().retrieve_one(current_user, uid)
        return team

    def retrieve_multiple(self,
                          current_user: User,
                          page: int = 1,
                          query=None,
                          page_size=10):
        cursor = super().retrieve_multiple(current_user, page, query, page_size)
        for team_dict in cursor:
            yield Team(**team_dict)

    def update(self, current_user: User, data: Team, uid: str):
        return super().update(current_user, data.dict(), uid)

    def delete(self, current_user: User, uid):
        raise NotImplementedError

    def get_user_teams(self, request_user: User, uid: str):
        # find teams that contain the member by uid
        query = {
            "members." + uid: {"$exists": True}
        }
        teams = self.retrieve_multiple(request_user, page=1, query=query)
        for team in teams:
            yield team
