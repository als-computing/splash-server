from . import NewReference, Reference
from ..service.base import MongoService
from ..users import User


class ReferencesService(MongoService):
    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)
        self._collection.create_index("DOI", unique=True)

    def create(self, current_user: User, reference: NewReference):
        
        return super().create(current_user=current_user, data=reference)

    def retrieve_one(
        self, current_user: User, uid: str = None, doi: str = None
    ) -> Reference:
        if uid is None and doi is None:
            raise TypeError("either param uid or doi must be a string.")
        if uid is not None and doi is not None:
            raise TypeError("either param uid or doi must be None")
        if uid:
            reference_dict = super().retrieve_one(current_user, uid)
            if reference_dict is None:
                return None
            return Reference(**reference_dict)
        if doi:
            reference_dict = self._collection.find_one({"DOI": doi}, {"_id": False})
            if reference_dict is None:
                return None
            return Reference(**reference_dict)

    def retrieve_multiple(
        self, current_user: User, page: int = 1, query=None, page_size=10
    ):
        cursor = super().retrieve_multiple(current_user, page, query, page_size)
        for reference_dict in cursor:
            yield Reference(**reference_dict)

    def search(self, current_user: User, search, page: int = 1, page_size=10):
        regex_query = {"$regex": search, "$options": "i"}
        query = {
            "$or": [
                {"title": regex_query},
                {"author.given": regex_query},
                {"author.family": regex_query},
                {"author.literal": regex_query},
                {"author.dropping-particle": regex_query},
                {"author.non-dropping-particle": regex_query},
                {"author.suffix": regex_query},
            ]
        }
        return self.retrieve_multiple(
            current_user, page=page, page_size=page_size, query=query
        )

    def update(
        self, current_user: User, data: NewReference, uid: str = None, doi: str = None
    ):
        old_data_dict = self.retrieve_one(current_user, uid=uid, doi=doi)
        if old_data_dict is None:
            return None
        old_data_dict = old_data_dict.dict()

        data["splash_date_created"] = old_data_dict["splash_date_created"]
        data["splash_user_uid"] = old_data_dict["splash_user_uid"]

        return super().update(current_user, data, old_data_dict["uid"])

    def delete(self, current_user: User, uid):
        raise NotImplementedError
