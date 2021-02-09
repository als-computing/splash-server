from splash.users import User
import pytest
from splash.service.base import (
    VersionNotFoundError,
    VersionedMongoService,
    ObjectNotFoundError,
    ImmutableMetadataField,
)
import mongomock


@pytest.fixture
def request_user():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
        },
        uid="foobar",
        given_name="ford",
        family_name="prefect",
        email="ford@beetleguice.planet",
    )


@pytest.fixture
def versioned_service():
    db = mongomock.MongoClient().db
    versioned_service = VersionedMongoService(db, "elves", "elves_old")
    return versioned_service


def test_versioned_update(versioned_service: VersionedMongoService, request_user: User):
    with pytest.raises(
        ImmutableMetadataField, match="Cannot mutate field: `version` in `splash_md`"
    ):
        uid = versioned_service.create(
            request_user,
            {
                "name": "Celebrimbor",
                "Occupation": "Ringmaker",
                "splash_md": {"version": 3},
            },
        )

    uid = versioned_service.create(
        request_user, {"name": "Celebrimbor", "Occupation": "Ringmaker"}
    )

    document_1 = versioned_service.retrieve_one(request_user, uid)
    assert document_1["uid"] == uid
    assert document_1["splash_md"]["version"] == 1
    assert document_1["name"] == "Celebrimbor"
    assert document_1["Occupation"] == "Ringmaker"
    assert len(document_1) == 4

    with pytest.raises(
        ImmutableMetadataField, match="Cannot mutate field: `version` in `splash_md`"
    ):
        versioned_service.update(
            request_user,
            {
                "name": "Celebrimbor",
                "Occupation": "Ringmaker",
                "splash_md": {"version": 3},
            },
            uid,
        )

    assert (
        versioned_service.update(
            request_user,
            {"name": "Celebrimbor", "Occupation": "Ringmaker, Swordsmith"},
            uid,
        )
        == uid
    )
    document_2 = versioned_service.retrieve_one(request_user, uid)
    assert document_2["uid"] == uid
    assert document_2["splash_md"]["version"] == 2
    assert document_2["name"] == "Celebrimbor"
    assert document_2["Occupation"] == "Ringmaker, Swordsmith"
    assert len(document_2) == 4

    assert (
        versioned_service.update(
            request_user,
            {"name": "Celebrimbor", "Occupation": "Ringmaker, Swordsmith, Archer"},
            uid,
        )
        == uid
    )
    document_3 = versioned_service.retrieve_one(request_user, uid)
    assert document_3["uid"] == uid
    assert document_3["splash_md"]["version"] == 3
    assert document_3["name"] == "Celebrimbor"
    assert document_3["Occupation"] == "Ringmaker, Swordsmith, Archer"
    assert len(document_3) == 4

    # Make sure there's only one version in the main collection at a time
    assert (
        len(list(versioned_service.retrieve_multiple(request_user, query={"uid": uid})))
        == 1
    )

    with pytest.raises(ObjectNotFoundError):
        versioned_service.update(
            request_user, {"name": "Legolas"}, uid="Does not exist"
        )

    assert versioned_service.retrieve_one(request_user, uid="Does not exist") is None


def test_retrieve_version(versioned_service: VersionedMongoService, request_user: User):
    uid = versioned_service.create(
        request_user, {"name": "Celebrimbor", "Occupation": "Ringmaker"}
    )
    versioned_service.update(
        request_user,
        {"name": "Celebrimbor", "Occupation": "Ringmaker, Swordsmith"},
        uid,
    )
    versioned_service.update(
        request_user,
        {"name": "Celebrimbor", "Occupation": "Ringmaker, Swordsmith, Archer"},
        uid,
    )
    document_1 = versioned_service.retrieve_version(request_user, uid, 1)
    assert document_1["uid"] == uid
    assert document_1["splash_md"]["version"] == 1
    assert document_1["name"] == "Celebrimbor"
    assert document_1["Occupation"] == "Ringmaker"
    assert len(document_1) == 4

    document_2 = versioned_service.retrieve_version(request_user, uid, 2)
    assert document_2["uid"] == uid
    assert document_2["splash_md"]["version"] == 2
    assert document_2["name"] == "Celebrimbor"
    assert document_2["Occupation"] == "Ringmaker, Swordsmith"
    assert len(document_2) == 4

    document_3 = versioned_service.retrieve_version(request_user, uid, 3)
    assert document_3["uid"] == uid
    assert document_3["splash_md"]["version"] == 3
    assert document_3["name"] == "Celebrimbor"
    assert document_3["Occupation"] == "Ringmaker, Swordsmith, Archer"
    assert len(document_3) == 4

    with pytest.raises(VersionNotFoundError):
        versioned_service.retrieve_version(request_user, uid, 4)

    with pytest.raises(ObjectNotFoundError):
        versioned_service.retrieve_version(request_user, "does not exist", 4)

    with pytest.raises(ValueError, match="argument `version` must be more than zero"):
        versioned_service.retrieve_version(request_user, uid, 0)

    with pytest.raises(ValueError, match="argument `version` must be more than zero"):
        versioned_service.retrieve_version(request_user, uid, -1)

    with pytest.raises(TypeError, match="argument `version` must be an integer"):
        versioned_service.retrieve_version(request_user, uid, 2.5)


def test_get_num_versions(versioned_service: VersionedMongoService, request_user: User):
    uid = versioned_service.create(
        request_user, {"name": "Sauron", "Occupation": "Industrialist"}
    )
    assert versioned_service.get_num_versions(request_user, uid) == 1
    versioned_service.update(
        request_user,
        {"name": "Sauron", "Occupation": "Industrialist, Necromancer"},
        uid,
    )
    assert versioned_service.get_num_versions(request_user, uid) == 2
    versioned_service.update(
        request_user,
        {"name": "Sauron", "Occupation": "Industrialist, Necromancer, Dark Lord"},
        uid,
    )
    assert versioned_service.get_num_versions(request_user, uid) == 3

    with pytest.raises(ObjectNotFoundError):
        versioned_service.get_num_versions(request_user, "this_uid_does_not_exist")
