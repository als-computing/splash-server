from splash.service import CreatedDocument, CreatedVersionedDocument
from typing import List
from pydantic import BaseModel, Extra, constr


class Metadata(BaseModel):
    title: constr(min_length=1)
    text: constr(min_length=1)

    class Config:
        extra = Extra.forbid


class ReferenceDois(BaseModel):
    doi: constr(min_length=1)


class NewPage(BaseModel):
    page_type: constr(min_length=1)
    title: constr(min_length=1)
    metadata: List[Metadata]
    documentation: constr(min_length=1)
    more_references: List[ReferenceDois]

    class Config:
        extra = Extra.forbid


class UpdatePage(NewPage):
    pass


class Page(NewPage, CreatedVersionedDocument):
    pass
