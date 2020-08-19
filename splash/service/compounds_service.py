from splash.data.base import MongoCollectionDao
from splash.service.base import Service, ValidationIssue
import os


class CompoundsService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(dao)
