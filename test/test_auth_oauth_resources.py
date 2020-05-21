import pytest
import json
from google.oauth2 import id_token
from google.auth.transport import requests

no_json = ""
malformed_json = "{"
empty_json = "{}"
wrong_type_token = json.dumps({"token": 5})
# The reason for these two lines of code is because the iss field could
# either contain https://accounts.google.com or accounts.google.com
# I"m not sure what the difference is between these two, but they are
# both valid issuer values and so should be allowed
issuer_https_prefix = json.dumps({"token": "issued by https://accounts.google.com"})
issuer_no_https_prefix = json.dumps({"token": "issued by accounts.google.com"})
wrong_issuer = json.dumps({"token": "wrong issuer"})
bad_value = json.dumps({"token": "bad_value"})
# Of course no token value will actually trigger a random exception
# This is just to simulate types of errors thrown other than
# a value error (e.g. httperror)
trigger_other_exception = json.dumps({"token":"trigger_other_exception"})

test_user = {
        "name": "google_user",
        "authenticators": [
            {
                "issuer": "https://accounts.google.com",
                "subject": "subject_123456"
            },
            {
                "issuer": "accounts.google.com",
                "subject": "subject_123456"
            }
        ]
    }


@pytest.mark.usefixtures("splash_client", "mongodb")


@pytest.fixture
def mock_env_client_id(monkeypatch):
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "correct_id")


@pytest.fixture
def mock_google_id_token_verify(monkeypatch):
    def mock_verify(token, Request, CLIENT_ID):
        base_user_info = {
            "email": "user@example.com", 
            "sub": "subject_123456",  # matches subject in test_user
            "given_name": "Sean",
            "family_name": "Kelly"}

        # The reason for these two lines of code is because the iss field could
        # either contain https://accounts.google.com or accounts.google.com
        # I"m not sure what the difference is between these two, but they are
        # both valid issuer values and so should be allowed
        if token == "issued by https://accounts.google.com":
            base_user_info["iss"] = "https://accounts.google.com"
            return base_user_info
        elif token == "issued by accounts.google.com":
            base_user_info["iss"] = "accounts.google.com"
            return base_user_info
        elif token == "wrong issuer":
            return {"iss": "wrong_issuer", "sub": "user@example.com"}
        elif token == "bad_value":
            raise ValueError("Bad Value")
        # Of course no token value will actually trigger a random exception (I hope)
        # This is just to account for other types of errors thrown other than
        # a value error (e.g. httperror)
        elif token == "trigger_other_exception":
            raise Exception("something_bad_happened")
    monkeypatch.setattr(id_token, "verify_oauth2_token", mock_verify)


@pytest.fixture
def mock_google_request(monkeypatch):
    # This is a function in the requests object 
    def mock_request():
        return
    monkeypatch.setattr(requests, "Request", mock_request)


def test_no_json(splash_client, mock_env_client_id, ):
    response = splash_client.post("/api/tokensignin", data=no_json, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400


def test_malformed_json(splash_client, mock_env_client_id,):
    response = splash_client.post("/api/tokensignin", data=malformed_json, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400


def test_empty_json(splash_client, mock_env_client_id, ):
    response = splash_client.post("/api/tokensignin", data=empty_json, )
    assert hasattr(response, "status_code")
    assert response.status_code == 400
    #response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"


def test_wrong_type_token(splash_client, mock_env_client_id,):
    response = splash_client.post("/api/tokensignin", data=wrong_type_token)
    assert hasattr(response, "status_code")
    assert response.status_code == 400 
    # response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "validation_error"


def test_issuer_https_prefix(splash_client, mock_env_client_id, mock_google_id_token_verify, mock_google_request):
    user_service = splash_client.application.user_service
    test_user_uid = user_service.create(test_user)
    response = splash_client.post("/api/tokensignin", data=issuer_https_prefix)
    assert hasattr(response, "status_code")
    assert response.status_code == 200
    # response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "message" in response_data
    assert response_data["message"] == "LOGIN SUCCESS"
    assert "user" in response_data
    assert response_data['user']['uid'] == test_user_uid


def test_issuer_no_https_prefix(splash_client, mock_env_client_id, mock_google_id_token_verify, mock_google_request):
    user_service = splash_client.application.user_service
    test_user_uid = user_service.create(test_user)
    response = splash_client.post("/api/tokensignin", data=issuer_no_https_prefix)
    assert hasattr(response, "status_code")
    assert response.status_code == 200
    # response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "message" in response_data
    assert response_data["message"] == "LOGIN SUCCESS"
    assert "user" in response_data
    assert response_data['user']['uid'] == test_user_uid


def test_wrong_issuer(splash_client, mock_env_client_id, mock_google_id_token_verify, mock_google_request):
    response = splash_client.post("/api/tokensignin", data=wrong_issuer)
    assert hasattr(response, "status_code")
    assert response.status_code == 500
    #response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "oauth_verification_error"

def test_bad_value(splash_client, mock_env_client_id,mock_google_id_token_verify, mock_google_request):
    response = splash_client.post("/api/tokensignin", data=bad_value)
    assert hasattr(response, "status_code")
    assert response.status_code == 500
    #response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "oauth_verification_error"


def test_trigger_other_exception(splash_client, mock_env_client_id, mock_google_id_token_verify, mock_google_request):
    response = splash_client.post("/api/tokensignin", data=trigger_other_exception)
    assert hasattr(response, "status_code")
    assert response.status_code == 500
    #response.data is sent in a bytes array, it needs to be decoded into a string
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert response_data["error"] == "server_error"