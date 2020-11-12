from typing import List

from splash.service.runs_service import RunsService
from splash.service.authorization import TeamRunChecker
from splash.models.teams import Team
from .data_teams_runs import teams, catalog, user_leader, user_owner, user_other_team


def test_get_runs_auth(monkeypatch, mongodb):
    checker = TeamRunChecker()
    runs_service = RunsService(checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.service.runs_service.catalog', catalog)
    runs = runs_service.get_runs(user_leader, list(catalog.keys())[0])
    assert runs is not None and len(runs) == 2
    runs = runs_service.get_runs(user_other_team, list(catalog.keys())[0])
    assert len(runs) == 0
