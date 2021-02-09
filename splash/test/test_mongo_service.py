from splash.service.models import SplashMetadata
from splash.test.test_teams_service import request_user
from splash.test.testing_utils import equal_dicts
from splash.users import User
import pytest
from splash.service.base import (
    VersionNotFoundError,
    MongoService,
    ObjectNotFoundError,
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
    "2021-01-05T19:15:53",
    "2021-01-06T19:15:53",
    "2021-03-06T19:15:53",
]
uid = ""

celebrimbor = {"name": "Celebrimbor", "Occupation": "Ringmaker"}
celebrimbor_2 = {"name": "Celebrimbor", "Occupation": "Ringmaker, Archer"}
celebrimbor_3 = {"name": "Celebrimbor", "Occupation": "Ringmaker, Archer, Swordsman"}
legolas = {"name": "Legolas", "Occupation": "Archer, Warrior"}
galadriel = {"name": "Galadriel", "Occupation": "Royal lady"}
elrond = {"name": "Elrond", "Occupation": "Lord"}
ignore_keys = ["splash_md", "uid"]


def test_creation(
    mongo_service: MongoService,
    request_user_1: User,
):
    # By setting the timezone offset we ensure that even if
    # We are in a different timezone we are still timestamping using utcnow
    # So everything is consistent https://github.com/spulec/freezegun#timezones
    with freeze_time(mock_times[0], tz_offset=-4, as_arg=True) as frozen_datetime:
        uid = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        frozen_datetime.move_to(mock_times[1])
        document_1 = mongo_service.retrieve_one(request_user_1, uid)
        metadata = document_1["splash_md"]
        equal_dicts(celebrimbor, document_1, ignore_keys)
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[0]
        assert len(metadata["edit_record"]) == 0


def test_create_ordering(mongo_service: MongoService, request_user_1: User, monkeypatch):
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


def test_edits(mongo_service: MongoService, request_user_1: User, request_user_2: User):
    with freeze_time(mock_times[0], tz_offset=-4, as_arg=True) as frozen_datetime:
        uid = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        frozen_datetime.move_to(mock_times[1])
        uid = mongo_service.update(
            request_user_1,
            deepcopy(celebrimbor_2),
            uid,
        )

        document = mongo_service.retrieve_one(request_user_1, uid)
        equal_dicts(document, celebrimbor_2, ignore_keys)
        metadata = document["splash_md"]
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[1]
        frozen_datetime.move_to(mock_times[2])

        uid = mongo_service.update(
            request_user_2,
            deepcopy(celebrimbor_3),
            uid,
        )

        document = mongo_service.retrieve_one(request_user_1, uid)

        equal_dicts(document, celebrimbor_3, ignore_keys)
        metadata = document["splash_md"]
        assert metadata["create_date"] == mock_times[0]
        assert metadata["creator"] == request_user_1.uid
        assert metadata["last_edit"] == mock_times[2]

        edit_record = metadata["edit_record"]

        assert len(edit_record) == 2

        assert edit_record[0]["date"] == mock_times[1]
        assert edit_record[0]["user"] == request_user_1.uid

        assert edit_record[1]["date"] == mock_times[2]
        assert edit_record[1]["user"] == request_user_2.uid

def test_edit_ordering(mongo_service: MongoService, request_user_1: User, monkeypatch):
    with freeze_time(mock_times[0], tz_offset=-4, auto_tick_seconds=15):
        uid = mongo_service.create(
            request_user_1,
            deepcopy(celebrimbor),
        )
        mongo_service.create(request_user_1, deepcopy(legolas))
        mongo_service.create(request_user_1, deepcopy(galadriel))
        mongo_service.create(request_user_1, deepcopy(elrond))
        mongo_service.update(request_user_1, {}, uid)
        elves = list(mongo_service.retrieve_multiple(request_user_1))

        assert len(elves) == 4
        equal_dicts({}, elves[0], ignore_keys)
        equal_dicts(elrond, elves[1], ignore_keys)
        equal_dicts(galadriel, elves[2], ignore_keys)
        equal_dicts(legolas, elves[3], ignore_keys)

def test_create_with_good_metadata(mongo_service: MongoService, request_user_1: User):
    uid = mongo_service.create(
        request_user_1, {"splash_md": {"mutable_field": "test_value"}}
    )
    assert uid


immutable_fields = SplashMetadata.__dict__["__fields__"]


def test_create_with_bad_metadata(mongo_service: MongoService, request_user_1: User):

    for field in immutable_fields:
        with pytest.raises(
            ImmutableMetadataField,
            match=f"Cannot mutate field: `{field}` in `splash_md`",
        ):
            mongo_service.create(request_user_1, {"splash_md": {field: "test_value"}})


def test_update_with_bad_metadata(mongo_service: MongoService, request_user_1: User):
    uid = mongo_service.create(request_user_1, {"Mordor": "Mt. Dum"})

    data = mongo_service.retrieve_one(request_user_1, uid)

    for field in immutable_fields:
        with pytest.raises(
            ImmutableMetadataField,
            match=f"Cannot mutate field: `{field}` in `splash_md`",
        ):
            mongo_service.update(
                request_user_1, {"splash_md": {field: "test_value"}}, uid
            )
        assert mongo_service.retrieve_one(request_user_1, uid) == data
