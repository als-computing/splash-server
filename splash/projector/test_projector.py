from .projector import project, ProjectionError, UnkownLocation
from .run_mocks import make_mock_run
from xarray import Dataset

NEX_IMAGE_FIELD = '/entry/instrument/detector/data'
NEX_ENERGY_FIELD = '/entry/instrument/monochromator/energy'
NEX_SAMPLE_NAME_FIELD = '/entry/sample/name'

good_projection = [{
        "name": "nxsans",
        "version": "2020.1",
        "configuration": {"name": "RSoXS"},
        "projection": {
            NEX_SAMPLE_NAME_FIELD: {"location": "configuration", "field": "sample"},
            NEX_IMAGE_FIELD: {"location": "event", "stream": "primary", "field": "ccd"},
            NEX_ENERGY_FIELD: {"location": "event", "stream": "primary", "field": "beamline_energy"}

        }
    }]

bad_location = [{
        "name": "nxsans",
        "version": "2020.1",
        "configuration": {"name": "RSoXS"},
        "projection": {
            NEX_SAMPLE_NAME_FIELD: {"location": "i_dont_exist", "field": "sample"},

        }
    }]

bad_stream = [{
        "name": "nxsans",
        "version": "2020.1",
        "configuration": {"name": "RSoXS"},
        "projection": {
            NEX_SAMPLE_NAME_FIELD: {"location": "configuration", "field": "sample"},
            NEX_IMAGE_FIELD: {"location": "event", "stream": "i_dont_exist", "field": "ccd"},

        }
    }]

bad_field = [{
        "name": "nxsans",
        "version": "2020.1",
        "configuration": {"name": "RSoXS"},
        "projection": {
            NEX_SAMPLE_NAME_FIELD: {"location": "configuration", "field": "sample"},
            NEX_IMAGE_FIELD: {"location": "event", "stream": "primary", "field": "i_dont_exist"},

        }
    }]

def test_unknown_location():
    mock_run = make_mock_run(bad_location, 'one_ring')
    try:
        project(mock_run)
    except Exception as e:
        assert isinstance(e, ProjectionError)
        assert isinstance(e, UnkownLocation)
        assert str(e) == 'Unknown location: i_dont_exist in projection.'
        return
    assert False, "An exception should have been raised"

def test_nonexistent_stream():
    mock_run = make_mock_run(bad_stream, 'one_ring')
    try:
        project(mock_run)
    except Exception as e:
        assert isinstance(e, ProjectionError)
        assert str(e) == 'Error with projecting run'
        return
    assert False, "An exception should have been raised"


def test_nonexistent_stream():
    mock_run = make_mock_run(bad_field, 'one_ring')
    try:
        project(mock_run)
    except Exception as e:
        assert isinstance(e, ProjectionError)
        assert str(e) == 'Error with projecting run'
        return
    assert False, "An exception should have been raised"

def test_projector():
    mock_run = make_mock_run(good_projection, 'one_ring')
    dataset = project(mock_run)
    # Ensure that the to_dask function was called on both 
    # energy and image datasets
    assert mock_run['primary'].to_dask_counter == 2
    assert dataset.attrs[NEX_SAMPLE_NAME_FIELD]
    for idx, energy in enumerate(dataset[NEX_ENERGY_FIELD]):
        assert energy == mock_run['primary'].dataset['beamline_energy'][idx]
    for idx, image in enumerate(dataset[NEX_IMAGE_FIELD]):
        comparison = image == mock_run['primary'].dataset['ccd'][idx]
        assert comparison.all()
   
