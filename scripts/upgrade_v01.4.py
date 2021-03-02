# This python file uploads all JSON from the folder
# that should be created by the Fake_seeder
import pymongo
from datetime import datetime


def update(db_name=None):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    db = myclient[db_name]
    now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    # default splash_md value
    splash_md = {
        "creator": "NONE",
        "create_date": now,
        "last_edit": now,
        "edit_record": [],
    }

    # insert this default field into all users
    users = db["users"]
    users.update_many({}, {"$set": {"splash_md": splash_md}})

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
    pages.update_many({}, {"$set": {"splash_md": splash_md}})
    # move `document_version` to `splash_md.version`
    pages.update_many({}, {"$rename": {"document_version": "splash_md.version"}})

    # Do the same thing we did for pages except now for pages_old collection
    # which contains the past versions of pages
    pages_old = db["pages_old"]
    pages_old.update_many({}, {"$set": {"splash_md": splash_md}})
    pages_old.update_many({}, {"$rename": {"document_version": "splash_md.version"}})


update(db_name="splash_test")
