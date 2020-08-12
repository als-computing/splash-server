from pydantic import BaseModel


class NewUserModel(BaseModel):
    given_name: str
    family_name: str


class UserModel(BaseModel):
    uid: str
    given_name: str
    family_name: str
