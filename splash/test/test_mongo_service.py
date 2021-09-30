import datetime
from splash.service.models import SplashMetadata
from splash.test.testing_utils import equal_dicts
from splash.users import User
import pytest
from splash.service.base import (
    EtagMismatchError,
    MongoService,
    ImmutableMetadataField,
)
import mongomock
from freezegun import freeze_time
from copy import deepcopy


@pytest.fixture
def request_user_1():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "170abbfa-5ce9-49ba-8072-69edb6c263a7",
        },
        uid="foobar",
        given_name="ford",
        family_name="prefect",
        email="ford@beetleguice.planet",
    )


@pytest.fixture
def request_user_2():
    return User(
        splash_md={
            "creator": "NONE",
            "create_date": "2020-01-7T13:40:53",
            "last_edit": "2020-01-7T13:40:53",
            "edit_record": [],
            "etag": "45f3439c-f162-4713-a33b-96d902ae0c2e",
        },
        uid="barfoo",
        given_name="Arthur",
        family_name="Dent",
        email="Arthur@gmail.com",
    )


@pytest.fixture
def mongo_service():
    db = mongomock.MongoClient().db
    mongo_service = MongoService(db, "elves")
    return mongo_service


mock_times = [
    datetime.datetime.strptime("2021-01-05T19:15:53", "%Y-%m-%dT%H:%M:%S"),
    datetime.datetime.strptime("2021-01-06T19:15:53", "%Y-%m-%dT%H:%M:%S"),
    datetime.datetime.strptime("2021-03-06T19:15:53", "%Y-%m-%dT%H:%M:%S"),
]

celebrimbor = {"name": "Celebrimbor", "Occupation": "Ringmaker"}
celebrimbor_2 = {"name": "Celebrimbor", "Occupation": "Ringmaker, Archer"}
celebrimbor_3 = {"name": "Celebrimbor", "Occupation": "Ringmaker, Archer, Swordsman"}
legolas = {"name": "Legolas", "Occupation": "Archer, Warrior"}
galadriel = {"name": "Galadriel", "Occupation": "Royal lady"}
elrond = {"name": "Elrond", "Occupation": "Lord"}
ignore_keys = ["splash_md", "uid"]

# TODO: Test paging
def test_creation(
    mongo_service: MongoService,
    request_user_1: User,
):
    # By setting the timezone offset we ensure that even if
    # We are in a different timezone we are still timestamping using utcnow
    # So everything is consistent https://github.com/spulec/freezegun#timezones
    with freeze_time(mock_times[0], tz_offset=-4, as_arg=True) as frozen_datetime:
        response = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        uid = response["uid"]
        frozen_datetime.move_to(mock_times[1])
        document_1 = mongo_service.retrieve_one(request_user_1, uid)
        metadata = document_1["splash_md"]
        equal_dicts(celebrimbor, document_1, ignore_keys)
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[0]
        assert len(metadata["edit_record"]) == 0
        assert metadata == response["splash_md"]


def test_create_ordering(
    mongo_service: MongoService, request_user_1: User, monkeypatch
):
    with freeze_time(mock_times[0], tz_offset=-4, auto_tick_seconds=15):
        mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        mongo_service.create(request_user_1, deepcopy(legolas))
        mongo_service.create(request_user_1, deepcopy(galadriel))
        mongo_service.create(request_user_1, deepcopy(elrond))

        elves = list(mongo_service.retrieve_multiple(request_user_1))

        assert len(elves) == 4
        equal_dicts(elrond, elves[0], ignore_keys)
        equal_dicts(galadriel, elves[1], ignore_keys)
        equal_dicts(legolas, elves[2], ignore_keys)
        equal_dicts(celebrimbor, elves[3], ignore_keys)


def test_order_by_key(mongo_service: MongoService, request_user_1: User, monkeypatch):
    mongo_service.create(
        request_user_1,
        deepcopy(celebrimbor),
    )
    mongo_service.create(request_user_1, deepcopy(legolas))
    mongo_service.create(request_user_1, deepcopy(galadriel))
    mongo_service.create(request_user_1, deepcopy(elrond))
    elves = list(mongo_service.retrieve_multiple(request_user_1, sort=[("name", 1)],))

    assert len(elves) == 4
    equal_dicts(celebrimbor, elves[0], ignore_keys)
    equal_dicts(elrond, elves[1], ignore_keys)
    equal_dicts(galadriel, elves[2], ignore_keys)
    equal_dicts(legolas, elves[3], ignore_keys)


def test_retrieve_multiple_errors(
    mongo_service: MongoService, request_user_1: User, monkeypatch
):
    mongo_service.create(
        request_user_1,
        deepcopy(celebrimbor),
    )
    mongo_service.create(request_user_1, deepcopy(legolas))
    mongo_service.create(request_user_1, deepcopy(galadriel))
    mongo_service.create(request_user_1, deepcopy(elrond))
    with pytest.raises(TypeError, match="`sort` argument must be of type list"):
        mongo_service.retrieve_multiple(request_user_1, sort=None)


