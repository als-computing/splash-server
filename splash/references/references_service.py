from pymongo import TEXT
from pymongo.operations import IndexModel
from . import NewReference, Reference
from ..service.base import MongoService
from ..users import User


class ReferencesService(MongoService):
    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def _create_indexes(self):
        full_text_index = IndexModel([("$**", TEXT)])
        # This allows us to ensure that all DOIs that are of type string are unique
        # which ensures that we can have multiple null DOIs but no duplicate string DOIs
        doi_index = IndexModel("DOI")
        self._collection.create_indexes([full_text_index, doi_index])
        super()._create_indexes()

    def create(self, current_user: User, reference: NewReference):
        return super().create(current_user=current_user, data=reference)

    def retrieve_one(self, current_user: User, uid) -> Reference:
        reference_dict = super().retrieve_one(current_user, uid)
        if reference_dict is None:
            return None
        return Reference(**reference_dict)

    def retrieve_multiple(
        self,
        current_user: User,
        page: int = 1,
        query=None,
        page_size=10,
    ):
        cursor = super().retrieve_multiple(current_user, page, query, page_size)
        for reference_dict in cursor:
            yield Reference(**reference_dict)

    def retrieve_by_doi(
        self,
        current_user: User,
        doi,
        page: int = 1,
        page_size=10,
    ):
        return self.retrieve_multiple(
            current_user,
            page=page,
            page_size=page_size,
            query={"DOI": {"$eq": doi, "$type": "string"}},
        )

    def search(self, current_user: User, search, page: int = 1, page_size=10):
        query = {"$text": {"$search": search}}
        return self.retrieve_multiple(
            current_user, page=page, page_size=page_size, query=query
        )

    def update(
        self,
        current_user: User,
        data: NewReference,
        uid,
        etag: str = None,
    ):
        old_data_dict = self.retrieve_one(current_user, uid)
        if old_data_dict is None:
            return None
        old_data_dict = old_data_dict.dict()

        return super().update(current_user, data, old_data_dict["uid"], etag=etag)

    def delete(self, current_user: User, uid):
        raise NotImplementedError
