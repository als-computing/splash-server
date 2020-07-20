import jsonschema
import json
from splash.data.base import MongoCollectionDao
from splash.service.base import Service, ValidationIssue
from splash.categories.utils import openSchema

EXPERIMENTS_SCHEMA = openSchema('experiment_schema.json', __file__)


class ExperimentService(Service):

    def __init__(self, dao: MongoCollectionDao,):
        super().__init__(dao, EXPERIMENTS_SCHEMA)