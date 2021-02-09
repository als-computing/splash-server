from collections import namedtuple
import logging
from splash.service.models import SplashMetadata
import uuid
from datetime import datetime
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
        if 'uid' in data:
            raise UidInDictError('Document should not have uid field')
        uid = uuid.uuid4()
        data['uid'] = str(uid)

        if "splash_md" not in data:
            data["splash_md"] = {}
        
        basic_md_fields = SplashMetadata.__dict__["__fields__"]
        for field in basic_md_fields:
            if field in data["splash_md"]:
                raise ImmutableMetadataField(f"Cannot mutate field: `{field}` in `splash_md`")

        data["splash_md"]["create_date"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        data["splash_md"]["last_edit"] = data["splash_md"]["create_date"]
        if current_user is None:
            data["splash_md"]["creator"] = "NONE"
        else:
            data["splash_md"]["creator"] = current_user.uid
        data["splash_md"]["edit_record"] = []

        logger.debug(f"create doc in collection {0}, doc: {1}", self._collection, data)

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
        cursor = self._collection.find(query, {'_id': False}).sort([("splash_md.last_edit", -1), ("splash_md.uid", -1)]).skip(skips).limit(page_size)

        # Return documents
        return cursor

    def update(self, current_user: User, data: dict, uid: str):
        # update_one might be more efficient, but kinda tricky
        if 'uid' in data:
            raise UidInDictError('Document should not have uid field')
        data['uid'] = uid
        
        current_document = MongoService.retrieve_one(self, current_user, uid)
        metadata = current_document["splash_md"]
        if "splash_md" not in data:
            data["splash_md"] = metadata
        else:
            basic_md_fields = SplashMetadata.__dict__["__fields__"]
            for field in basic_md_fields:
                # The top layer that called this cannot mutate
                # any of these fields. They should only be mutated by
                # This service layer
                if field in data["splash_md"]:
                    raise ImmutableMetadataField(f"Cannot mutate field: `{field}` in `splash_md`")
                data["splash_md"][field] = metadata[field]
        data["splash_md"]["last_edit"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
        data["splash_md"]["edit_record"].append({"date": data["splash_md"]["last_edit"], "user": current_user.uid})
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
        if "splash_md" in data:
            if "version" in data["splash_md"]:
                raise ImmutableMetadataField("Cannot mutate field: `version` in `splash_md`")
        else:
            data["splash_md"] = {}

        current_document = super().retrieve_one(current_user, uid)
        if current_document is None:
            raise ObjectNotFoundError
        data["splash_md"]["version"] = current_document["splash_md"]["version"] + 1
        self._versions_svc._collection.insert_one(current_document)
        return super().update(current_user, data, uid)

    def create(self, current_user: User, data: dict):
        if "splash_md" in data:
            if "version" in data["splash_md"]:
                raise ImmutableMetadataField("Cannot mutate field: `version` in `splash_md`")
        else:
            data["splash_md"] = {}
        data["splash_md"]["version"] = 1
        return super().create(current_user, data)

    def retrieve_version(self, current_user: User, uid: str, version):
        if not isinstance(version, int):
            raise TypeError("argument `version` must be an integer")
        if version <= 0:
            raise ValueError("argument `version` must be more than zero")

        document = super().retrieve_one(current_user, uid)
        if document is None or document["splash_md"]["version"] != version:
            document = self._versions_svc._collection.find_one({"$and": [{"uid": uid}, {"splash_md.version": version}]}, {'_id': False})
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

    def get_num_versions(self, current_user: User, uid):
        document = super().retrieve_one(current_user, uid)
        if document is None:
            raise ObjectNotFoundError
        num = document["splash_md"]['version']
        return num

    def delete(self, current_user: User, uid):
        raise NotImplementedError


class ObjectNotFoundError(Exception):
    pass


class VersionNotFoundError(Exception):
    pass


class UidInDictError(KeyError):
    pass


class ImmutableMetadataField(KeyError):
    pass
