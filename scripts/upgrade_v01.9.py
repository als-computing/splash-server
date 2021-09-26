import os
import pymongo
from pymongo.collation import Collation
from pymongo.operations import IndexModel

mongo_uri = os.getenv("MONGO_DB_URI")
print(f"using {mongo_uri}")

db = pymongo.MongoClient(mongo_uri).get_database()

doi_index = IndexModel(
    [("splash_md.archived", pymongo.ASCENDING), ("DOI", pymongo.ASCENDING)],
    collation=Collation("en_US", strength=2),
)


references = db["references"]

references.drop_index([("DOI", 1)])
references.create_indexes([doi_index])
