import pytest

from .testing_utils import generic_test_api_crud, generic_test_etag_functionality
from splash.teams import NewTeam


new_team_1 = NewTeam(
    **{
        "name": "la_vie_claire1",
        "members": {
            "lemond": ["member", "leader"],
            "hinault": ["member", "leader", "owner"],
            "hampsten": ["member"],
        },
    }
)

new_team_2 = NewTeam(
    **{
        "name": "la_vie_claire2",
        "members": {
            "lemond": ["member", "leader"],
            "hinault": ["member", "leader", "owner"],
            "hampsten": ["member"],
        },
    }
)

@pytest.mark.usefixtures("splash_client", "token_header")
def test_api_crud_team(api_url_root, splash_client, token_header):
    generic_test_api_crud(
        new_team_1.dict(), api_url_root + "/teams", splash_client, token_header
    )


def test_etag_functionality(api_url_root, splash_client, token_header):
    generic_test_etag_functionality(
        new_team_2.dict(), api_url_root + "/teams", splash_client, token_header
    )
