import os
import json
from flask import current_app
import jsonschema
from .resources import MultiObjectResource, SingleObjectResource
from splash.data import (BadIdError, MongoCollectionDao,
                         ObjectNotFoundError)

dirname = os.path.dirname(__file__)
experiments_schema_file = open(os.path.join(dirname, "experiment_schema.json"))
EXPERIMENTS_SCHEMA = json.load(experiments_schema_file)
experiments_schema_file.close()


class Experiments(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)

    def validate(self, data):
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)


class Experiment(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)

    def validate(self, data):
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)
