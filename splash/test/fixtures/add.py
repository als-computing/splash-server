import os

os.environ['TOKEN_SECRET_KEY'] = "the_question_to_the_life_the_universe_and_everything"
os.environ['GOOGLE_CLIENT_ID'] = "Gollum"
os.environ['GOOGLE_CLIENT_SECRET'] = "the_one_ring"

from fastapi.testclient import TestClient
import pytest
import mongomock


from splash.models.users import NewUserModel
from splash.api.config import ConfigStore
from splash.compounds.compounds_routes import set_compounds_service
from splash.compounds.compounds_service import CompoundsService
from splash.users.users_routes import set_users_service
from splash.users.users_service import UsersService
from splash.runs.runs_routes import set_runs_service
from splash.runs.runs_service import RunsService
from splash.api.auth import  create_access_token, set_services as set_auth_services
from splash.api.main import app

test_user = NewUserModel(
    given_name="ford",
    family_name="prefect",
    email="ford@beetleguice.planet")

token_info = {"sub": None, "scopes": ['splash']}

db = mongomock.MongoClient().db
users_svc = UsersService(db, 'users')
compounds_svc = CompoundsService(db, 'compounds')
runs_svc = RunsService()
set_users_service(users_svc)
set_compounds_service(compounds_svc)
set_runs_service(runs_svc)
set_auth_services(users_svc)


@pytest.fixture
def mongodb():
    return db


@pytest.fixture
def splash_client(mongodb, monkeypatch):
    uid = users_svc.create(test_user, dict(test_user))
    token_info['sub'] = uid
    client = TestClient(app)

    return client


@pytest.fixture
def token_header():
    token = create_access_token(token_info)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def api_url_root():
    return "/api/v1"
