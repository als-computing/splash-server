import mongomock
import pytest

from splash.categories.experiments.experiments_service import ExperimentService
from .testing_utils import generic_test_flask_crud

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


def test_experiment_service_validate():
    exp_svc = ExperimentService(None)
    issues = exp_svc.validate({"foo": "bar"})
    assert issues


@pytest.mark.usefixtures("splash_client", "mongodb")
def test_flask_crud_experiments(splash_client, mongodb):
    generic_test_flask_crud(new_experiment, '/api/experiments', splash_client, mongodb)


new_experiment = {
    "name": "whiteboard enterprise interfaces tests",
    "technique": {
        "name": "sample_technique",
        "technique_metadata": {
            "some_stuff": "some more things",
            "some_more_stuff": "some things"
        }
    },
    "experiment_metadata": {
        "gap": "2"
    },
    "researcher": {
        "mwet_id": "9b48cf0c-9225-40fa-8e2a-f9e23195dc11",
        "name": "Max Carter",
        "group": "Ford",
        "institution": "UCSB"
    },
    "experimental_conditions": {
        "run_time": "7 days",
        "membrane_or_polymer_area": "1 cm^2"
    },
    "trials": [
        {
            "membrane_or_polymer": "S48",
            "ph": 7,
            "ionic_strength": {
                "value": 0.01,
                "unit": "mM"
            },
            "solutes_present": [
                "Na+",
                "Cl-",
                "In"
            ],
            "adsorbing": "In"
        },
        {
            "membrane_or_polymer": "S48",
            "ph": 10,
            "ionic_strength": {
                "value": 0.01,
                "unit": "mM"
            },
            "solutes_present": [
                "Na+",
                "Cl-",
                "In"
            ],
            "adsorbing": "In"
        },
        {
            "membrane_or_polymer": "S48",
            "pH": 7,
            "ionic_strength": {
                "value": 0.1,
                "unit": "mM"
            },
            "solutes_present": [
                "Na+",
                "Cl-",
                "In"
            ],
            "adsorbing": "In"
        },
        {
            "membrane_or_polymer": "S48",
            "ph": 10,
            "ionic_strength": {
                "value": 0.1,
                "unit": "mM"
            },
            "solutes_present": [
                "Na+",
                "Cl-",
                "In"
            ],
            "adsorbing": "In"
        }
    ],
}