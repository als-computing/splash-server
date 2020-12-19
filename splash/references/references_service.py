from datetime import datetime
from . import NewReference, Reference
from ..service import MongoService
from ..users import User


class ReferencesService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)
        self._collection.create_index('DOI', unique=True)

    def create(self, current_user: User, reference: NewReference):
        reference['splash_date_created'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        reference['splash_user_uid'] = current_user.uid
        return super().create(current_user=current_user, data=reference)

    def retrieve_one(self, current_user: User, uid: str = None, doi: str = None) -> Reference:
        if uid is None and doi is None:
            raise TypeError("either param uid or doi must be a string.")
        if uid is not None and doi is not None:
            raise TypeError("either param uid or doi must be None")
        if uid:
            Reference_dict = super().retrieve_one(current_user, uid)
            if Reference_dict is None:
                return None
            return Reference(**Reference_dict)
        if doi:
            Reference_dict = self._collection.find_one({"DOI": doi}, {'_id': False})
            if Reference_dict is None:
                return None
            return Reference(**Reference_dict)

    def retrieve_multiple(self,
                          current_user: User,
                          page: int = 1,
                          query=None,
                          page_size=10):
        cursor = super().retrieve_multiple(current_user, page, query, page_size)
        for Reference_dict in cursor:
            yield Reference(**Reference_dict)

    def update(self, current_user: User, data: NewReference, uid: str=None, doi: str=None):
        if uid is None and doi is None:
            raise TypeError("either param uid or doi must be a string.")
        if uid is not None and doi is not None:
            raise TypeError("either param uid or doi must be None")
        old_data_dict = None
        if uid is not None:
            old_data_dict = self.retrieve_one(current_user, uid=uid)
        if doi is not None:
            old_data_dict = self.retrieve_one(current_user, doi=doi)

        if old_data_dict is None:
            return None
        data['date_user_created'] = old_data_dict['date_user_created']
        data['user_uid'] = old_data_dict['user_uid']

        return super().update(current_user, new_data_dict, old_data_dict['uid'])

    def delete(self, current_user: User, uid):
        raise NotImplementedError
