import pytest
import json
import 

no_json = ""
malformed_json = "{"
empty_json = "{}"
wrong_type_uid = json.dumps({"catalog": "gondor", "run_uid": 5})
wrong_type_catalog = json.dumps({"catalog": 7, "run_uid": "orc-mark-2"})
missing_catalog = json.dumps({"run_uid": "orc-mark-2"})
missing_uid = json.dumps({"catalog": "mordor"})

endpoint = "/api/runs"

@pytest.mark.usefixtures("splash_client", "mongodb")
def test_no_json(splash_client,):
    response = splash_client.get("/api/runs", data=no_json)
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "value_error"

def test_malformed_json(splash_client,):
    response = splash_client.get("/api/runs", data=malformed_json, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "value_error"

def test_empty_json(splash_client,):
    response = splash_client.get("/api/runs", data=empty_json, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"

def test_wrong_type_uid(splash_client,):
    response = splash_client.get("/api/runs", data=wrong_type_uid, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"

def test_wrong_type_catalog(splash_client,):
    response = splash_client.get("/api/runs", data=wrong_type_catalog, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"

def test_missing_catalog(splash_client,):
    response = splash_client.get("/api/runs", data=missing_catalog, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"

def test_missing_uid(splash_client,):
    response = splash_client.get("/api/runs", data=missing_uid, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"

