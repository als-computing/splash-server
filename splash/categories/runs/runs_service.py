from databroker import catalog
from databroker.core import BlueskyRun
from splash.categories.runs import bluesky_utils


class CatalogDoesNotExist(Exception):
    pass


class RunDoesNotExist(Exception):
    pass


class RunService():
    def __init__(self):
        return

    def get_preview(self, uid, catalog_name):
        print(list(catalog))
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

        runs = catalog[catalog_name]

        if uid not in runs:
            raise RunDoesNotExist(f'Run uid: {uid} does not exist')

        run = runs[uid]
        stream, field = self.guess_stream_field(run)
        data = getattr(run, stream).to_dask()[field].squeeze()
        for i in range(len(data.shape) - 2):
            data = data[0]
        return data.compute()

    def guess_stream_field(self, catalog: BlueskyRun):
        # TODO: use some metadata (techniques?) for guidance about how to get a preview

        for stream in ['primary', *bluesky_utils.streams_from_run(catalog)]:
            descriptor = bluesky_utils.descriptors_from_stream(catalog, stream)[0]
            fields = bluesky_utils.fields_from_descriptor(descriptor)
            for field in fields:
                field_ndims = bluesky_utils.ndims_from_descriptor(descriptor, field)
                if field_ndims > 1:
                    return stream, field
