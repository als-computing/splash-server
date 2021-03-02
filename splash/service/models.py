from typing import List
from pydantic import BaseModel
from datetime import datetime


class EditElement(BaseModel):
    date: datetime
    user: str


class SplashMetadata(BaseModel):
    creator: str
    create_date: datetime
    last_edit: datetime
    edit_record: List[EditElement]


class VersionedSplashMetadata(SplashMetadata):
    version: int


class CreatedDocument(BaseModel):
    uid: str
    splash_md: SplashMetadata


class CreatedVersionedDocument(BaseModel):
    uid: str
    splash_md: VersionedSplashMetadata
