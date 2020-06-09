import jsonschema
import json
from splash.data.base import Dao
from splash.service.base import Service, ValidationIssue
import os

dirname = os.path.dirname(__file__)
user_schema_file = open(os.path.join(dirname, "user_schema.json"))
USER_SCHEMA = json.load(user_schema_file)
user_schema_file.close()


class MultipleUsersAuthenticatorException(Exception):
    pass


class UserNotFoundException(Exception):
    pass


class UserService(Service):

    def __init__(self, dao: Dao):
        super().__init__(self)
        self.dao = dao
        self.validator = jsonschema.Draft7Validator(USER_SCHEMA)

    def validate(self, data):
        errors = self.validator.iter_errors(data)
        return_errs = []
        for error in errors:
            return_errs.append(ValidationIssue(error.message, str(error.path), error))
        return return_errs

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
