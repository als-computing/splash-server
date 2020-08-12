from typing import Optional
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pymongo import MongoClient
from pydantic import BaseModel

from .routers import users, tokens, compounds, runs

print("in")
# from splash.categories.users.users_service import UserService, UserNotFoundException, MultipleUsersAuthenticatorException
# from splash.data.base import MongoCollectionDao

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


app.include_router(
    tokens.router,
    prefix="/api/tokensignin",
    tags=["tokens"],
    responses={404: {"description": "Not found"}}
)


app.include_router(
    users.router,
    prefix="/api/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    compounds.router,
    prefix="/api/compounds",
    tags=["compounds"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    runs.router,
    prefix="/api/runs",
    tags=["runs"],
    responses={404: {"description": "Not found"}}
)