def test_edits(mongo_service: MongoService, request_user_1: User, request_user_2: User):
    with freeze_time(mock_times[0], tz_offset=-4, as_arg=True) as frozen_datetime:
        response = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        frozen_datetime.move_to(mock_times[1])
        response = mongo_service.update(
            request_user_1,
            deepcopy(celebrimbor_2),
            response["uid"],
        )

        document = mongo_service.retrieve_one(request_user_1, response["uid"])
        equal_dicts(document, celebrimbor_2, ignore_keys)
        metadata = document["splash_md"]
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[1]
        assert metadata == response["splash_md"]
        frozen_datetime.move_to(mock_times[2])

        response = mongo_service.update(
            request_user_2,
            deepcopy(celebrimbor_3),
            response["uid"],
        )

        document = mongo_service.retrieve_one(request_user_1, response["uid"])

        equal_dicts(document, celebrimbor_3, ignore_keys)
        metadata = document["splash_md"]
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[2]
        assert metadata == response["splash_md"]

        edit_record = metadata["edit_record"]

        assert len(edit_record) == 2

        assert edit_record[0]["date"] == mock_times[1]
        assert edit_record[0]["user"] == request_user_1.uid

        assert edit_record[1]["date"] == mock_times[2]
        assert edit_record[1]["user"] == request_user_2.uid


def test_edit_ordering(mongo_service: MongoService, request_user_1: User, monkeypatch):
    with freeze_time(mock_times[0], tz_offset=-4, auto_tick_seconds=15):
        response = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        mongo_service.create(request_user_1, deepcopy(legolas))
        mongo_service.create(request_user_1, deepcopy(galadriel))
        mongo_service.create(request_user_1, deepcopy(elrond))
        mongo_service.update(request_user_1, {}, response["uid"])
        elves = list(mongo_service.retrieve_multiple(request_user_1))

        assert len(elves) == 4
        equal_dicts({}, elves[0], ignore_keys)
        equal_dicts(elrond, elves[1], ignore_keys)
        equal_dicts(galadriel, elves[2], ignore_keys)
        equal_dicts(legolas, elves[3], ignore_keys)


def test_create_with_good_metadata(mongo_service: MongoService, request_user_1: User):
    response = mongo_service.create(
        request_user_1, {"splash_md": {"mutable_field": "test_value"}}
    )
    assert response


immutable_fields = SplashMetadata.__dict__["__fields__"]


def test_create_with_bad_metadata(mongo_service: MongoService, request_user_1: User):

    for field in immutable_fields:
        with pytest.raises(
            ImmutableMetadataField,
            match=f"Cannot mutate field: `{field}` in `splash_md`",
        ):
            mongo_service.create(request_user_1, {"splash_md": {field: "test_value"}})


def test_update_with_good_metadata(mongo_service: MongoService, request_user_1: User):
    response = mongo_service.create(request_user_1, {"Mordor": "Mt. Doom"})

    incoming_data = mongo_service.retrieve_one(request_user_1, response["uid"])
    incoming_data.pop("splash_md")
    incoming_data["splash_md"] = {"muteable_field": "test"}
    incoming_data.pop("uid")

    mongo_service.update(request_user_1, deepcopy(incoming_data), response["uid"])

    stored_data = mongo_service.retrieve_one(request_user_1, response["uid"])
    # Make sure body stayed the same
    equal_dicts(incoming_data, stored_data, ignore_keys)
    # Make sure that the field was changed
    assert incoming_data["splash_md"]["muteable_field"] == stored_data["splash_md"]["muteable_field"]


def test_update_with_bad_metadata(mongo_service: MongoService, request_user_1: User):
    response = mongo_service.create(request_user_1, {"Mordor": "Mt. Doom"})

    data = mongo_service.retrieve_one(request_user_1, response["uid"])

    for field in immutable_fields:
        with pytest.raises(
            ImmutableMetadataField,
            match=f"Cannot mutate field: `{field}` in `splash_md`",
        ):
            mongo_service.update(
                request_user_1, {"splash_md": {field: "test_value"}}, response["uid"]
            )
        assert mongo_service.retrieve_one(request_user_1, response["uid"]) == data


def test_etag_functionality(mongo_service: MongoService, request_user_1: User):
    response = mongo_service.create(
        request_user_1,
        deepcopy(celebrimbor),
    )
    uid = response["uid"]
    document_1 = mongo_service.retrieve_one(request_user_1, uid)
    metadata = document_1["splash_md"]
    assert len(metadata["etag"]) > 0

    etag1 = metadata["etag"]
    mongo_service.update(request_user_1, deepcopy(celebrimbor_2), uid, etag=etag1)
    document_2 = mongo_service.retrieve_one(request_user_1, uid)
    etag2 = document_2["splash_md"]["etag"]
    assert etag1 != etag2

    with pytest.raises(
        EtagMismatchError,
    ) as exc:
        mongo_service.update(request_user_1, deepcopy(celebrimbor_3), uid, etag=etag1)

    doc_2 = mongo_service.retrieve_one(request_user_1, uid)
    assert exc.value.args[0] == f"Etag argument `{etag1}` does not match current etag: `{etag2}`"
    assert exc.value.etag == etag2
    # make sure no changes were made
    assert doc_2 == document_2
