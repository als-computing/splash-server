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
        NEX_ENERGY_FIELD: dataset['beamline_energy'],
        NEX_IMAGE_FIELD: dataset['ccd'],
    }
    attrs = {NEX_SAMPLE_NAME_FIELD: run.metadata['sample']}
    return xarray.Dataset(data_vars, attrs=attrs)


class MockRun():
    def __init__(self, sample=''):
        self.metadata = {
            'sample': ''
        }
        data_vars = {
            'beamline_energy': ('time', BEAMLINE_ENERGY_VALS),
            'i_zero': ('time', I_ZERO_VALS),
            'ccd': (('time', 'dim_0', 'dim_1'), CCD)
        }
        self.dataset = xarray.Dataset(data_vars)
        self.metadata['sample'] = sample


def make_mock_run(sample):
    return MockRun(sample)


root_catalog = {
    'one_ring_research': {

    },
    'mordor_research': {
        'orc-mark-3-uid': make_mock_run('orc'),
        'nazgul-mark-4-uid': make_mock_run('nazgul'),
        'balrog-mark-9-uid': make_mock_run('balrog')
    }
}
