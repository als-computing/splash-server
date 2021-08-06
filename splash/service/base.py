from collections import namedtuple
import logging
from splash.service.models import SplashMetadata, VersionedSplashMetadata
import uuid
from datetime import datetime
from splash.users import User
from pymongo.collation import Collation
from pymongo import DESCENDING, IndexModel
from pymongo import ASCENDING


ValidationIssue = namedtuple("ValidationIssue", "description, location, exception")

logger = logging.getLogger("splash.service")


# This is a decorator which ensures that none of fields in SplashMetadata 
# Are being modified. We only want these fields to be modified by MongoService
# It also ensures that the uid is not being modified
def validate_base_metadata(func):
    def wrapper(self, current_user: User, data: dict, *args, **kwargs):
        if "uid" in data:
            raise UidInDictError("Document should not have uid field")

        if "splash_md" not in data:
            return func(self, current_user, data, *args, **kwargs)

        basic_md_fields = SplashMetadata.__dict__["__fields__"]
        # The top layer that called this cannot mutate
        # any of these fields. They should only be mutated by
        # this service layer
        for field in basic_md_fields:
            if field in data["splash_md"]:
                raise ImmutableMetadataField(
                    f"Cannot mutate field: `{field}` in `splash_md`"
                )
        return func(self, current_user, data, *args, **kwargs)
    return wrapper


# This is a decorator which ensures that none of the fields in VersionedSplashMetadata
# are being modified.
def validate_versioned_metadata(func):
    def wrapper(self, current_user: User, data: dict, *args, **kwargs):

        if "splash_md" not in data:
            return func(self, current_user, data, *args, **kwargs)

        versioned_md_fields = VersionedSplashMetadata.__dict__["__fields__"]
        # The top layer that called this cannot mutate
        # any of these fields. They should only be mutated by
        # this service layer
        for field in versioned_md_fields:
            if field in data["splash_md"]:
                raise ImmutableMetadataField(
                    f"Cannot mutate field: `{field}` in `splash_md`"
                )
        return func(self, current_user, data, *args, **kwargs)
    return wrapper


class BadPageArgument(Exception):
    pass


class Service:
    def create(self, current_user: User, data):
        raise NotImplementedError

    def retrieve_one(self, current_user: User, uid):
        raise NotImplementedError

    def retrieve_multiple(
        self, current_user: User, page: int, query=None, page_size=10
    ):
        raise NotImplementedError

    def update(self, current_user: User, data, uid: str):
        raise NotImplementedError

    def delete(self, current_user: User, uid):
        raise NotImplementedError


