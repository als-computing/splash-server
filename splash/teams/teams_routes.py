from typing import List, Optional

from attr import dataclass
from fastapi import APIRouter, Security
from fastapi.exceptions import HTTPException
from fastapi import Header
from pydantic import BaseModel
from pydantic.tools import parse_obj_as
from splash.api.auth import get_current_user
from splash.service import SplashMetadata
from splash.service.base import ObjectNotFoundError

from ..users import User
from . import NewTeam, Team
from .teams_service import TeamsService

teams_router = APIRouter()


@dataclass
class Services():
    teams: TeamsService


services = Services(None)


def set_teams_service(svc: TeamsService):
    services.teams = svc


class CreateTeamResponse(BaseModel):
    uid: str
    splash_md: SplashMetadata


@teams_router.get("", tags=["teams"], response_model=List[Team])
def read_teams(
            page: int = 1,
            page_size: int = 100,
            current_user: User = Security(get_current_user)):
    results = services.teams.retrieve_multiple(current_user, page=page, page_size=page_size)
    return parse_obj_as(List[Team], list(results))


@teams_router.get("/{uid}", tags=['teams'], response_model=Team)
def read_team(
            uid: str,
            current_user: User = Security(get_current_user)):
    team = services.teams.retrieve_one(current_user, uid)
    return team


@teams_router.post("", tags=['teams'], response_model=CreateTeamResponse)
def create_team(
                team: NewTeam,
                current_user: User = Security(get_current_user)):
    response = services.teams.create(current_user, team)
    return response


@teams_router.put("/{uid}", tags=['teams'], response_model=CreateTeamResponse)
def update_team(uid: str,
                team: NewTeam,
                current_user: User = Security(get_current_user),
                if_match: Optional[str] = Header(None)):
    try:
        response = services.teams.update(current_user, team, uid, etag=if_match)
    except ObjectNotFoundError:
        raise HTTPException(404)
    return response
