#This script is meant to convert all times to the native format for BSON

import datetime
import os
import pymongo

mongo_uri = os.getenv("MONGO_DB_URI")
print(f"using {mongo_uri}")
db = pymongo.MongoClient(mongo_uri).get_database()


def update():
    collection_names = ["pages", "pages_old", "references", "teams", "users"]
    for collection_name in collection_names:
        results = convert_create_and_last_edit_dates(collection_name)
        print(
            f"{collection_name}: matched: {results.matched_count}  modified: {results.modified_count}"
        )

        results = convert_dates_in_edit_record(collection_name)

        print(f"{collection_name}: matched: {results[0]}  modified: {results[1]}")

    # pages_old = db["pages_copy"]


# results = pages_old.update_many({}, {"$unset": {"metadata":""}})
# print(
#     f"pages old: matched: {results.matched_count}  modified: {results.modified_count}"
# )


def convert_create_and_last_edit_dates(collection_name):
    collection = db[collection_name]

    results = collection.update_many(
        {},
        [
            {
                "$set": {
                    "splash_md.create_date": {
                        "$toDate": "$splash_md.create_date",
                    },
                    "splash_md.last_edit": {
                        "$toDate": "$splash_md.last_edit",
                    },
                }
            }
        ],
    )
    return results


# This converts dates in the edit_record array
def convert_dates_in_edit_record(collection_name):
    collection = db[collection_name]
    cursor = collection.find({})
    updates = []

    # iterate over every document first
    # to make sure that the cursor doesn't
    # retrieve something twice because we performed a write
    matched_count = 0
    for document in cursor:

        new_edit_record = []
        for edit in document["splash_md"]["edit_record"]:
            if type(edit["date"]) is str:
                edit["date"] = datetime.datetime.strptime(
                    edit["date"], "%Y-%m-%dT%H:%M:%S"
                )
                new_edit_record.append(edit)
            else:
                new_edit_record.append(edit)

        updates.append({"oid": document["_id"], "update": new_edit_record})
        matched_count += 1

    modified_count = 0
    for update in updates:
        result = collection.find_one_and_update(
            {"_id": update["oid"]},
            {"$set": {"splash_md.edit_record": update["update"]}},
        )
        if result is not None:
            modified_count += 1
    return matched_count, modified_count


update()