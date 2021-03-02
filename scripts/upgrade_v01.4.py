import os
import pymongo
from datetime import datetime


def update():
    mongo_uri = os.getenv('MONGO_DB_URI')
    print(f'using {mongo_uri}')
    db = pymongo.MongoClient(mongo_uri).get_database()
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    # default splash_md value
    splash_md = {
        "creator": "NONE",
        "create_date": now,
        "last_edit": now,
        "edit_record": [],
    }    # insert this default field into all users
    users = db["users"]
    results = users.update_many({}, {"$set": {"splash_md": splash_md}})
    print(f'users: matched: {results.matched_count}  modified: {results.modified_count}')    
    # insert this default field into all teams
    teams = db["teams"]
    teams.update_many({}, {"$set": {"splash_md": splash_md}})
    references = db["references"]
    # Insert this default field into all references
    references.update_many({}, {"$set": {"splash_md": splash_md}})
    # Delete `splash_date_created`
    # move `splash_user_uid` to `creator` in `splash_md`
    references.update_many(
        {},
        {
            "$unset": {
                "splash_date_created": "",
            },
            "$rename": {
                "splash_user_uid": "splash_md.creator",
            }
        },
    )    
    pages = db["pages"]
    # Set default  `splash_md`
    results = pages.update_many({}, {"$set": {"splash_md": splash_md}})
    print(f'pages add: matched: {results.matched_count}  modified: {results.modified_count}')
    # move `document_version` to `splash_md.version`
    results = pages.update_many({}, {"$rename": {"document_version": "splash_md.version"}})
    print(f'pages move version: matched: {results.matched_count}  modified: {results.modified_count}')
    # Do the same thing we did for pages except now for pages_old collection
    # which contains the past versions of pages
    results = pages_old = db["pages_old"]
    results = pages_old.update_many({}, {"$set": {"splash_md": splash_md}})
    print(f'pages old set: matched: {results.matched_count}  modified: {results.modified_count}')
    results = pages_old.update_many({}, {"$rename": {"document_version": "splash_md.version"}})
    print(f'pages old  move version: matched: {results.matched_count}  modified: {results.modified_count}')
    update()
