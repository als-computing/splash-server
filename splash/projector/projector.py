from databroker.core import BlueskyRun
import xarray


class ProjectionError(Exception):
    pass


class UnkownLocation(ProjectionError):
    pass


def project(run: BlueskyRun):
    #TODO: do validation on projections object in order to make more descriptive 
    # errors
    try:
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
                raise UnkownLocation(f'Unknown location: {location} in projection.')
    except Exception as e:
        if isinstance(e, UnkownLocation):
            raise
        raise ProjectionError('Error with projecting run')
    return xarray.Dataset(data_vars, attrs=attrs)







