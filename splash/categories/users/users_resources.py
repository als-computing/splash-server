from flask import current_app
from splash.resource.base import SingleObjectResource, MultiObjectResource
from splash.data.base import MongoCollectionDao

BASE_URL_SEGMENT = 'users' 

class Users(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)


class User(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db.splash.experiments)
        super().__init__(dao)
