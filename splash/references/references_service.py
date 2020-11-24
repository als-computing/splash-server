from datetime import datetime
from . import NewReference
from ..service import MongoService
from ..users import User


class ReferencesService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def create(self, current_user: User, reference: NewReference):
        reference['date_created'] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        reference['user_uid'] = current_user.uid
        return super().create(current_user=current_user, data=reference)
