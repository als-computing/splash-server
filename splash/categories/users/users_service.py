import jsonschema
import json
from splash.data.base import Dao
from splash.service.base import Service, ValidationIssue
from splash.categories.utils import openSchema

USER_SCHEMA = openSchema('user_schema.json', __file__)


class MultipleUsersAuthenticatorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UserService(Service):

    def __init__(self, dao: Dao):
        super().__init__(dao, USER_SCHEMA)
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
