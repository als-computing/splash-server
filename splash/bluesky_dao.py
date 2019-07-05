from splash.data import Dao
from intake_bluesky.mongo_normalized import BlueskyMongoCatalog

class IntakeBlueSkyDao(Dao):

    def __init__(self, metadatastore_db, asset_registry_db):
        self.catalog = BlueskyMongoCatalog(metadatastore_db, asset_registry_db)

    def retrieve(self, uid):
       run_catalog = self.catalog[uid]

       return RunData(run_catalog.metadata, run_catalog)


class RunData():
    def __init__(self, metadata, run_catalog):
        self._metadata = metadata
        self._run_catalog = run_catalog

    def __call__(self, *args, **kwargs):
        yield from self._run_catalog.read_canonical()

    @property
    def metadata(self):
        return self._metadata


