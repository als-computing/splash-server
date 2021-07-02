from pymongo import IndexModel
from pymongo import ASCENDING, TEXT


def create_indexes_pages_old(collection):
    uid_version_unique_index = IndexModel(
        [("uid", ASCENDING), ("splash_md.version", ASCENDING)], unique=True
    )
    collection.create_indexes([uid_version_unique_index])


def create_indexes(collection):
    uid_unique_index = IndexModel("uid", unique=True)
    creator_index = IndexModel("splash_md.creator")
    collection.create_indexes([uid_unique_index, creator_index])


def create_pages_indexes(collection):
    create_indexes(collection)
    text_index = IndexModel([("title", TEXT), ("documentation", TEXT)])
    collection.create_indexes([text_index])


def create_references_indexes(collection):
    create_indexes(collection)
    full_text_index = IndexModel([("$**", TEXT)])
    doi_index = IndexModel("DOI")
    collection.create_indexes([full_text_index, doi_index])


def create_users_indexes(collection):
    create_indexes(collection)
    text_index = IndexModel(
        [("given_name", TEXT), ("family_name", TEXT), ("email", TEXT)]
    )
    collection.create_indexes([text_index])


def create_teams_indexes(collection):
    create_indexes(collection)
    collection.create_index("name", unique=True)
