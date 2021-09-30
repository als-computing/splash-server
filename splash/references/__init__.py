from typing import Optional

from pydantic.types import constr
from splash.service import CreatedDocument
from pydantic import BaseModel, Extra


class NewReference(BaseModel):
    DOI: Optional[constr(min_length=1)] = None
    origin_url: Optional[constr(min_length=1)] = None

    class Config:
        extra = Extra.allow


class Reference(NewReference, CreatedDocument):
    pass


class UpdateReference(NewReference):
    pass
