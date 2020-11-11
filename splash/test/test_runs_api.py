import pytest
import json
from fastapi.testclient import TestClient

import numpy as np
from PIL import Image, ImageOps
import io

from .category_runs_definitions import (
    mock_project,
    root_catalog)


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


@pytest.mark.usefixtures("splash_client", "token")


@pytest.fixture
def mock_data(monkeypatch):
    monkeypatch.setattr('splash.runs.runs_service.project', mock_project)
    monkeypatch.setattr('splash.runs.runs_service.catalog', root_catalog,)


def test_list_catalogs(api_url_root, splash_client: TestClient, token_header, mock_data):
    response = splash_client.get(api_url_root + "/runs", headers=token_header)
    assert response.status_code == 200
    catalog_list = response.json()
    # assert "catalogs" in response_data
    # catalog_list = response_data['catalogs']

    for catalog in root_catalog.keys():
        assert catalog in catalog_list
    assert len(catalog_list) == len(root_catalog.keys())


def test_list_runs(api_url_root, splash_client: TestClient, token_header, mock_data):    
    response = splash_client.get(api_url_root + "/runs/mordor_research", headers=token_header)
    assert response.status_code == 200
    response_data = response.json()
    catalog = root_catalog['mordor_research']
    assert len(response_data) == len(catalog)

    for response_run in response_data:
        response_run_uid = response_run.get('uid')
        assert response_run_uid in catalog
        assert response_run['num_images'] == catalog[response_run_uid].dataset['beamline_energy'].shape[0]
        assert response_run['sample_name'] == catalog[response_run_uid].metadata['sample']


def test_list_runs_catalog_doesnt_exist(api_url_root, splash_client: TestClient, token_header, mock_data):
    response = splash_client.get(api_url_root + "/runs/gondor_research", headers=token_header)
    assert response.status_code == 404
    response_data = json.loads(response.content)
    assert response_data['detail'] == 'Catalog name: gondor_research is not a catalog'


def test_get_image_bad_frame(api_url_root, splash_client: TestClient, token_header, mock_data):
    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/image?frame=blah", headers=token_header)
    assert response.status_code == 422

    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/image?frame=1.5", headers=token_header)
    assert response.status_code == 422

    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/image?frame=-1", headers=token_header)
    assert response.status_code == 422



def test_get_image_metadata_bad_frame(api_url_root, splash_client: TestClient, token_header, mock_data):
    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/metadata?frame=blah", headers=token_header)
    assert response.status_code == 422

    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/metadata?frame=1.5", headers=token_header)
    assert response.status_code == 422

    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/metadata?frame=-1", headers=token_header)
    assert response.status_code == 422




def test_get_image(api_url_root, splash_client: TestClient, token_header, mock_data):
    image_data = root_catalog['mordor_research']['orc-mark-3-uid'].dataset['ccd']

    for idx, image in enumerate(image_data):
        response = splash_client.get(api_url_root + f"/runs/mordor_research/orc-mark-3-uid/image?frame={idx}", headers=token_header)
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/JPEG'
        assert response.content == convert_raw(image).read()


def test_get_image_metadata(api_url_root, splash_client: TestClient, token_header, mock_data):
    energy_data = root_catalog['mordor_research']['orc-mark-3-uid'].dataset['beamline_energy']
    for idx, energy in enumerate(energy_data):
        response = splash_client.get(api_url_root + f"/runs/mordor_research/orc-mark-3-uid/metadata?frame={idx}", headers=token_header)
        assert response.status_code == 200
        response_data = json.loads(response.content)
        assert response_data['energy'] == energy


def test_get_image_metadata_doesnt_exist(api_url_root, splash_client: TestClient, token_header, mock_data):
    
    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/metadata?frame=50", headers=token_header)
    assert response.status_code == 400


def test_get_image_doesnt_exist(api_url_root, splash_client: TestClient, token_header, mock_data):
    response = splash_client.get(api_url_root + "/runs/mordor_research/orc-mark-3-uid/image?frame=50", headers=token_header)
    assert response.status_code == 400
