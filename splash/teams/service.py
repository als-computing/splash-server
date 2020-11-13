from typing import List
from pydantic import parse_obj_as

from ..models.users import UserModel
from ..service.base import MongoService
from .models import NewTeam, Team


class TeamsService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def create(self, current_user: UserModel, team: NewTeam):
        super().create(current_user, team.dict())

    def get_user_teams(self, request_user: UserModel, uid: str) -> List[Team]:
        # find teams that contain the member by uid
        query = {
            "members." + uid: {"$exists": True}
        }
        teams_dicts = list(self.retrieve_multiple(request_user, page=1, query=query))
        return parse_obj_as(List[Team], teams_dicts)
