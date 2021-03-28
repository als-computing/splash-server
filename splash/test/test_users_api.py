import pytest

from .testing_utils import generic_test_api_crud, generic_test_etag_functionality


@pytest.mark.usefixtures("splash_client", "token_header")
def test_api_user(api_url_root, splash_client, token_header):
    generic_test_api_crud(
        new_user, api_url_root + "/users", splash_client, token_header
    )


def test_etag_functionality(api_url_root, splash_client, token_header):
    generic_test_etag_functionality(
        new_user, api_url_root + "/users", splash_client, token_header
    )


new_user = {
    "given_name": "tricia",
    "family_name": "mcmillan",
    "email": "trillian@heartofgold.improbable",
    "authenticators": [
        {
            "issuer": "accounts.google.com",
            "subject": "dsfsdsdfsdfsdfsdfsdf",
            "email": "trillian@hearfofconld.improbable",
        }
    ],
}
