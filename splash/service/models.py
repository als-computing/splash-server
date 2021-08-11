from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime


class EditElement(BaseModel):
    date: datetime
    user: str


# This model is for fields that can only be changed by the base mongo service
class PrivateSplashMetadata(BaseModel):
    creator: str
    create_date: datetime
    last_edit: datetime
    edit_record: List[EditElement]
    etag: str


class SplashMetadata(PrivateSplashMetadata):
    archived: Optional[bool] = None


# This model is for fields that can only be changed by the base mongo versioned service
class PrivateVersionedSplashMetadata(BaseModel):
    version: int


class VersionedSplashMetadata(SplashMetadata, PrivateVersionedSplashMetadata):
    pass


class CreatedDocument(BaseModel):
    uid: str
    splash_md: SplashMetadata


class CreatedVersionedDocument(BaseModel):
    uid: str
    splash_md: VersionedSplashMetadata
