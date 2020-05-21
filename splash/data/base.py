import logging
# from bson.objectid import ObjectId
# from bson.errors import InvalidId
import uuid

class Dao(object):
    '''Interface for CRUD Serverice'''

    def create(self, doc):
        raise NotImplementedError

    def retrive(self, uid):
        raise NotImplementedError

    def retreive_many(self, query=None):
        raise NotImplementedError

    def update(self, doc):
        raise NotImplementedError

    def delete(self, uid):
        raise NotImplementedError


# class MongoCollectionDao(Dao):
#     ''' Mongo data service for mapping CRUD and search
#     operations to a MongoDB. '''
#     def __init__(self, client, db_name, collection_name):
#         self._client = client
#         self._db_name = db_name
#         self._collection_name = collection_name
#         self._collection = None
        
#     def _get_collection(self):
#         if self._collection is None:
#             print(f'{self._client},  {self._db_name}   {self._collection_name}')
#             self._collection = self._client[self._db_name][self._collection_name]
#             print(self._collection)
#             return self._collection

#     def create(self, doc):
#         logging.debug(f"create doc in collection {0}, doc: {1}", self._collection_name, doc)
#         uid = uuid.uuid4()
#         doc['uid'] = str(uid)
#         self.collection.insert_one(doc)
#         return doc['uid']

#     def retrieve(self, uid):
#         return self._get_collection().find_one({"uid": uid})

#     def retrieve_multiple(self, page, query=None, page_size=10):
#         if query is None:
#             # Calculate number of documents to skip
#             skips = page_size * (page - 1)
#             num_results = self._get_collection().find().count()
#             # Skip and limit
#             cursor = self._get_collection().find().skip(skips).limit(page_size)

#             # Return documents
#             return num_results, cursor

#         else:
#             raise NotImplementedError

#     def update(self, doc):
#         # update should not be able to change uid
#         if 'uid' not in doc:
#             raise BadIdError('Cannot change object uid')
#         # update_one might be more efficient, but kinda tricky
#         status = self._get_collection().replace_one({"uid": doc['uid']}, doc)
#         if status.modified_count == 0:
#             raise ObjectNotFoundError

#     def delete(self, uid):
#         status = self._get_collection().delete_one({"uid": uid})
#         if status.deleted_count == 0:
#             raise ObjectNotFoundError

class MongoCollectionDao(Dao):
    ''' Mongo data service for mapping CRUD and search
    operations to a MongoDB. '''
    def __init__(self, db, collection_name):
        self._db = db
        self._collection = db[collection_name]
        
    def create(self, doc):
        logging.debug(f"create doc in collection {0}, doc: {1}", self._collection, doc)
        uid = uuid.uuid4()
        doc['uid'] = str(uid)
        self._collection.insert_one(doc)
        return doc['uid']

    def retrieve(self, uid):
        return self._collection.find_one({"uid": uid})

    def retrieve_paged(self, page, query=None, page_size=10):
        if query is None:
            # Calculate number of documents to skip
            skips = page_size * (page - 1)
            num_results = self._collection.find().count()
            # Skip and limit
            cursor = self._collection.find().skip(skips).limit(page_size)

            # Return documents
            return num_results, cursor

        else:
            raise NotImplementedError

    def retreive_many(self, query=None):
        return self._collection.find(query)

    def update(self, doc):
        # update should not be able to change uid
        if 'uid' not in doc:
            raise BadIdError('Cannot change object uid')
        # update_one might be more efficient, but kinda tricky
        status = self._collection.replace_one({"uid": doc['uid']}, doc)
        if status.modified_count == 0:
            raise ObjectNotFoundError

    def delete(self, uid):
        status = self._collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError

class ObjectNotFoundError(Exception):
    pass


class BadIdError(Exception):
    pass

