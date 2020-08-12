from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List
from splash.models.users import UserModel, NewUserModel

from splash.categories.users.users_service import UserService
from ..services import get_users_service

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/", tags=["users"], response_model=List[UserModel])
def read_users(users_service: UserService = Depends(get_users_service)):
    results = users_service.retrieve_multiple(1)
    return results[1]


@router.get("/{uid}", tags=['users'])
def read_user(uid: str, users_service: UserService = Depends(get_users_service)):
    user_json = users_service.retrieve_one(uid)
    return (UserModel(**user_json))


@router.post("/", tags=['users'])
def create_user(user: NewUserModel, users_service: UserService = Depends(get_users_service)):
    uid = users_service.create(dict(user))
    return uid
