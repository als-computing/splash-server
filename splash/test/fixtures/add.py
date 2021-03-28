import os

from fastapi.testclient import TestClient
import mongomock
from mongomock import collection
import pytest

from splash.pages.pages_routes import set_pages_service
from splash.pages.pages_service import PagesService
from splash.references.references_routes import set_references_service
from splash.references.references_service import ReferencesService
from splash.users import NewUser
from splash.users.users_routes import set_users_service
from splash.users.users_service import UsersService
from splash.runs.runs_routes import set_runs_service
from splash.runs.runs_service import RunsService, TeamRunChecker
from splash.teams import NewTeam
from splash.teams.teams_routes import set_teams_service
from splash.teams.teams_service import TeamsService
from splash.api.auth import create_access_token, set_services as set_auth_services

from splash.api.main import app

os.environ['TOKEN_SECRET_KEY'] = "the_question_to_the_life_the_universe_and_everything"
os.environ['GOOGLE_CLIENT_ID'] = "Gollum"
os.environ['GOOGLE_CLIENT_SECRET'] = "the_one_ring"

test_user = NewUser(
    given_name="ford",
    family_name="prefect",
    email="ford@beetleguice.planet")

token_info = {"sub": None, "scopes": ['splash']}

db = mongomock.MongoClient().db
users_svc = UsersService(db, 'users')
pages_svc = PagesService(db, 'pages', 'pages_old')
references_svc = ReferencesService(db, 'references')
teams_svc = TeamsService(db, 'teams')
runs_svc = RunsService(teams_svc, TeamRunChecker())
set_auth_services(users_svc)
set_pages_service(pages_svc)
set_references_service(references_svc)
set_runs_service(runs_svc)
set_teams_service(teams_svc)
set_users_service(users_svc)


def collationMock(self, collation):
    assert collation.document == {'locale':'en_US'}
    return self


@pytest.fixture(scope="function", autouse=True)
def mock_collation_prop(monkeypatch):
    print('hello')
    monkeypatch.setattr(collection.Cursor, "collation", collationMock)


@pytest.fixture
def mongodb():
    return db


@pytest.fixture
def splash_client(mongodb, monkeypatch):
    uid = users_svc.create(None, test_user)["uid"]
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


leader = {

        'given_name': 'leader',
        'family_name': 'lemond',
        'email': 'greg@lemond.io',
        'authenticators': [
            {
                'issuer': 'aso',
                'email': 'greg@aso.com',
                'subject': 'randomsubject'
            }
        ]
    }

same_team = {

        'given_name': 'same_team',
        'family_name': 'hinault',
        'email': 'bernard@hinault.io',
        'authenticators': [
            {
                'issuer': 'aso',
                'email': 'bernard@aso.com',
                'subject': 'badger'
            }
        ]
    }

other_team = {

        'given_name': 'other_team',
        'family_name': 'fignon',
        'email': 'laurent@fignon.com',
        'authenticators': [
            {
                'issuer': 'aso',
                'email': 'laurent@aso.com',
                'subject': 'glasses'
            }
        ]
    }


@pytest.fixture(scope="session", autouse=True)
def users():
    user_leader_uid = users_svc.create(None, NewUser(**leader))["uid"]
    user_same_team_uid = users_svc.create(None, NewUser(**same_team))["uid"]
    user_other_team_uid = users_svc.create(None, NewUser(**other_team))["uid"]
    users = {}
    users['leader'] = users_svc.retrieve_one(None, user_leader_uid)
    users['same_team'] = users_svc.retrieve_one(None, user_same_team_uid)
    users['other_team'] = users_svc.retrieve_one(None, user_other_team_uid)
    return users


@pytest.fixture
def teams_service(mongodb, users):
    teams_service = TeamsService(mongodb, "teams")
    teams_service.create(users['leader'], NewTeam(**{"name": "other_team",
                                              "members": {users['other_team'].uid: ['leader']}}))

    teams_service.create(users['leader'], NewTeam(**{'name': 'same_team',
                                              'members': {
                                                    users['leader'].uid: ['leader'],
                                                    users['same_team'].uid: ['domestique']}
                                                }))

    return teams_service
