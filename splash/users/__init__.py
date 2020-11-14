from typing import Optional, List

from pydantic import BaseModel, Extra


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


class User(NewUser):
    uid: str
    disabled: Optional[bool] = None
