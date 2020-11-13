
from typing import List
from pydantic import parse_obj_as
import pytest
from xarray import DataArray

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


def test_get_runs_auth(monkeypatch, teams_service):
    catalog = {
        "tour_winners": {
                '85': MockRun('la_vie_claire'),
                '86': MockRun('la_vie_claire'),
                '87': MockRun('carrera'),
                '88': MockRun('cafe_de_columbia'),
        }
    }
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', catalog)
    runs = runs_service.get_runs(user_leader_lemond, "tour_winners")
    # lemond is a member of la_vie_claire, which created two run
    assert runs is not None and len(runs) == 2, '2 available runs match those submitted by team'
    runs = runs_service.get_runs(user_other_team, "tour_winners")
    assert len(runs) == 0, 'no runs available to use who is not member of a team that created one'


def test_get_run_auth(monkeypatch, teams_service):
    catalog = {
        "tour_winners": {
                '85': MockRun('la_vie_claire'),
                '87': MockRun('carrera')
        }
    }
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', catalog)
    run = runs_service.get_slice_metadata(user_leader_lemond, "tour_winners", '85', 'primay_config_field', 0)
    assert run is not None

    run = runs_service.get_slice_metadata(user_leader_lemond, "tour_winners", '87', 'primay_config_field', 0)
    assert run is not None


class MockRun(dict):
    def __init__(self, team):
        self.metadata = {
            'start': {
                'user_id': 'runner_id',
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
                            },
                            'image_data': {
                                'type': 'linked',
                                'location': 'event',
                                'stream': 'primary',
                                'field': 'image'
                            },
                            'primay_config_field': {
                                'type': 'linked',
                                'location': 'configuration',
                                'stream': 'primary',
                                'config_device': 'camera_device',
                                'config_index': 0,
                                'field': 'camera_config_field'
                            }
                        }
                    }
                ]
            },
        }
        self.primary = Stream()
        # self.primary = type('MockStream', (dict,), {})()
        self['primary'] = self.primary
        
        self.primary['image'] = DataArray([[1.0, 1.0], [0.0, 1.0]])
        self.primary.metadata = {}
        self.primary.metadata['descriptors'] = []
        self.primary.metadata['descriptors'].append({})
        self.primary.metadata['descriptors'][0]['configuration'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data']['camera_config_field'] = 'config_value'


class Stream(dict):
    def to_dask(self):
        return self


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

user_leader_lemond = parse_obj_as(UserModel, lemond)
user_owner = parse_obj_as(UserModel, hinault)
user_team = parse_obj_as(UserModel, hampsten)
user_other_team = parse_obj_as(UserModel, fignon)