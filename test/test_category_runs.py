import pytest
import json
import databroker
from .category_runs_definitions import MockRun
endpoint = "/api/runs"


def make_mock_run(sample, datafile):
    return MockRun(sample, datafile)


root_catalog = {
    'one_ring_research': {

    },
    'mordor_research': {
        'orc-mark-3-uid': make_mock_run('orc', '/home/sauron/orc'),
        'nazgul-mark-4-uid': make_mock_run('nazgul', '/home/sauron/nazgul'),
        'balrog-mark-9-uid': make_mock_run('balrog', '/home/sauron/balrog')
    }
}


@pytest.mark.usefixtures("splash_client")
@pytest.fixture
def mock_root_catalog(monkeypatch):
    monkeypatch.setattr(databroker, 'catalog', root_catalog,)


def test_list_catalogs(mock_root_catalog, splash_client,):
    response = splash_client.get("/api/runs",)
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert "catalogs" in response_data
    catalog_list = response_data['catalogs']

    for catalog in root_catalog:
        assert catalog in catalog_list
    assert len(catalog_list) == len(root_catalog)


def test_list_runs(mock_root_catalog, splash_client):
    response = splash_client.get("/api/runs/mordor_research")
    assert response.status_code == 200
    response_data = json.loads(response.data)
    catalog = root_catalog['mordor_research']
    assert len(response_data) == len(catalog)
    for run in catalog:
        assert run in response_data
        assert response_data[run]['num_images'] == catalog[run].metadata['stop']['num_events']['primary']
        assert response_data[run]['sample'] == catalog[run].metadata['start']['sample']
        assert response_data[run]['data_file'] == catalog[run].metadata['start']['data_file']


def test_list_runs_catalog_doesnt_exist(mock_root_catalog, splash_client):
    response = splash_client.get("/api/runs/gondor_research")
    assert response.status_code == 404
    response_data = json.loads(response.data)
    assert response_data['error'] == 'catalog_not_found'
    assert response_data['message'] == 'Catalog name: gondor_research is not a catalog'


def test_get_image_bad_frame(mock_root_catalog, splash_client):
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


def test_get_image_metadata_bad_frame(mock_root_catalog, splash_client):
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

#TODO: fix the following failing tests, when run they will give:
# This requires better mocking of the to_dask() attribute of the stream
# ...
# File "splash-server/splash/categories/runs/runs_service.py", line 57, in get_image
    # image_data = image_data[frame_number]
# File "splash-server/env/lib/python3.6/site-packages/dask/dataframe/core.py", line 2879, in __getitem__
    # "Series getitem in only supported for other series objects "
# NotImplementedError: Series getitem in only supported for other series objects with matching partition structure
def test_get_image(mock_root_catalog, splash_client):
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=0")
    assert response.status_code == 200
    assert response.headers['content-type'] == 'image/JPEG'
# TODO: test the images themselves to ensure that images are properly compressed


def test_get_image_metadata(mock_root_catalog, splash_client):
    response = splash_client.get("/api/runs/mordor_research/orc-mark-3-uid?frame=0&metadata=true")
    assert response['i_zero'] == -1
    assert response['beamline_energy'] == 1


def test_get_image_metadata_doesnt_exist(mock_root_catalog, splash_client):
    #Test for the case that the image doesn't exist
    raise NotImplementedError()


def test_get_image_doesnt_exist(mock_root_catalog, splash_client):
    #Test for the case that the image doesn't exist
    raise NotImplementedError()