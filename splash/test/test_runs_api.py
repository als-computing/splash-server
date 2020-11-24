import io
import json

from fastapi.testclient import TestClient
import numpy as np
from PIL import Image, ImageOps
import pytest

from splash.api.auth import create_access_token

from .runs_definitions import root_catalog


def create_token(user_id: str):
    token_info = {"sub": user_id, "scopes": ['splash']}
    token = create_access_token(token_info)
    return {"Authorization": f"Bearer {token}"}



@pytest.mark.usefixtures("splash_client", "token", "users", "teams_service")
@pytest.fixture
def leader_token(mongodb, users):
    return create_token(users['leader'].uid)


def convert_raw(data):
    log_image = np.array(data.compute())
    log_image = log_image - np.min(log_image) + 1.001
    log_image = np.log(log_image)
    log_image = 205*log_image/(np.max(log_image))
    auto_contrast_image = Image.fromarray(log_image.astype('uint8'))
    auto_contrast_image = ImageOps.autocontrast(
                            auto_contrast_image, cutoff=0.1)
    # auto_contrast_image = resize(np.array(auto_contrast_image),
                                            # (size, size))
    file_object = io.BytesIO()
    auto_contrast_image.save(file_object, format='JPEG')
    # move to beginning of file so `send_file()` will read from start    
    file_object.seek(0)

    return file_object

def test_list_catalogs(api_url_root, splash_client: TestClient, leader_token, monkeypatch):
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog) 
    response = splash_client.get(api_url_root + "/runs", headers=leader_token)
    assert response.status_code == 200
    catalog_list = response.json()
    for catalog in root_catalog.keys():
        assert catalog in catalog_list
    assert len(catalog_list) == len(root_catalog.keys())


def test_list_runs(api_url_root, splash_client: TestClient, leader_token, teams_service, monkeypatch):
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog) 
    response = splash_client.get(api_url_root + "/runs/root_catalog", headers=leader_token)
    assert response.status_code == 200
    response_data = response.json()
    catalog = root_catalog['root_catalog']
    same_team_runs = []
    {same_team_runs.append(run) for run in catalog if "same_team" in run}
    assert len(response_data) == len(same_team_runs)

    for response_run in response_data:
        response_run_uid = response_run.get('uid')
        assert response_run_uid in catalog
        assert response_run['sample_name'] == catalog[response_run_uid].metadata['start']['sample']


def test_list_runs_catalog_doesnt_exist(api_url_root, splash_client: TestClient, leader_token, teams_service):
    
    response = splash_client.get(api_url_root + "/runs/does_not_exist", headers=leader_token)
    assert response.status_code == 404
    response_data = json.loads(response.content)
    assert response_data['detail'] == 'Catalog name: does_not_exist is not a catalog'

#  temporarily removed until support is re-introduced
# def test_get_image_bad_frame(api_url_root, splash_client: TestClient, leader_token, teams_service):
#     response = splash_client.get(api_url_root + "/runs/root_catalog/same_team_1/image?frame=blah",
#                                  headers=leader_token)
#     assert response.status_code == 422

#     response = splash_client.get(api_url_root + "/runs/root_catalog/same_team_1/image?frame=1.5", 
#                                  headers=leader_token)
#     assert response.status_code == 422

#     response = splash_client.get(api_url_root + "/runs/root_catalog/same_team_1/image?frame=-1", 
#                                  headers=leader_token)
#     assert response.status_code == 422


#  temporarily removed until support is re-introduced
# def test_get_image(api_url_root, splash_client: TestClient, leader_token, teams_service, monkeypatch):
#     monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog)
#     image_data = root_catalog['root_catalog']['same_team_1'].primary['image']
#     for idx, image in enumerate(image_data):
#         response = splash_client.get(api_url_root + f"/runs/root_catalog/same_team_1/image?frame={idx}&field=image_data",
#                                      headers=leader_token)
#         assert response.status_code == 200
#         assert response.headers['content-type'] == 'image/JPEG'
#         assert response.content == convert_raw(image).read()


def test_get_thumb(api_url_root, splash_client: TestClient, leader_token, teams_service, monkeypatch):
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog)
    image_data = root_catalog['root_catalog']['same_team_1'].thumbnail['image']
    for idx, image in enumerate(image_data):
        response = splash_client.get(api_url_root + f"/runs/root_catalog/same_team_1/thumb?slice={str(idx)}",
                                     headers=leader_token)
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/JPEG'
        assert response.content == convert_raw(image).read()
