from .data import MongoCollectionDao
from collections import namedtuple

ValidationIssue = namedtuple('ValidationIssue', 'description, location, exception')


class Service():

    def __init__(self, dao: MongoCollectionDao):
        self.dao = dao

    def create(self, data):
        self.dao.create(data)

    def retreive_one(self, uid):
        return self.dao.retrieve(uid)

    def retreive_multiple(self, page, query=None, page_size=10):
        return self.dao.retreive_multiple(page, query, page_size)

    def update(self, uid, data):
        return self.dao.update(data)

    def delete(self, uid):
        raise self.dao.delete(uid)

    def validate(data):
        return []

