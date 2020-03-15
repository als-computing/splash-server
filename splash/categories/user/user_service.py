import jsonschema
import json
from splash.data.base import MongoCollectionDao
from splash.service.base import Service, ValidationIssue
import os

dirname = os.path.dirname(__file__)
user_schema_file = open(os.path.join(dirname, "user_schema.json"))
USER_SCHEMA = json.load(user_schema_file)
user_schema_file.close()


class UserService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(self)
        self.validator = jsonschema.Draft7Validator(USER_SCHEMA)

    def validate(self, data):
        errors = self.validator.iter_errors(data)
        return_errs = []
        for error in errors:
            return_errs.append(ValidationIssue(error.message, str(error.path), error))
        return return_errs
