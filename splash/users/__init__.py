from typing import List, Optional

from pydantic import BaseModel, Extra
from splash.service.models import CreatedDocument, SplashMetadata


class AuthenticatorModel(BaseModel):
    issuer: str
    email: str
    subject: Optional[str] #TODO this should be required, but data needs migration


class NewUserSplashMd(BaseModel):
    admin: Optional[bool] = None

    class Config:
        extra = Extra.forbid


class NewUser(BaseModel):
    splash_md: Optional[NewUserSplashMd] = NewUserSplashMd()
    given_name: str
    family_name: str
    email: Optional[str]
    authenticators: Optional[List[AuthenticatorModel]]

    class Config:
        extra = Extra.forbid


class UserSplashMd(SplashMetadata):
    admin: Optional[bool] = None


class User(NewUser, CreatedDocument):
    disabled: Optional[bool] = None
    splash_md: UserSplashMd
