from pymongo import MongoClient

from .users_service import UsersService
from .runs_service import RunsService
from .compounds_service import CompoundsService

# service_provider = ServiceProvider()

# def init_service_provider(db):
#     service_provider.init(db)

# class ServiceProvider():
#     """ Provides a single interface for constructing services based on a database instance.
#         This is used as a global for service reousrces like fastapi.
#     """

#     def __init__(self, db: MongoClient):
#         self._users_service = UsersService(db, 'users')
#         self._compounds_service = CompoundsService(db, 'compounds')
#         self._runs_service = RunsService()

#     def set_db(db)

#     @property
#     def users(self):
#         return self._users_service

#     @property
#     def compounds(self):
#         return self._compounds_service

#     @property
#     def runs(self):
#         return self._runs_service


