from pydantic import parse_obj_as
import pytest
from xarray import DataArray

from splash.models.users import UserModel


class MockRun(dict):
    def __init__(self, team):
        self.metadata = {
            'start': {
                'user_id': 'runner_id',
                'team': team,
                'sample': 'cloudy water',
                'projections': [
                    {
                        'name': 'foo',
                        'version': '1.0',
                        'configuration': 'why is this required?',
                        'projection': {
                            'collection_team': {
                                'type': 'linked',
                                'location': 'start',
                                'field': 'team'
                            },
                            'sample_name': {
                                'type': 'linked',
                                'location': 'start',
                                'field': 'sample'
                            },
                            'image_data': {
                                'type': 'linked',
                                'location': 'event',
                                'stream': 'primary',
                                'field': 'image'
                            },
                            'beamline_energy': {
                                'type': 'linked',
                                'location': 'event',
                                'stream': 'primary',
                                'field': 'energy'
                            },
                            'primary_config_field': {
                                'type': 'linked',
                                'location': 'configuration',
                                'stream': 'primary',
                                'config_device': 'camera_device',
                                'config_index': 0,
                                'field': 'camera_config_field'
                            }
                        }
                    }
                ]
            },
        }
        self.primary = Stream()
        # self.primary = type('MockStream', (dict,), {})()
        self['primary'] = self.primary
        self.primary['energy'] = DataArray([1.21, 1.22])
        self.primary['image'] = DataArray([[1.0, 1.0], [0.0, 1.0]])
        self.primary.metadata = {}
        self.primary.metadata['descriptors'] = []
        self.primary.metadata['descriptors'].append({})
        self.primary.metadata['descriptors'][0]['configuration'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data']['camera_config_field'] = 'config_value'


class Stream(dict):
    def to_dask(self):
        return self


root_catalog = {
        "root_catalog": {
                'same_team_1': MockRun('same_team'),
                'other_team_1': MockRun('other_team'),
                'same_team_2': MockRun('same_team'),
        }
    }
