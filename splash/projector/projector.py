from databroker.core import BlueskyRun
import xarray


def project(run: BlueskyRun):
    configuration = run.metadata['start']
    projection = configuration['projections'][0]['projection']
    attrs = {}
    data_vars = {}
    for nexfield, mapping in projection.items():
        location = mapping['location']
        field = mapping['field']
        stream = None
        if location == 'event':
            stream = mapping['stream']
            data_vars[nexfield] = run[stream].to_dask()[field]
        elif location == 'configuration':
            attrs[nexfield] = configuration[field]
        else:
            raise KeyError(f'Unknown location: {location} in projection.')
    return xarray.Dataset(data_vars, attrs=attrs)







