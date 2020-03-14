import os
import json
from flask import current_app
import jsonschema
from .resources import MultiObjectResource, SingleObjectResource
from splash.service.data import MongoCollectionDao



class Experiments(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)



class Experiment(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)