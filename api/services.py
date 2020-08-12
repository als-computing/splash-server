from pymongo import MongoClient
from splash.categories.users.users_service import UserService
from splash.categories.runs.runs_service import RunService
from splash.categories.compounds.compounds_service import CompoundsService
from splash.data.base import MongoCollectionDao

db = MongoClient().splash


def get_users_service():
    return UserService(MongoCollectionDao(MongoClient().splash, 'users'))


def get_compounds_service():
    return CompoundsService(MongoCollectionDao(MongoClient().splash, 'compounds'))

def get_runs_service():
    return RunService()
