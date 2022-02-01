import pytest
from splash.users.users_service import UsersService
from splash.service.authorization import NotAuthorized
from splash.users import User, NewUser
from mongomock import MongoClient
from .testing_utils import equal_dicts


@pytest.fixture
def admin_user():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "f672367e-c534-4f4a-9e5a-0941dbab2d1c",
            "admin": True
        },
        uid="foobar1",
        given_name="Sauron",
        family_name="The Dark Lord",
        email="Sauron@mordor.net",
    )


@pytest.fixture
def regular_user():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "f672367e-c534-4f4a-9e5a-0941dbab2d1c",
            "admin": False
        },
        uid="foobar2",
        given_name="Saruman",
        family_name="The White",
        email="saruman@middleearth.org",
    )

@pytest.fixture
def regular_user_no_admin_prop():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "f672367e-c534-4f4a-9e5a-0941dbab2d1c",
        },
        uid="foobar3",
        given_name="Gandalf",
        family_name="The Grey",
        email="Gandalf@middleearth.org",
    )

db = MongoClient().db


@pytest.fixture
def users_service():
    users_service = UsersService(db, "users")
    return users_service


uid = ""


def test_admin_can_create_and_edit(users_service: UsersService, admin_user):
    uruk_user = NewUser(given_name="Uruk", family_name="Hai", email="uruk@mordor.net")
    resp = users_service.create(admin_user, uruk_user)
    uid = resp["uid"]
    document = users_service.retrieve_one(admin_user, uid).dict()

    uruk_dict = uruk_user.dict()

    assert uruk_dict['given_name'] == document['given_name']
    assert uruk_dict['family_name'] == document['family_name']
    assert uruk_dict['email'] == document['email']

    update = NewUser(given_name="Uruk", family_name="Hai", email="uruk@middleearth.org")
    resp = users_service.update(admin_user, update, uid)
    document = users_service.retrieve_one(admin_user, uid).dict()

    update_dict = update.dict()

    assert update_dict['given_name'] == document['given_name']
    assert update_dict['family_name'] == document['family_name']
    assert update_dict['email'] == document['email']

    return


def test_regular_cannot_edit(users_service: UsersService, regular_user):
    uruk_user = NewUser(given_name="Uruk", family_name="Hai", email="uruk@mordor.net")
    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.create(regular_user, uruk_user)

    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.update(regular_user, uruk_user, uid)

    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.delete(regular_user, uid)

    return


def test_regular_no_admin_prop_cannot_edit(users_service: UsersService, regular_user_no_admin_prop):
    uruk_user = NewUser(given_name="Uruk", family_name="Hai", email="uruk@mordor.net")
    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.create(regular_user_no_admin_prop, uruk_user)

    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.update(regular_user_no_admin_prop, uruk_user, uid)

    with pytest.raises(NotAuthorized, match="user is not an admin"):
        users_service.delete(regular_user_no_admin_prop, uid)

    return
