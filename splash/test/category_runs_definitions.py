from datetime import datetime

import xarray

MOCK_IMAGE = xarray.DataArray([[1, 2], [3, 4]])
BEAMLINE_ENERGY_VALS = [1, 2, 3, 4, 5]
I_ZERO_VALS = [-1, -2, -3, -4, -5]
CCD = [MOCK_IMAGE+1, MOCK_IMAGE+2, MOCK_IMAGE+3, MOCK_IMAGE+4, MOCK_IMAGE+5]

NEX_IMAGE_FIELD = '/entry/instrument/detector/data'
NEX_ENERGY_FIELD = '/entry/instrument/monochromator/energy'
NEX_SAMPLE_NAME_FIELD = '/entry/sample/name'


def mock_project(run):
    dataset = run.dataset
    data_vars = { 

        NEX_IMAGE_FIELD: dataset['ccd'],
    }
    attrs = {
        "collector_name": run.metadata["collector_name"], 
        "collection_date": run.metadata["collection_date"],
        "sample_name": run.metadata["sample_name"],
        "num_data_images": run.metadata["num_data_images"]}
    return xarray.Dataset(data_vars, attrs=attrs)


class MockRun():
    def __init__(self, sample, collector_name):
        self.metadata = {
            "collector_name": collector_name,
            "collection_date": datetime.utcnow(),
            "sample_name": "earth",
            "num_data_images": 5
        }
        data_vars = {
            'beamline_energy': ('time', BEAMLINE_ENERGY_VALS),
            'i_zero': ('time', I_ZERO_VALS),
            'ccd': (('time', 'dim_0', 'dim_1'), CCD)
        }
        self.dataset = xarray.Dataset(data_vars)
        self.metadata[NEX_SAMPLE_NAME_FIELD] = sample


def make_mock_run(sample, collector_name):
    return MockRun(sample, collector_name)


root_catalog = {
    'one_ring_research': {

    },
    'mordor_research': {
        'orc-mark-3-uid': make_mock_run('orc', 'gandolf'),
        'nazgul-mark-4-uid': make_mock_run('nazgul', 'slartibartfast'),
        'balrog-mark-9-uid': make_mock_run('balrog', 'gandolf')
    }
}
