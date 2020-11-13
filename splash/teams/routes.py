from pydantic.tools import parse_obj_as
from splash.service.base import ObjectNotFoundError
from attr import dataclass
from fastapi import APIRouter, Security
from fastapi.exceptions import HTTPException
from pydantic import BaseModel
from typing import List
from splash.models.users import UserModel
from splash.api.auth import get_current_user

from .models import Team, NewTeam
from .service import TeamsService

teams_router = APIRouter()


@dataclass
class Services():
    teams: TeamsService


services = Services(None)


def set_teams_service(svc: TeamsService):
    services.teams = svc


class CreateTeamResponse(BaseModel):
    uid: str


@teams_router.get("", tags=["teams"], response_model=List[Team])
def read_teams(
            page: int = 1,
            page_size: int = 100,
            current_user: UserModel = Security(get_current_user)):
    results = services.teams.retrieve_multiple(current_user, page=page, page_size=page_size)
    return parse_obj_as(List[Team], list(results))


@teams_router.get("/{uid}", tags=['teams'], response_model=Team)
def read_team(
            uid: str,
            current_user: UserModel = Security(get_current_user)):
    user_json = services.teams.retrieve_one(current_user, uid)
    return (Team(**user_json))


@teams_router.post("", tags=['teams'], response_model=CreateTeamResponse)
def create_team(
                team: NewTeam,
                current_user: UserModel = Security(get_current_user)):
    uid = services.teams.create(current_user, team.dict())
    return CreateTeamResponse(uid=uid)


@teams_router.put("/{uid}", tags=['teams'])
def update_team(uid: str,
                team: Team,
                current_user: UserModel = Security(get_current_user)):
    try:
        services.teams.update(current_user, team.dict(), uid)
    except ObjectNotFoundError:
        raise HTTPException(404)
    return True
