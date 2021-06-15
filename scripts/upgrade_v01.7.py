#This upgrade script removes all metadata properties from all the pages. 
# This is because we are no longer supporting the side metadata properties within the UI.
import os
import pymongo

def update():
    mongo_uri = os.getenv('MONGO_DB_URI')
    print(f'using {mongo_uri}')
    db = pymongo.MongoClient(mongo_uri).get_database()
    pages = db["pages"]

    results = pages.update_many({}, {"$unset": {"metadata":""}})
    print(
        f"pagess: matched: {results.matched_count}  modified: {results.modified_count}"
    )

    pages_old = db["pages_old"]
    results = pages_old.update_many({}, {"$unset": {"metadata":""}})
    print(
        f"pages old: matched: {results.matched_count}  modified: {results.modified_count}"
    )


update()