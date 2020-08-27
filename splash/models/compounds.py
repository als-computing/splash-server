from pydantic import BaseModel, Extra, constr
from typing import List


class Metadata(BaseModel):
    name: constr(min_length=1)
    value: constr(min_length=1)


class Section(BaseModel):
    title: constr(min_length=1)
    text: constr(min_length=1)


class Documentation(BaseModel):
    sections: List[Section] = []


class NewCompound(BaseModel):
    species: constr(min_length=1)
    metadata: List[Metadata]
    documentation: Documentation

    class Config:
        extra = Extra.forbid


class Compound(NewCompound):
    uid: str
