from .base import MongoService


class CompoundsService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__( db, collection_name)
