from splash.service import CreatedDocument, CreatedVersionedDocument
from typing import List
from pydantic import BaseModel, Extra, constr


class Metadata(BaseModel):
    title: constr(min_length=1)
    text: constr(min_length=1)

    class Config:
        extra = Extra.forbid


class Section(BaseModel):
    title: constr(min_length=1)
    text: constr(min_length=1)

    class Config:
        extra = Extra.forbid


class Documentation(BaseModel):
    sections: List[Section] = []

    class Config:
        extra = Extra.forbid


class NewPage(BaseModel):
    page_type: constr(min_length=1)
    title: constr(min_length=1)
    metadata: List[Metadata]
    documentation: Documentation

    class Config:
        extra = Extra.forbid


class Page(NewPage, CreatedVersionedDocument):
    pass


class NumVersions(BaseModel):
    number: int
