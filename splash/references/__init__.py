# from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, constr, Extra
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


class CreateReferenceResponse(BaseModel):
    uid: str