import pytest

from .testing_utils import generic_test_api_crud
from splash.teams import NewTeam

@pytest.mark.usefixtures("splash_client", "token_header")
def test_api_crud_team(api_url_root, splash_client, token_header):
    new_team = NewTeam(**{'name': 'la_vie_claire',
                                              'members': {
                                                    'lemond': ['member', 'leader'],
                                                    'hinault': ['member', 'leader', 'owner'],
                                                    'hampsten': ['member']}})
    generic_test_api_crud(new_team.dict(), api_url_root + "/teams", splash_client, token_header)
