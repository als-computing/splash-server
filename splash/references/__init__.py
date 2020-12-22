from pydantic import BaseModel, Extra
from datetime import datetime


class NewReference(BaseModel):
    DOI: str
    origin_url: str

    class Config:
        extra = Extra.allow


class Reference(NewReference):
    uid: str
    splash_date_created: datetime
    splash_user_uid: str
