from . import Compound, NewCompound
from ..service import MongoService
from ..users import User


class CompoundsService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__( db, collection_name)

    def create(self, current_user: User, Compound: NewCompound) -> str:
        return super().create(current_user, Compound.dict())

    def retrieve_one(self, current_user: User, uid: str) -> Compound:
        Compound_dict = super().retrieve_one(current_user, uid)
        if Compound_dict is None:
            return None
        return Compound(**Compound_dict)

    def retrieve_multiple(self,
                          current_user: User,
                          page: int = 1,
                          query=None,
                          page_size=10):
        cursor = super().retrieve_multiple(current_user, page, query, page_size)
        for compound_dict in cursor:
            yield Compound(**compound_dict)

    def update(self, current_user: User, data: Compound, uid: str):
        return super().update(current_user, data.dict(), uid)

    def delete(self, current_user: User, uid):
        raise NotImplementedError

    def get_user_compounds(self, request_user: User, uid: str):
        # find Compounds that contain the member by uid
        query = {
            "members." + uid: {"$exists": True}
        }
        compounds_dicts = list(self.retrieve_multiple(request_user, page=1, query=query))
        for compound_dict in compounds_dicts:
            yield Compound(**compound_dict)