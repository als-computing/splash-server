from pydantic.types import StrictBool
from splash.service import CreatedVersionedDocument
from typing import List
from pydantic import BaseModel, Extra, constr


class ReferenceDois(BaseModel):
    uid: constr(min_length=1)
    in_text: StrictBool


class NewPage(BaseModel):
    page_type: constr(min_length=1)
    title: constr(min_length=1)
    documentation: constr(min_length=1)
    references: List[ReferenceDois]

    class Config:
        extra = Extra.forbid


class UpdatePage(NewPage):
    pass


class Page(NewPage, CreatedVersionedDocument):
    pass
