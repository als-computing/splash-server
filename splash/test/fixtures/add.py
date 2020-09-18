import os

os.environ['TOKEN_SECRET_KEY'] = "the_question_to_the_life_the_universe_and_everything"
os.environ['GOOGLE_CLIENT_ID'] = "Gollum"
os.environ['GOOGLE_CLIENT_SECRET'] = "the_one_ring"

import pytest
import mongomock

from splash.api import set_service_provider, get_service_provider as services
from splash.service import ServiceProvider
from splash.api.routers import auth
from splash.models.users import NewUserModel
from fastapi.testclient import TestClient

test_user = NewUserModel(
    given_name="ford",
    family_name="prefect",
    email="ford@beetleguice.planet")

token_info = {"sub": None, "scopes": ['splash']}

db = mongomock.MongoClient().db
set_service_provider(ServiceProvider(db))
from splash.api.main import app

@pytest.fixture
def mongodb():
    return db


@pytest.fixture
def splash_client(mongodb, monkeypatch):
    uid = services().users.create(test_user, dict(test_user))
    token_info['sub'] = uid
    client = TestClient(app)

    return client


@pytest.fixture
def token_header():
    token = auth.create_access_token(token_info)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def api_url_root():
    return "/api/v1"
