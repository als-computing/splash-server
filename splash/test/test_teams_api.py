import pytest

from .testing_utils import generic_test_api_crud
from .data_teams_runs import teams


@pytest.mark.usefixtures("splash_client", "token_header")
def test_api_crud_team(api_url_root, splash_client, token_header):
    new_team = teams[0].dict()
    new_team.pop('uid')
    generic_test_api_crud(new_team, api_url_root + "/teams", splash_client, token_header)
