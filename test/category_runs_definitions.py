import xarray
SAMPLE_DESCRIPTOR = {'data_keys': {
    'beamline_energy': {'dtype': 'number',
                        'shape': [],
                        'source': 'ai file',
                        'units': 'epu'},
    'ccd': {'dtype': 'array',
            'external': 'FILESTORE:',
            'shape': [1024, 1024],
            'source': 'ai file'},

    'i_zero': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
}}

MOCK_IMAGE = xarray.DataArray([[1, 2], [3, 4]])
BEAMLINE_ENERGY_VALS = [1, 2, 3, 4, 5]
I_ZERO_VALS = [-1, -2, -3, -4, -5]
CCD = [MOCK_IMAGE+1, MOCK_IMAGE+2, MOCK_IMAGE+3, MOCK_IMAGE+4, MOCK_IMAGE+5]

class MockStream():
    def __init__(self, metadata):
        self.metadata = metadata
        data_vars = {
            'beamline_energy': ('time', BEAMLINE_ENERGY_VALS),
            'i_zero': ('time', I_ZERO_VALS),
            'ccd': (('time', 'dim_0', 'dim_1'), CCD)
        }
        self.dataset = xarray.Dataset(data_vars)

    def to_dask(self):
        return self.dataset


class MockRun():
    def __init__(self, sample='', datafile='', num_images=3):
        self.metadata = {
            'start': {
                'sample': '',
                'data_file': ''
            },
            'stop': {
                'num_events':
                {'primary': 0}
            }
        }
        self.metadata['stop']['num_events']['primary'] = num_images
        self.metadata['start']['sample'] = sample
        self.metadata['start']['data_file'] = datafile

        metadata_with_descriptors = {'descriptors': [SAMPLE_DESCRIPTOR]}
        metadata_with_descriptors.update(self.metadata)
        self.primary = MockStream(metadata_with_descriptors)

    def __getitem__(self, key):
        if key == 'primary':
            return self.primary
        raise KeyError(f'Key: {key}, does not exist')

    def __iter__(self):
        yield 'primary'


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
