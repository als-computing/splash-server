import os

from fastapi.testclient import TestClient
import mongomock
from mongomock import collection
import pytest

from splash.pages.pages_routes import set_pages_service
from splash.pages.pages_service import PagesService
from splash.references.references_routes import set_references_service
from splash.references.references_service import ReferencesService
from splash.users import NewUser, User
from splash.users.users_routes import set_users_service
from splash.users.users_service import UsersService
from splash.runs.runs_routes import set_runs_service
from splash.runs.runs_service import RunsService, TeamRunChecker
from splash.teams import NewTeam
from splash.teams.teams_routes import set_teams_service
from splash.teams.teams_service import TeamsService
from splash.api.auth import create_access_token, set_services as set_auth_services


from splash.api.main import app
API_URL_ROOT = "/splash/api/v1"
os.environ["TOKEN_SECRET_KEY"] = "the_question_to_the_life_the_universe_and_everything"
os.environ["GOOGLE_CLIENT_ID"] = "Gollum"
os.environ["GOOGLE_CLIENT_SECRET"] = "the_one_ring"


db = mongomock.MongoClient().db
users_svc = UsersService(db, "users")
pages_svc = PagesService(db, "pages", "pages_old")
references_svc = ReferencesService(db, "references")
teams_svc = TeamsService(db, "teams")
runs_svc = RunsService(teams_svc, TeamRunChecker())
set_auth_services(users_svc)
set_pages_service(pages_svc)
set_references_service(references_svc)
set_runs_service(runs_svc)
set_teams_service(teams_svc)
set_users_service(users_svc)


def collationMock(self, collation):
    assert collation.document == {"locale": "en_US"}
    return self


@pytest.fixture(scope="function", autouse=True)
def mock_collation_prop(monkeypatch):
    monkeypatch.setattr(collection.Cursor, "collation", collationMock)


@pytest.fixture
def mongodb():
    return db

# @pytest.fixture
# def fresh_mongodb():
#     return mongomock.MongoClient().db


@pytest.fixture
def test_user1():
    return NewUser(
        given_name="ford", family_name="prefect", email="ford@beetleguice.planet", 
    )


#@pytest.fixture
#def test_user2():
#   return NewUser(
#        given_name="Marvin", family_name="The android", email="marvin@heartofgold.net"
#    )


token_info1 = {"sub": None, "scopes": ["splash"]}
token_info2 = {"sub": None, "scopes": ["splash"]}

admin_user1 = User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "f672367e-c534-4f4a-9e5a-0941dbab2d1c",
            "admin": True
        },
        uid="foobar1",
        given_name="Sauron",
        family_name="The Dark Lord",
        email="Sauron@mordor.net",
    )

admin_user2 = NewUser(
        splash_md={
            "admin": True
        },
        given_name="Melkor",
        family_name="The Ainur",
        email="Melkor@silmarillion.com",
    )

@pytest.fixture
def splash_client(mongodb, test_user1, monkeypatch):
    uid = users_svc.create(admin_user1, admin_user2)["uid"]
    token_info1["sub"] = uid
    client = TestClient(app)
    return client


@pytest.fixture
def token_header():
    token = create_access_token(token_info1)
    return {"Authorization": f"Bearer {token}"}


#@pytest.fixture
#def token_header2():
#    token = create_access_token(token_info2)
#    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def api_url_root():
    return API_URL_ROOT


leader = {
    "given_name": "leader",
    "family_name": "lemond",
    "email": "greg@lemond.io",
    "authenticators": [
        {"issuer": "aso", "email": "greg@aso.com", "subject": "randomsubject"}
    ],
}

same_team = {
    "given_name": "same_team",
    "family_name": "hinault",
    "email": "bernard@hinault.io",
    "authenticators": [
        {"issuer": "aso", "email": "bernard@aso.com", "subject": "badger"}
    ],
}

other_team = {
    "given_name": "other_team",
    "family_name": "fignon",
    "email": "laurent@fignon.com",
    "authenticators": [
        {"issuer": "aso", "email": "laurent@aso.com", "subject": "glasses"}
    ],
}


@pytest.fixture(scope="session", autouse=True)
def users():
    user_leader_uid = users_svc.create(admin_user1, NewUser(**leader))["uid"]
    user_same_team_uid = users_svc.create(admin_user1, NewUser(**same_team))["uid"]
    user_other_team_uid = users_svc.create(admin_user1, NewUser(**other_team))["uid"]
    users = {}
    users["leader"] = users_svc.retrieve_one(admin_user1, user_leader_uid)
    users["same_team"] = users_svc.retrieve_one(admin_user1, user_same_team_uid)
    users["other_team"] = users_svc.retrieve_one(admin_user1, user_other_team_uid)
    return users


@pytest.fixture
def teams_service(mongodb, users):
    teams_service = TeamsService(mongodb, "teams")
    db.teams.delete_many({})
    teams_service.create(
        users["leader"],
        NewTeam(
            **{"name": "other_team", "members": {users["other_team"].uid: ["leader"]}}
        ),
    )

    teams_service.create(
        users["leader"],
        NewTeam(
            **{
                "name": "same_team",
                "members": {
                    users["leader"].uid: ["leader"],
                    users["same_team"].uid: ["domestique"],
                },
            }
        ),
    )

    return teams_service
