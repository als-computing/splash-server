import jsonschema
import json
from .data import MongoCollectionDao
from .base import Service, ValidationIssue
import os

dirname = os.path.dirname(__file__)
experiments_schema_file = open(os.path.join(dirname, "experiment_schema.json"))
EXPERIMENTS_SCHEMA = json.load(experiments_schema_file)
experiments_schema_file.close()


class ExperimentService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(self)
        self.validator = jsonschema.Draft7Validator(EXPERIMENTS_SCHEMA)

    def validate(self, data):
        errors = self.validator.iter_errors(data)
        return_errs = []
        for error in errors:
            return_errs.append(ValidationIssue(error.message, str(error.path), error))
        return return_errs
