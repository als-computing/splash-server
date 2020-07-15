from databroker import catalog
from databroker.core import BlueskyRun
from splash.categories.runs import bluesky_utils
import sys
import numpy as np
from PIL import Image, ImageOps
import io


class CatalogDoesNotExist(Exception):
    pass


class RunDoesNotExist(Exception):
    pass


class RunService():
    def __init__(self):
        return

    def get_image(self, catalog_name, uid,  raw_bytes=False):
        """Retrieves image preview of run specified by `catalog_name` and `uid`.
        Returns a file object representing a compressed jpeg image by default.
        If `raw_bytes` is set to `True`, then it returns a generator
        for streaming the entire image as bytes"""
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

        runs = catalog[catalog_name]

        if uid not in runs:
            raise RunDoesNotExist(f'Run uid: {uid} does not exist')

        run = runs[uid]
        stream, field = guess_stream_field(run)
        data = getattr(run, stream).to_dask()[field].squeeze()
        for i in range(len(data.shape) - 2):
            data = data[0]

        if raw_bytes:
            return stream_image_as_bytes(data)
        else:
            return convert_raw(data)

    def list_catalogs(self):
        return list(catalog)

    def list_runs(self, catalog_name):
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

        return list(catalog[catalog_name])


def guess_stream_field(catalog: BlueskyRun):
    # TODO: use some metadata (techniques?) for guidance about how to get a preview

    for stream in ['primary', *bluesky_utils.streams_from_run(catalog)]:
        descriptor = bluesky_utils.descriptors_from_stream(catalog, stream)[0]
        fields = bluesky_utils.fields_from_descriptor(descriptor)
        for field in fields:
            field_ndims = bluesky_utils.ndims_from_descriptor(descriptor, field)
            if field_ndims > 1:
                return stream, field


def ensure_small_endianness(dataarray):
    byteorder = dataarray.data.dtype.byteorder
    if byteorder == '=' and sys.byteorder == 'little':
        return dataarray
    elif byteorder == '<':
        return dataarray
    elif byteorder == '|':
        return dataarray
    elif byteorder == '=' and sys.byteorder == 'big':
        return dataarray.data.byteswap().newbyteorder()
    elif byteorder == '>':
        return dataarray.data.byteswap().newbyteorder()


# This function should yield the array in 32 row chunks
def stream_image_as_bytes(dataarray):
    # TODO generalize the function for any sized image
    for chunk_beginning in range(0, 1024, 32):
        chunk_end = chunk_beginning + 32
        chunk = dataarray[chunk_beginning:chunk_end].compute()
        chunk = ensure_small_endianness(chunk)
        yield bytes(chunk.data)


def convert_raw(data):
    log_image = np.array(data.compute())
    log_image = log_image - np.min(log_image) + 1.001
    log_image = np.log(log_image)
    log_image = 205*log_image/(np.max(log_image))
    auto_contrast_image = Image.fromarray(log_image.astype('uint8'))
    auto_contrast_image = ImageOps.autocontrast(
                            auto_contrast_image, cutoff=0.1)
    # auto_contrast_image = resize(np.array(auto_contrast_image),
                                            # (size, size))
                        
    file_object = io.BytesIO()

    auto_contrast_image.save(file_object, format='JPEG')

    # move to beginning of file so `send_file()` will read from start    
    file_object.seek(0)

    return file_object
