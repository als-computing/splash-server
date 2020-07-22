import pytest

from splash.categories.users.users_service import UserService
from .testing_utils import generic_test_flask_crud


@pytest.mark.usefixtures("splash_client", "mongodb")
def test_validate():
    exp_svc = UserService(None)
    issues = exp_svc.validate({"foo": "bar"})
    assert issues


def test_flask_crud_user(splash_client, mongodb):
    generic_test_flask_crud(new_user, '/api/users', splash_client, mongodb)


new_user = {
    "name": "bobmcbob",
    "groups": ["legends", "cannibals"],
    "authenticators": [
        {"issuer": "accounts.google.com",
         "subject": "dsfsdsdfsdfsdfsdfsdf"}
    ]
}