class MongoService:
    def __init__(self, db, collection_name):
        self._db = db
        self._collection = db[collection_name]
        self._create_indexes()

    def _create_indexes(self):
        uid_unique_index = IndexModel("uid", unique=True)
        creator_index = IndexModel("splash_md.creator")
        sort_index = IndexModel([("splash_md.last_edit", DESCENDING), ("uid", DESCENDING)])
        self._collection.create_indexes([uid_unique_index, creator_index, sort_index])

    @validate_base_metadata
    def create(self, current_user: User, data: dict):
        uid = uuid.uuid4()
        data["uid"] = str(uid)

        if "splash_md" not in data:
            data["splash_md"] = {}

        # remove the microsecond because mongo will truncate past a certain amount of decimal places
        data["splash_md"]["create_date"] = datetime.utcnow().replace(microsecond=0)
        data["splash_md"]["last_edit"] = data["splash_md"]["create_date"]
        if current_user is None:
            data["splash_md"]["creator"] = "NONE"
        else:
            data["splash_md"]["creator"] = current_user.uid
        data["splash_md"]["edit_record"] = []
        data["splash_md"]["etag"] = str(uuid.uuid4())

        logger.debug(f"create doc in collection {0}, doc: {1}", self._collection, data)

        self._collection.insert_one(data)
        return {"uid": data["uid"], "splash_md": data["splash_md"]}

    def retrieve_one(self, current_user: User, uid) -> dict:
        return self._collection.find_one({"uid": uid}, {"_id": False})

    def retrieve_multiple(
        self,
        user: User,
        page: int = 1,
        query=None,
        page_size=10,
        # KEEP IN MIND THAT SORT ORDER MAY NOT BE CONSISTENT IF YOU HAVE EQUALITY
        # AMONG ALL OF ITS CLAUSES IN TWO DOCUMENTS.
        # IF YOU WANT TO MAKE SURE IT STAYS CONSISTENT,
        # PLACE A UID AT THE END: https://docs.mongodb.com/manual/reference/method/cursor.sort/#sort-consistency
        sort=[("splash_md.last_edit", DESCENDING), ("uid", DESCENDING)],
    ):
        if type(sort) is not list:
            raise TypeError("`sort` argument must be of type list")
        if page <= 0:
            raise BadPageArgument("Page parameter must greater than 0")

        # Calculate number of documents to skip
        skips = page_size * (page - 1)
        # Skip and limit
        if query is None:
            query = {}
        cursor = self._collection.find(query, {"_id": False})

        # Return documents
        return (
            cursor.sort(sort).collation(Collation("en_US")).skip(skips).limit(page_size)
        )

    @validate_base_metadata
    def update(self, current_user: User, data: dict, uid: str, etag=None):
        data["uid"] = uid

        current_document = MongoService.retrieve_one(self, current_user, uid)

        metadata = current_document["splash_md"]

        # If the etags don't match
        if etag is not None and etag != metadata["etag"]:
            raise EtagMismatchError(
                f"Etag argument `{etag}` does not match current etag: `{ metadata['etag'] }`",
                metadata["etag"],
            )

        if "splash_md" not in data:
            data["splash_md"] = metadata
        else:
            # If the top layer is also sending in metadata
            # then we want to merge it with the metadata already in the
            # document
            metadata.update(data["splash_md"])
            data["splash_md"] = metadata
        # Update the edit_record array and last edit timestamp
        # remove the microsecond because mongo will truncate past a certain amount of decimal places
        data["splash_md"]["last_edit"] = datetime.utcnow().replace(microsecond=0)
        data["splash_md"]["edit_record"].append(
            {"date": data["splash_md"]["last_edit"], "user": current_user.uid}
        )
        data["splash_md"]["etag"] = str(uuid.uuid4())

        status = self._collection.replace_one({"uid": uid}, data)
        if status.matched_count == 0:
            raise ObjectNotFoundError
        return {"uid": data["uid"], "splash_md": data["splash_md"]}

    def delete(self, current_user: User, uid):
        status = self._collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError


class HistoricMongoService(MongoService):
    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def _create_indexes(self):
        uid_version_unique_index = IndexModel(
            [("uid", ASCENDING), ("splash_md.version", ASCENDING)], unique=True
        )
        self._collection.create_indexes([uid_version_unique_index])


class VersionedMongoService(MongoService):
    def __init__(self, db, collection_name, revisions_collection_name):
        super().__init__(db, collection_name)
        self._versions_svc = HistoricMongoService(db, revisions_collection_name)

    @validate_versioned_metadata
    def update(self, current_user: User, data: dict, uid: str, etag=None):
        if "splash_md" not in data:
            data["splash_md"] = {}
        current_document = super().retrieve_one(current_user, uid)
        if current_document is None:
            raise ObjectNotFoundError
        data["splash_md"]["version"] = current_document["splash_md"]["version"] + 1
        result = super().update(current_user, data, uid, etag=etag)
        self._versions_svc._collection.insert_one(current_document)
        return result

    @validate_versioned_metadata
    def create(self, current_user: User, data: dict):
        if "splash_md" not in data:
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
            document = self._versions_svc._collection.find_one(
                {"$and": [{"uid": uid}, {"splash_md.version": version}]}, {"_id": False}
            )
            if document is not None:
                return document
            # If the document exists nowhere then the object was not found
            elif (
                self._versions_svc.retrieve_one(current_user, uid) is None
                and super().retrieve_one(current_user, uid) is None
            ):
                raise ObjectNotFoundError
            # If the document does exist somewhere then version was not found
            else:
                raise VersionNotFoundError

        return document

    def get_num_versions(self, current_user: User, uid):
        document = super().retrieve_one(current_user, uid)
        if document is None:
            raise ObjectNotFoundError
        num = document["splash_md"]["version"]
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


class EtagMismatchError(ValueError):
    def __init__(self, message, etag):
        self.etag = etag
        super().__init__(message, etag)
