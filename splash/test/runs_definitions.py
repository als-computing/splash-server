from logging import root
from uuid import uuid4
from splash.api import auth
from databroker.core import RemoteBlueskyEventStream
from xarray import DataArray


class MockRun(dict):
    def __init__(self, data_session):
        self.metadata = {
            'start': {
                'user_id': 'runner_id',
                'uid': str(uuid4()),
                'sample': 'cloudy water',
                'data_session': data_session,
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
        self.primary['image'] = DataArray([[[1.0, 1.0], [0.0, 1.0]]])
        self.primary.metadata = {}
        self.primary.metadata['descriptors'] = []
        self.primary.metadata['descriptors'].append({})
        self.primary.metadata['descriptors'][0]['configuration'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data'] = {}
        self.primary.metadata['descriptors'][0]['configuration']['camera_device']['data']['camera_config_field'] = 'config_value'

        self.thumbnail = Stream()
        self['thumbnail'] = self.thumbnail
        self.thumbnail['image'] = DataArray([[[1.0, 1.0], [0.0, 1.0]]])


class Stream(dict):
    def to_dask(self):
        return self


class Catalog(dict):

    # def __init__(self) -> None:
    #     return super().__init__()

    def search(self, query, skip=0, limit=None):
        data_session_filter = query["$and"][0]["data_session"]
        data_sessions = data_session_filter.get("$in")
        # new_data = {k: v for k, v in self.items() if data_sessions in v.metadata['start']['data_session']}
        new_data = {}
        for k, v in self.items():
            for data_session in data_sessions:
                if data_session in v.metadata['start']['data_session']:
                    new_data[k] = v
        return new_data


child_catalog = Catalog({"same_team_1": MockRun(['same_team']),
                         "other_team_1": MockRun(['other_team']),
                         "same_team_2": MockRun(['same_team'])})

root_catalog = Catalog({"root_catalog": child_catalog})
