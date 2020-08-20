import xarray

MOCK_IMAGE = xarray.DataArray([[1, 2], [3, 4]])
BEAMLINE_ENERGY_VALS = [1, 2, 3, 4, 5]
I_ZERO_VALS = [-1, -2, -3, -4, -5]
CCD = [MOCK_IMAGE+1, MOCK_IMAGE+2, MOCK_IMAGE+3, MOCK_IMAGE+4, MOCK_IMAGE+5]


class MockStream():
    def __init__(self, metadata):
        self.metadata = metadata
        data_vars = {
            'beamline_energy': ('time', BEAMLINE_ENERGY_VALS),
            'ccd': (('time', 'dim_0', 'dim_1'), CCD)
        }
        self.dataset = xarray.Dataset(data_vars)
        self.to_dask_counter = 0

    def to_dask(self):
        # This enables us to test that the to_dask function is called
        # the appropriate number of times.
        # It would be better if we could actually return the dataset as a dask dataframe
        # However, for some reason this won't let us access the arrays
        #  by numeric index and will throw an error
        self.to_dask_counter += 1
        return self.dataset


class MockRun():
    def __init__(self, projections=[], sample='',):
        self.metadata = {
            'start': {
                'sample': '',
                'projections': []
            },
            'stop': {}
        }
        self.metadata['start']['sample'] = sample
        self.metadata['start']['projections'] = projections
        self.primary = MockStream(self.metadata)

    def __getitem__(self, key):
        if key == 'primary':
            return self.primary
        raise KeyError(f'Key: {key}, does not exist')


def make_mock_run(projections, sample):
    return MockRun(projections, sample)


