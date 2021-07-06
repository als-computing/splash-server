from pymongo import ASCENDING, DESCENDING, TEXT
from pymongo.operations import IndexModel
from ..users import NewUser, User
from ..service.base import MongoService


class MultipleUsersAuthenticatorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UsersService(MongoService):
    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def _create_indexes(self):
        text_index = IndexModel(
            [("given_name", TEXT), ("family_name", TEXT), ("email", TEXT)]
        )
        sort_index = IndexModel([("family_name", ASCENDING), ("splash_md.last_edit", DESCENDING)])
        self._collection.create_indexes([text_index, sort_index])
        super()._create_indexes()

    def create(self, current_user: User, new_user: NewUser) -> str:
        return super().create(current_user, new_user.dict())

    def retrieve_one(self, current_user: User, uid: str) -> User:
        user_dict = super().retrieve_one(current_user, uid)
        if user_dict is None:
            return None
        return User(**user_dict)

    def retrieve_multiple(
        self,
        current_user: User,
        page: int = 1,
        query=None,
        page_size=10,
        sort=[("family_name", ASCENDING), ("splash_md.last_edit", DESCENDING)],
    ):
        cursor = super().retrieve_multiple(current_user, page, query, page_size, sort)
        for user_dict in cursor:
            yield User(**user_dict)

    def update(self, current_user: User, new_user: NewUser, uid: str, etag: str = None):
        return super().update(current_user, new_user.dict(), uid, etag=etag)

    def delete(self, current_user: User, uid):
        raise NotImplementedError

    def get_user_authenticator(self, current_user: User, email):  # TODO Needs test
        """Fetches a user based on an issuer and subject. Use for example
        after receiving a JWT and validating that the user exists in the system.

        Parameters
        ----------
        issuer : str
            Identifier of the issuing authority
        subject : str
            subject id in the authority's system
        """
        users = list(
            self.retrieve_multiple(current_user, query={"authenticators.email": email})
        )

        if len(users) == 0:
            raise UserNotFoundException()
        if len(users) > 1:
            raise MultipleUsersAuthenticatorException()
        return users[0]

    def insecure_get_user(self, uid: str):
        """For checking that a user exists before having a user. Does not
        require a user id

        Parameters
        ----------
        uid : str
            uid of user to query

        Returns
        -------
        dict
            user info
        """
        return self.retrieve_one(None, uid)
