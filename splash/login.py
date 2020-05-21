from flask import current_app
from flask_login import UserMixin
from splash.categories.users.users_service import UserNotFoundException


class User(UserMixin):
    def __init__(self, uid, email, given_name, family_name, is_active):
        self._id = uid
        # self.uid = uid
        self.email = email
        self.given_name = given_name
        self.family_name = family_name
        self._is_active = is_active
        # self.is_authenticated = ?? #what to do with this mixin property?

    def __iter__(self):
        values = self.__dict__
        values['uid'] = self._id
        yield from values.items()

    @property
    def uid(self):
        return self._id

    @property
    def id(self):
        return self._id

