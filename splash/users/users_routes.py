from attr import dataclass
from fastapi import APIRouter, Security
# from fastapi.security import OpenIdConnect
from pydantic import BaseModel
from typing import List

from . import User, NewUser
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


@users_router.get("", tags=["users"], response_model=List[User])
def read_users(
            current_user: User = Security(get_current_user)):
    results = services.users.retrieve_multiple(current_user)
    return list(results)


@users_router.get("/{uid}", tags=['users'], response_model=User)
def read_user(
            uid: str,
            current_user: User = Security(get_current_user)):
    return services.users.retrieve_one(current_user, uid)


@users_router.put("/{uid}", tags=['users'], response_model=CreateUserResponse)
def replace_user(
        uid: str,
        user: NewUser,
        current_user: User = Security(get_current_user)):
    uid = services.users.update(current_user, user, uid)
    return CreateUserResponse(uid=uid)


@users_router.post("", tags=['users'], response_model=CreateUserResponse)
def create_user(
                user: NewUser,
                current_user: User = Security(get_current_user)):
    uid = services.users.create(current_user, user)
    return CreateUserResponse(uid=uid)
