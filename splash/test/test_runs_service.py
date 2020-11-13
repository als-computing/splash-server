
from typing import List

from pydantic import parse_obj_as
import pytest

from splash.runs.runs_service import RunsService, TeamRunChecker
from splash.teams.service import TeamsService
from splash.teams.models import NewTeam, Team
from splash.models.users import UserModel

# from .data_teams_runs import teams, catalog, user_leader, user_owner, user_other_team


@pytest.fixture
def teams_service(mongodb, ):
    teams_service = TeamsService(mongodb, "teams")
    teams_service.create("foobar", NewTeam(**{"name": "banesto",
                                           "members": {"indurain": ['legend'],
                                                       "delgado": ['domestique'],
                                                       "lemond": ['leader'],
                                                       "shared_user": ['domestique']}}))
    teams_service.create("foobar", NewTeam(**{"name": "motorola",
                                           "members": {"armstrong": ['doper'],
                                                       "landis": ['domestique'],
                                                       "shared_user": ['domestique']}}))
    teams_service.create("foobar", NewTeam(**{'name': 'la_vie_claire',
                                              'members': {
                                                    'lemond': ['member', 'leader'],
                                                    'hinault': ['member', 'leader', 'owner'],
                                                    'hampsten': ['member']}}))
    return teams_service


def test_get_runs_auth(monkeypatch, mongodb, teams_service):
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', catalog)
    runs = runs_service.get_runs(user_leader, list(catalog.keys())[0])
    assert runs is not None and len(runs) == 2
    runs = runs_service.get_runs(user_other_team, list(catalog.keys())[0])
    assert len(runs) == 0


class MockRun():
    def __init__(self, run_user_id, team):
        self.metadata = {
            'start': {
                'user_id': run_user_id,
                'team': team,
                'projections': [
                    {
                        'name': 'foo',
                        'version': '1.0',
                        'configuration': 'why is this required?',
                        'projection': {
                            'collection_team': {
                                'type': 'linked',
                                'location': 'start',
                                'field': 'team'
                            }
                        }
                    }
                ]
            }
        }


catalog = {
    "tour_winners": {
            '85': MockRun('bernard_hinault', 'la_vie_claire'),
            # same team as hinault...for now
            '86': MockRun('greg_lemond', 'la_vie_claire'),
            '87': MockRun('stephen_roche', 'carrera'),
            '88': MockRun('pedro_delgado', 'cafe_de_columbia'),
            # lemond came back with different team, like a grad student in a different lab
            '89': MockRun('greg_lemond', 'ADR')
    }
}

lemond = {
        'uid': 'lemond',
        'given_name': 'greg',
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

hinault = {
        'uid': 'hinault',
        'given_name': 'bernard',
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
hampsten = {
        'uid': 'hampsten',
        'given_name': 'andy',
        'family_name': 'hampsten',
        'email': 'andy@ahmptsten.io',
        'authenticators': [
            {
                'issuer': 'aso',
                'email': 'andy@aso.com',
                'subject': 'alpduez'
            }
        ]
    }
fignon = {
        'uid': 'fignon',
        'given_name': 'lalurent',
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

user_leader = parse_obj_as(UserModel, lemond)
user_owner = parse_obj_as(UserModel, hinault)
user_team = parse_obj_as(UserModel, hampsten)
user_other_team = parse_obj_as(UserModel, fignon)