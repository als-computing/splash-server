
from typing import List
from pydantic import parse_obj_as
import pytest
from xarray import DataArray

from splash.runs.runs_service import RunsService, TeamRunChecker
from splash.service.authorization import AccessDenied
from splash.teams.service import TeamsService
from splash.teams.models import NewTeam

from .runs_definitions import root_catalog


@pytest.mark.usefixtures("splash_client", "users", "teams_service")
def test_get_runs_auth(monkeypatch, teams_service, users):
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog)
    runs = runs_service.get_runs(users['leader'], "root_catalog")
    # lemond is a member of la_vie_claire, which created two run
    assert runs is not None and len(runs) == 2, '2 available runs match those submitted by same_team'
    runs = runs_service.get_runs(users['other_team'], "root_catalog")
    assert len(runs) == 1, 'one run available to use who is a member of other_team'


def test_get_slice_metadata_auth(monkeypatch, teams_service, users):
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog)
    slice_meta_data = runs_service.get_slice_metadata(users['leader'], "root_catalog", 'same_team_1', 0)
    assert slice_meta_data is not None, 'retrieved slice metadata for run user has access to'
    assert slice_meta_data['beamline_energy'] == 1.21

    with pytest.raises(AccessDenied):
        slice_meta_data = runs_service.get_slice_metadata(users['leader'], "root_catalog", 'other_team_1', 0)



def test_slice_image_auth(monkeypatch, teams_service, users):
    checker = TeamRunChecker()
    runs_service = RunsService(teams_service, checker)
    # patch the catalog into the service to override stock intake catalog
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog)
    image_array = runs_service.get_slice_image(users['leader'], "root_catalog", 'same_team_1', 'image_data', 0, raw_bytes=True)
    assert image_array is not None, 'retrieved slice image for run user has access to'
    with pytest.raises(AccessDenied):
        image_array = runs_service.get_slice_image(users['leader'], "root_catalog", 'other_team_1', 'image_data', 0, raw_bytes=True)
