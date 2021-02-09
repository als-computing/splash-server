from splash.service import CreatedDocument
from pydantic import BaseModel, Extra


class NewReference(BaseModel):
    DOI: str
    origin_url: str

    class Config:
        extra = Extra.allow


class Reference(NewReference, CreatedDocument):
    pass


class CreateReferenceResponse(BaseModel):
    uid: str
