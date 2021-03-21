import pytest

from .testing_utils import generic_test_api_crud, generic_test_etag_functionality
from splash.teams import NewTeam


new_team = NewTeam(
    **{
        "name": "la_vie_claire",
        "members": {
            "lemond": ["member", "leader"],
            "hinault": ["member", "leader", "owner"],
            "hampsten": ["member"],
        },
    }
)


@pytest.mark.usefixtures("splash_client", "token_header", "test_user")
def test_api_crud_team(api_url_root, splash_client, token_header):
    generic_test_api_crud(
        new_team.dict(), api_url_root + "/teams", splash_client, token_header
    )


def test_etag_functionality(api_url_root, splash_client, token_header, test_user):
    generic_test_etag_functionality(
        new_team.dict(), api_url_root + "/teams", splash_client, token_header, test_user
    )
