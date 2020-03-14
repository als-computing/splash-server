import pytest
import mongomock
from splash.experiments.experiment_service import ExperimentService

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


def test_validate():
    exp_svc = ExperimentService(None)
    issues = exp_svc.validate({"foo": "bar"})
    assert issues
