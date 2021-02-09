from typing import List, Optional

from pydantic import BaseModel, Extra
from splash.service.models import CreatedDocument


class AuthenticatorModel(BaseModel):
    issuer: str
    email: str
    subject: Optional[str] #TODO this should be required, but data needs migration


class NewUser(BaseModel):

    given_name: str
    family_name: str
    email: Optional[str]
    authenticators: Optional[List[AuthenticatorModel]]

    class Config:
        extra = Extra.forbid


class User(NewUser, CreatedDocument):
    disabled: Optional[bool] = None
