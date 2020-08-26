from pydantic import BaseModel, Extra
from typing import List


class Metadata(BaseModel):
    name: str
    value: str


class Section(BaseModel):
    title: str
    text: str


class Documentation(BaseModel):
    sections: List[Section] = []


class NewCompound(BaseModel):
    species: str
    metadata: List[Metadata]
    documentation: Documentation

    class Config:
        extra = Extra.forbid


class Compound(NewCompound):
    uid: str
