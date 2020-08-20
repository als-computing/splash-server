import json
import os
from collections import namedtuple
from splash.models.users import UserModel

# from pydantic import BaseModel

from splash.data.base import MongoCollectionDao

ValidationIssue = namedtuple('ValidationIssue', 'description, location, exception')


class BadPageArgument(Exception):
    pass


class Service():

    def __init__(self, dao: MongoCollectionDao):
        self.dao = dao

    # def validate(self, data):
    #     errors = self.validator.iter_errors(data)
    #     return_errs = []
    #     for error in errors:
    #         return_errs.append(ValidationIssue(error.message, str(error.path), error))
    #     return return_errs

    def create(self, current_user: UserModel, data):
        return self.dao.create(data)

    def retrieve_one(self, current_user: UserModel, uid):
        return self.dao.retrieve(uid)

    def retrieve_multiple(self,
                          current_user: UserModel,
                          page: int,
                          query=None,
                          page_size=10):
        if not is_integer(page):
            raise BadPageArgument('Page number must be an integer,\
                            represented as an integer, string, or float.')
        if page <= 0:
            raise BadPageArgument("Page parameter must be positive")

        cursor = self.dao.retrieve_paged(page, query, page_size=0)
        return list(cursor)
        # return 

    def update(self, current_user: UserModel, data):
        return self.dao.update(data)

    def delete(self, current_user: UserModel, uid):
        raise self.dao.delete(uid)


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()
