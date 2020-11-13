from collections import namedtuple
import logging
from typing import Dict
import uuid

from pymongo import MongoClient

from splash.models.users import UserModel


ValidationIssue = namedtuple('ValidationIssue', 'description, location, exception')

logger = logging.getLogger('splash_server.service')

class BadPageArgument(Exception):
    pass


class Service():

    def create(self, current_user: UserModel, data):
        raise NotImplementedError

    def retrieve_one(self, current_user: UserModel, uid):
        raise NotImplementedError

    def retrieve_multiple(self,
                          current_user: UserModel,
                          page: int,
                          query=None,
                          page_size=10):
        raise NotImplementedError

    def update(self, current_user: UserModel, data, uid: str):
        raise NotImplementedError

    def delete(self, current_user: UserModel, uid):
        raise NotImplementedError


class MongoService():

    def __init__(self, db, collection_name):
        self._db = db
        self._collection = db[collection_name]

    def create(self, current_user: UserModel, data: Dict):
        logger.debug(f"create doc in collection {0}, doc: {1}", self._collection, data)
        if 'uid' in data:
            raise UidInDictError('Document should not have uid field')
        uid = uuid.uuid4()
        data['uid'] = str(uid)
        self._collection.insert_one(data)
        return data['uid']

    def retrieve_one(self, current_user: UserModel, uid) -> dict:
        return self._collection.find_one({"uid": uid}, {'_id': False})

    def retrieve_multiple(self,
                          user: UserModel,
                          page: int = 1,
                          query=None,
                          page_size=10):

        if page <= 0:
            raise BadPageArgument("Page parameter must greater than 0")

        # Calculate number of documents to skip
        skips = page_size * (page - 1)
        # Skip and limit
        if query is None:
            query = {}
        cursor = self._collection.find(query, {'_id': False}).skip(skips).limit(page_size)

        # Return documents
        return cursor

    def update(self, current_user: UserModel, data: str, uid: str):
        # update_one might be more efficient, but kinda tricky
        data['uid'] = uid
        status = self._collection.replace_one({"uid": uid}, data)
        if status.matched_count == 0:
            raise ObjectNotFoundError
        return uid

    def delete(self, current_user: UserModel, uid):
        status = self._collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError


class ObjectNotFoundError(Exception):
    pass

class UidInDictError(KeyError):
    pass