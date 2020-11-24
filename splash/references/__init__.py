from datetime import datetime
from pydantic import BaseModel, Extra, constr

from pydantic.networks import AnyHttpUrl


class NewReference(BaseModel):
    reference: constr(min_length=1)
    doi_url: AnyHttpUrl

    class Config:
        extra = Extra.forbid


class Reference(NewReference):
    uid: str
    date_created: datetime
    user_uid: str


class CreateReferenceResponse(BaseModel):
    uid: str
