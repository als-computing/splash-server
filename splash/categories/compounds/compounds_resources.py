from flask import current_app
from splash.resource.base import SingleObjectResource, MultiObjectResource
from splash.data.base import MongoCollectionDao


class Compundss(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.compounds)
        super().__init__(dao)


class Compound(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.compounds)
        super().__init__(dao)
