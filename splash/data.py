import logging
from bson.objectid import ObjectId
from bson.errors import InvalidId
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



class SearchService(object):
    def search(self, query, start=0, count=100):
        raise NotImplementedError

class MongoCollectionDao(Dao):
    ''' Mongo data service for mapping CRUD and search
    operations to a MongoDB. '''
    def __init__(self, collection):
        self.collection = collection

    def create(self, doc):
        logging.debug(f"update collection {0}, doc: {1}", self.collection, doc)
        uid = uuid.uuid4()
        doc['uid'] = str(uid)
        self.collection.insert_one(doc)
        return doc['uid']

    def retrieve(self, uid):
        return self.collection.find_one({"uid": uid})

    def retrieve_many(self, page, query=None, page_size=10):
        if query is None:
            # Calculate number of documents to skip
            skips = page_size * (page - 1)
            # Skip and limit
            cursor = self.collection.find().skip(skips).limit(page_size)

            # Return documents
            return cursor

        else:
            raise NotImplementedError

    def update(self, uid, doc):
        #update should not be able to change uid
        if 'uid' in doc and doc['uid'] != uid:
            raise BadIdError('Cannot change object uid')
        doc["uid"] = uid
        status = self.collection.replace_one({"uid": uid}, doc) #update_one might be more efficient, but kinda tricky
        if status.modified_count == 0:
            raise ObjectNotFoundError

    def delete(self, uid):
        status = self.collection.delete_one({"uid": uid})
        if status.deleted_count == 0:
            raise ObjectNotFoundError



class ObjectNotFoundError(Exception):
    pass


class BadIdError(Exception):
    pass
