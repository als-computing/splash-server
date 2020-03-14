from flask import current_app
from splash.resource.base import SingleObjectResource, MultiObjectResource
from splash.data.base import MongoCollectionDao


class Experiments(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)


class Experiment(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)
