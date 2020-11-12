import pytest
from splash.data.base import MongoCollectionDao
from splash.service.teams_service import TeamsService
from splash.models.users import UserModel


@pytest.fixture
def request_user():
    return UserModel(
                    uid="foobar",
                    given_name="ford",
                    family_name="prefect",
                    email="ford@beetleguice.planet")

@pytest.fixture
def teams_service(mongodb, request_user):
    teams_service = TeamsService(MongoCollectionDao(mongodb, "teams"))
    teams_service.create(request_user, {"name": "banesto",
                                        "members": {"indurain": ['legend'],
                                                    "delgado": ['domestique'],
                                                    "shared_user": ['domestique']}})
    teams_service.create(request_user, {"name": "motorola",
                                        "members": {"armstrong": ['doper'],
                                                    "landis": ['domestique'],
                                                    "shared_user": ['domestique']}})
    return teams_service


def test_get_user_teams(teams_service: TeamsService, request_user):
    teams = teams_service.get_user_teams(request_user, 'indurain')
    assert len(teams) == 1
    assert teams[0].name == 'banesto'

    teams = teams_service.get_user_teams(request_user, 'shared_user')
    assert len(teams) == 2
    assert teams[0].name == 'banesto'
    assert teams[1].name == 'motorola'
