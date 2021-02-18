from calendar import c
from collections import namedtuple
import logging
from typing import Dict
import uuid

from splash.users import User


ValidationIssue = namedtuple('ValidationIssue', 'description, location, exception')

logger = logging.getLogger('splash.service')


class BadPageArgument(Exception):
    pass


class Service():

    def create(self, current_user: User, data):
        raise NotImplementedError

    def retrieve_one(self, current_user: User, uid):
        raise NotImplementedError

    def retrieve_multiple(self,
                          current_user: User,
                          page: int,
                          query=None,
                          page_size=10):
        raise NotImplementedError

    def update(self, current_user: User, data, uid: str):
        raise NotImplementedError

    def delete(self, current_user: User, uid):
        raise NotImplementedError


class MongoService():

    def __init__(self, db, collection_name):
        self._db = db
        self._collection = db[collection_name]

    def create(self, current_user: User, data: dict):
        logger.debug(f"create doc in collection {0}, doc: {1}", self._collection, data)
        if 'uid' in data:
            raise UidInDictError('Document should not have uid field')
        uid = uuid.uuid4()
        data['uid'] = str(uid)
        self._collection.insert_one(data)
        return data['uid']

    def retrieve_one(self, current_user: User, uid) -> dict:
        return self._collection.find_one({"uid": uid}, {'_id': False})

    def retrieve_multiple(self,
                          user: User,
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

    def update(self, current_user: User, data: dict, uid: str):
        # update_one might be more efficient, but kinda tricky
        # if 'uid' in data:
        #     raise UidInDictError('Document should not have uid field')
        data['uid'] = uid
        status = self._collection.replace_one({"uid": uid}, data)
        if status.matched_count == 0:
            raise ObjectNotFoundError
        return uid

    def delete(self, current_user: User, uid):
        status = self._collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError


class VersionedMongoService(MongoService):
    def __init__(self, db, collection_name, revisions_collection_name):
        super().__init__(db, collection_name)
        self._versions_svc = MongoService(db, revisions_collection_name)

    def update(self, current_user: User, data: dict, uid: str):
        # update_one might be more efficient, but kinda tricky
        if "document_version" in data:
            raise VersionInDictError("Cannot have `document_version` key in dict.")

        current_document = super().retrieve_one(current_user, uid)
        if current_document is None:
            raise ObjectNotFoundError
        data["document_version"] = current_document["document_version"] + 1
        self._versions_svc._collection.insert_one(current_document)
        return super().update(current_user, data, uid)

    def create(self, current_user: User, data: dict):
        if "document_version" in data:
            raise VersionInDictError("Cannot have `document_version` key in dict.")
        data["document_version"] = 1
        return super().create(current_user, data)

    def retrieve_version(self, current_user: User, uid: str, version):
        if not isinstance(version, int):
            raise TypeError("argument `version` must be an integer")
        if version <= 0:
            raise ValueError("argument `version` must be more than zero")

        document = super().retrieve_one(current_user, uid)
        if document is None or document["document_version"] != version:
            document = self._versions_svc._collection.find_one({"$and": [{"uid": uid}, {"document_version": version}]}, {'_id': False})
            if document is not None:
                return document
            # If the document exists nowhere then the object was not found
            elif self._versions_svc.retrieve_one(current_user, uid) is None \
                    and super().retrieve_one(current_user, uid) is None:
                raise ObjectNotFoundError
            # If the document does exist somewhere then version was not found
            else:
                raise VersionNotFoundError

        return document

    def get_num_versions(self, current_user, uid):
        document = super().retrieve_one(current_user, uid)
        if document is None:
            raise ObjectNotFoundError
        num = document['document_version']
        return num


class ObjectNotFoundError(Exception):
    pass


class VersionNotFoundError(Exception):
    pass


class UidInDictError(KeyError):
    pass


class VersionInDictError(KeyError):
    pass
