import pytest
from splash.teams.teams_service import TeamsService
from splash.teams import NewTeam
from splash.users import User
from freezegun import freeze_time


@pytest.fixture
def request_user():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
        },
        uid="foobar",
        given_name="ford",
        family_name="prefect",
        email="ford@beetleguice.planet",
    )


@pytest.fixture
def teams_service(mongodb, request_user):
    teams_service = TeamsService(mongodb, "teams")
    with freeze_time("2020-02-9T13:40:53", tz_offset=-4, auto_tick_seconds=15):
        teams_service.create(
            request_user,
            NewTeam(
                **{
                    "name": "banesto",
                    "members": {
                        "indurain": ["legend"],
                        "delgado": ["domestique"],
                        "shared_user": ["domestique"],
                    },
                }
            ),
        )
        teams_service.create(
            request_user,
            NewTeam(
                **{
                    "name": "motorola",
                    "members": {
                        "armstrong": ["doper"],
                        "landis": ["domestique"],
                        "shared_user": ["domestique"],
                    },
                }
            ),
        )
    return teams_service


def test_get_user_teams(teams_service: TeamsService, request_user):
    teams = list(teams_service.get_user_teams(request_user, "indurain"))
    assert len(teams) == 1
    assert teams[0].name == "banesto"

    teams = list(teams_service.get_user_teams(request_user, "shared_user"))
    assert len(teams) == 2
    assert teams[0].name == "motorola"
    assert teams[1].name == "banesto"
