import jsonschema
import json
from splash.data.base import MongoCollectionDao
from splash.service.base import Service, ValidationIssue
from splash.categories.utils import openSchema
import os

COMPOUND_SCHEMA = openSchema('compounds_schema.json', __file__)


class CompoundsService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(dao, COMPOUND_SCHEMA)
