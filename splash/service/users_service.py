from .base import MongoService

class MultipleUsersAuthenticatorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UsersService(MongoService):

    def __init__(self, db, collection_name):
        super().__init__(db, collection_name)

    def get_user_authenticator(self, email):  # TODO Needs test
        """Fetches a user based on an issuer and subject. Use for example
        after receiving a JWT and validating that the user exists in the system.

        Parameters
        ----------
        issuer : str
            Identifier of the issuing authority
        subject : str
            subject id in the authority's system
        """
        users = list(self.retrieve_multiple(None, 1, query={
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
        return self.retrieve_one(None, uid)
