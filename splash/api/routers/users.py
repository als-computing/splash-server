from attr import dataclass
from fastapi import APIRouter, Security
# from fastapi.security import OpenIdConnect
from pydantic import BaseModel
from typing import List
from splash.models.users import UserModel, NewUserModel
# from splash.api.main import service_provider
from .auth import get_current_user
from splash.service.users_service import UsersService

router = APIRouter()

@dataclass
class Services():
    users: UsersService


services = Services(None)

def set_services(users_service: UsersService):
    services.users = users_service


class CreateUserResponse(BaseModel):
    uid: str

@router.get("", tags=["users"], response_model=List[UserModel])
def read_users(
            current_user: UserModel = Security(get_current_user)):
    results = services.users.retrieve_multiple(current_user, 1)
    return list(results)


@router.get("/{uid}", tags=['users'], response_model=UserModel)
def read_user(
            uid: str,
            current_user: UserModel = Security(get_current_user)):
    user_json = services.users.retrieve_one(current_user, uid)
    return (UserModel(**user_json))

@router.put("/{uid}", tags=['users'], response_model=CreateUserResponse)
def replace_user(
        uid: str,
        user: NewUserModel,
        current_user: UserModel = Security(get_current_user)):
    uid = services.users.update(current_user, user.dict(), uid)
    return CreateUserResponse(uid=uid)


@router.post("", tags=['users'], response_model=CreateUserResponse)
def create_user(
                user: NewUserModel,
                current_user: UserModel = Security(get_current_user)):
    uid = services.users.create(current_user, user.dict())
    return CreateUserResponse(uid=uid)
