import pytest

from splash.api.config import ConfigStore

@pytest.mark.usefixtures("splash_client")
def test_settings_api(monkeypatch, api_url_root, splash_client, token_header):
    # monkeypatch.setenv("GOOGLE_CLIENT_ID", "test_id")
    monkeypatch.setattr(ConfigStore, "GOOGLE_CLIENT_ID", "test_id")
    response = splash_client.get(api_url_root + "/settings")
    assert response.status_code == 200, f"{response.status_code}: response is {response.content}"
    assert response.json()['google_client_id'] == "test_id"
