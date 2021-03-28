import os
from re import match
import uuid
import pymongo

#mongo_uri = os.getenv("MONGO_DB_URI")
db = pymongo.MongoClient("localhost").splash
#print(f"using {mongo_uri}")


def set_etags_for_collection(collection_name):
    users = db[collection_name]
    cursor = users.find({})
    oids = []

    # iterate over every document first
    # to make sure that the cursor doesn't
    # retrieve something twice because we performed a write
    matched_count = 0
    for document in cursor:
        oids.append(document["_id"])
        matched_count += 1

    modified_count = 0
    for oid in oids:
        etag = str(uuid.uuid4())
        result = users.find_one_and_update({"_id": oid}, {"$set": {"splash_md.etag": etag}})
        if result is not None:
            modified_count += 1
    return matched_count, modified_count


def update():

    matched_count, modified_count = set_etags_for_collection("users")
    print(
        f"users: matched: {matched_count}  modified: {modified_count}"
    )

    matched_count, modified_count = set_etags_for_collection("teams")
    print(
        f"teams: matched: {matched_count}  modified: {modified_count}"
    )

    matched_count, modified_count = set_etags_for_collection("references")
    print(
        f"references: matched: {matched_count}  modified: {modified_count}"
    )

    matched_count, modified_count = set_etags_for_collection("pages")
    print(
        f"pages: matched: {matched_count}  modified: {modified_count}"
    )

    matched_count, modified_count = set_etags_for_collection("pages_old")
    print(
        f"pages_old: matched: {matched_count}  modified: {modified_count}"
    )


update()