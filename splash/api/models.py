from enum import Enum

from pydantic import BaseModel


class ArchiveActions(str, Enum):
    archive = 'archive'
    restore = 'restore'


class PatchBody(BaseModel):
    archive_action: ArchiveActions
