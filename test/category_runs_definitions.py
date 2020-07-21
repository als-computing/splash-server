import xarray


class MockStream():
    def __init__(self, metadata):
        self.metadata = metadata
        mock_image = [[1, 2], [3, 4]]
        data_vars = {
            'beamline_energy': ('time', [1, 2, 3, 4, 5]),
            'i_zero': ('time', [-1, -2, -3, -4, -5]),
            'ccd': (('time', 'dim_0', 'dim_1'), [mock_image, mock_image, mock_image, mock_image, mock_image])
        }
        self.dataset = xarray.Dataset(data_vars)

    def to_dask(self):
        return self.dataset.to_dask_dataframe()


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


SAMPLE_DESCRIPTOR = {'data_keys': {'ai_0': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
                                   'ai_3_izero': {'dtype': 'number',
                                                  'shape': [],
                                                  'source': 'ai file'},
                                   'ai_5': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
                                   'ai_6_beamstop': {'dtype': 'number',
                                                     'shape': [],
                                                     'source': 'ai file'},
                                   'ai_7': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
                                   'background': {'dtype': 'number',
                                                  'shape': [],
                                                  'source': 'ai file'},
                                   'beam_current': {'dtype': 'number',
                                                    'shape': [],
                                                    'source': 'ai file',
                                                    'units': 'kev'},
                                   'beamline_energy': {'dtype': 'number',
                                                       'shape': [],
                                                       'source': 'ai file',
                                                       'units': 'epu'},
                                   'ccd': {'dtype': 'array',
                                           'external': 'FILESTORE:',
                                           'shape': [1024, 1024],
                                           'source': 'ai file'},
                                   'ccd_temp': {'dtype': 'number',
                                                'shape': [],
                                                'source': 'ai file',
                                                'units': 'c'},
                                   'coolstage_temp': {'dtype': 'number',
                                                      'shape': [],
                                                      'source': 'ai file',
                                                      'units': 'c'},
                                   'counts': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
                                   'epu_polarization': {'dtype': 'number',
                                                        'shape': [],
                                                        'source': 'ai file'},
                                   'frame_num': {'dtype': 'number',
                                                 'shape': [],
                                                 'source': 'ai file'},
                                   'i_zero': {'dtype': 'number', 'shape': [], 'source': 'ai file'},
                                   'lv_memory': {'dtype': 'number',
                                                 'shape': [],
                                                 'source': 'ai file'},
                                   'pause_trigger': {'dtype': 'number',
                                                     'shape': [],
                                                     'source': 'ai file'},
                                   'photodiode': {'dtype': 'number',
                                                  'shape': [],
                                                  'source': 'ai file'},
                                   'pzt_shutter': {'dtype': 'number',
                                                   'shape': [],
                                                   'source': 'ai file'},
                                   'temperature_controller': {'dtype': 'number',
                                                              'shape': [],
                                                              'source': 'ai file'},
                                   'tey_signal': {'dtype': 'number',
                                                  'shape': [],
                                                  'source': 'ai file'},
                                   'timestamp_error': {'dtype': 'number',
                                                       'shape': [],
                                                       'source': 'ai file'},
                                   'timestamp_server_time': {'dtype': 'number',
                                                             'shape': [],
                                                             'source': 'ai file'},
                                   'timestamp_transmit_time': {'dtype': 'number',
                                                               'shape': [],
                                                               'source': 'ai file'},
                                   'total_flux': {'dtype': 'number',
                                                  'shape': [],
                                                  'source': 'ai file'}}}
