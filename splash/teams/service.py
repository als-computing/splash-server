from typing import List
from pydantic import parse_obj_as

from ..data.base import MongoCollectionDao
from ..models.users import UserModel
from ..service.base import Service
from ..models.teams import Team


class TeamsService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(dao)

    def get_user_teams(self, user: UserModel, uid: str) -> List[Team]:
        # find teams that contain the member by uid
        query = {
            "members." + uid: {"$exists": True}
        }
        teams_dicts = list(self.dao.retrieve_paged(query=query))
        return parse_obj_as(List[Team], teams_dicts)
