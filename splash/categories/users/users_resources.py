from flask import current_app
from splash.resource.base import SingleObjectResource, MultiObjectResource
from splash.data.base import MongoCollectionDao


COLLECTION_NAME = 'users' 

class Users(MultiObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db, COLLECTION_NAME)
        super().__init__(dao)


class User(SingleObjectResource):
    def __init__(self):
        dao = MongoCollectionDao(current_app.db, COLLECTION_NAME)
        super().__init__(dao)
