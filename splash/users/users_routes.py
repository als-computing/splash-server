from fastapi.param_functions import Header
from attr import dataclass
from fastapi import APIRouter, Security
from fastapi.exceptions import HTTPException
# from fastapi.security import OpenIdConnect
from pydantic import BaseModel
from typing import List, Optional

from . import User, NewUser, UserSplashMd
from .users_service import UsersService

from splash.api.auth import get_current_user


users_router = APIRouter()

@dataclass
class Services():
    users: UsersService


services = Services(None)


def set_users_service(users_service: UsersService):
    services.users = users_service


class CreateUserResponse(BaseModel):
    uid: str
    splash_md: UserSplashMd


@users_router.get("", tags=["users"], response_model=List[User])
def read_users(
            current_user: User = Security(get_current_user)):
    results = services.users.retrieve_multiple(current_user)
    return list(results)


@users_router.get("/{uid}", tags=['users'], response_model=User)
def read_user(
            uid: str,
            current_user: User = Security(get_current_user)):
    user = services.users.retrieve_one(current_user, uid)
    if user is None:
        raise HTTPException(
                status_code=404,
                detail="object not found",
            )
    return user


@users_router.put("/{uid}", tags=['users'], response_model=CreateUserResponse)
def replace_user(
        uid: str,
        user: NewUser,
        current_user: User = Security(get_current_user),
        if_match: Optional[str] = Header(None)):
    return services.users.update(current_user, user, uid, etag=if_match)


@users_router.post("", tags=['users'], response_model=CreateUserResponse)
def create_user(
                user: NewUser,
                current_user: User = Security(get_current_user)):
    return services.users.create(current_user, user)
