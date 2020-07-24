import pytest
import json
from .category_runs_definitions import mock_project, root_catalog, NEX_SAMPLE_NAME_FIELD, NEX_ENERGY_FIELD
from test.category_runs_definitions import root_catalog
import numpy as np
from PIL import Image, ImageOps
import io

endpoint = "/api/runs"


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

@pytest.mark.usefixtures("splash_client")

@pytest.fixture
def mock_data(monkeypatch):
    monkeypatch.setattr('splash.categories.runs.runs_service.project', mock_project)
    monkeypatch.setattr('splash.categories.runs.runs_service.catalog', root_catalog,)


def test_list_catalogs(splash_client, mock_data):
    response = splash_client.get("/api/runs",)
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert "catalogs" in response_data
    catalog_list = response_data['catalogs']

    for catalog in root_catalog:
        assert catalog in catalog_list
    assert len(catalog_list) == len(root_catalog)


def test_list_runs(splash_client, mock_data):
    response = splash_client.get("/api/runs/mordor_research")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    catalog = root_catalog['mordor_research']
    assert len(response_data) == len(catalog)
    for run in catalog:
        assert run in response_data
        assert response_data[run]['num_images'] == catalog[run].dataset['beamline_energy'].shape[0]
        assert response_data[run][NEX_SAMPLE_NAME_FIELD] == catalog[run].metadata['sample']


def test_list_runs_catalog_doesnt_exist(splash_client, mock_data):
    response = splash_client.get("/api/runs/gondor_research")
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert response_data['error'] == 'catalog_not_found'
    assert response_data['message'] == 'Catalog name: gondor_research is not a catalog'


def test_get_image_bad_frame(splash_client, mock_data):
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=blah")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be an integer, represented as an integer, string, or float.'

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=1.5")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be an integer, represented as an integer, string, or float.'

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=-1")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be a positive integer'


def test_get_image_metadata_bad_frame(splash_client, mock_data):
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=blah&metadata=true")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be an integer, represented as an integer, string, or float.'

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=1.5&metadata=true")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be an integer, represented as an integer, string, or float.'

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=-1&metadata=true")
    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert response_data['error'] == 'bad_frame_argument'
    assert response_data['message'] == 'Frame number must be a positive integer'



def test_get_image(splash_client, mock_data):
    image_data = root_catalog['mordor_research']['orc-mark-3-uid'].dataset['ccd']

    for idx, image in enumerate(image_data):
        response = splash_client.get(f"/api/runs/mordor_research/orc-mark-3-uid?frame={idx}")
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/JPEG'
        assert response.data == convert_raw(image).read()


def test_get_image_metadata(splash_client, mock_data):
    energy_data = root_catalog['mordor_research']['orc-mark-3-uid'].dataset['beamline_energy']
    for idx, energy in enumerate(energy_data):
        response = splash_client.get(f"/api/runs/mordor_research/orc-mark-3-uid?frame={idx}&metadata=true")
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data[NEX_ENERGY_FIELD] == energy

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=0&metadata=blahblah")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/JPEG'

    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=0&metadata=false")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/JPEG'


def test_get_image_metadata_doesnt_exist(splash_client, mock_data):
    
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=50&metadata=true")
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert 'Frame number: 50, does not exist.' == response_data['message']
    assert 'frame_does_not_exist' == response_data['error']


def test_get_image_doesnt_exist(splash_client, mock_data):
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=50")
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert 'Frame number: 50, does not exist.' == response_data['message']
    assert 'frame_does_not_exist' == response_data['error']
