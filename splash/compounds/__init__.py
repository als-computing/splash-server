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


class NewCompound(BaseModel):
    species: constr(min_length=1)
    metadata: List[Metadata]
    documentation: Documentation

    class Config:
        extra = Extra.forbid


class Compound(NewCompound):
    uid: str