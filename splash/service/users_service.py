from splash.data.base import MongoCollectionDao
from splash.service.base import Service


class MultipleUsersAuthenticatorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UsersService(Service):

    def __init__(self, dao: MongoCollectionDao):
        super().__init__(dao)
        self.dao = dao

    def get_user_authenticator(self, email):
        """Fetches a user based on an issuer and subject. Use for example
        after receiving a JWT and validating that the user exists in the system.

        Parameters
        ----------
        issuer : str
            Identifier of the issuing authority
        subject : str
            subject id in the authority's system
        """
        users = list(self.dao.retreive_many(query={
                "authenticators.email": email
            }))

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
        return self.dao.retrieve(uid)
