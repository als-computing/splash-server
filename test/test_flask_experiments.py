import splash
from splash.data import MongoCollectionDao
from splash.resources.experiments import Experiments
import os
import tempfile
import mongomock
import pytest
import json

@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db


@pytest.fixture
def client(mongodb):
    app = splash.create_app(mongodb)
    return app.test_client()


def test_crud_experiment(client, mongodb):
    url = '/api/experiments'
    
    #create 
    response = client.post(
        url, 
        data = json.dumps(new_experiment), 
        content_type='application/json')
    assert response.status_code == 200
    response_dict= json.loads(response.get_json())
    new_uid = response_dict['uid']
    assert new_uid

    #retreive all
    response = client.get(url)
    assert response.status_code == 200
    response_dict= json.loads(response.get_json())
    assert response_dict['total_results'] == 1

    #retrive one
    response = client.get(url + '/' + new_uid)
    assert response.status_code == 200
    

    
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
    "uid": "b0798c7c-a4fa-4754-a132-8fdabac0d71a"
}