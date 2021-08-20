# This script attempts to create a partial index on the references collection.
# If we cannot do this it will throw an error, letting the user know of that so that they can fix it manually

import os
import pymongo
from pymongo.operations import IndexModel

mongo_uri = os.getenv("MONGO_DB_URI")
print(f"using {mongo_uri}")

db = pymongo.MongoClient(mongo_uri).get_database()

doi_index_to_be_dropped = IndexModel("DOI")

doi_index = IndexModel(
            "DOI", partialFilterExpression={"DOI": {"$type": "string"}}, unique=True
        )
references = db['references']

references.drop_index([('DOI', 1)])
references.create_indexes([doi_index])

