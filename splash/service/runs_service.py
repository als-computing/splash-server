from typing import List
from databroker import catalog
from databroker.core import BlueskyRun
from splash.service.projector.projector import project
import sys
import numpy as np
from PIL import Image, ImageOps
import io

NEX_IMAGE_FIELD = '/entry/instrument/detector/data'
NEX_ENERGY_FIELD = '/entry/instrument/monochromator/energy'
NEX_SAMPLE_NAME_FIELD = '/entry/sample/name'


class CatalogDoesNotExist(Exception):
    pass


class RunDoesNotExist(Exception):
    pass


class BadFrameArgument(Exception):
    pass


class FrameDoesNotExist(Exception):
    pass


class RunsService():
    def __init__(self):
        return

    def get_image(self, catalog_name, uid, frame, raw_bytes=False):
        """Retrieves image preview of run specified by `catalog_name` and `uid`.
        Returns a file object representing a compressed jpeg image by default.
        If `raw_bytes` is set to `True`, then it returns a generator
        for streaming the entire image as bytes"""
        frame_number = validate_frame_num(frame)
        dataset = return_dask_dataset(catalog_name, uid)
        image_data = dataset[NEX_IMAGE_FIELD].squeeze()

        try:
            image_data = image_data[frame_number]
        except(IndexError):
            raise FrameDoesNotExist(f'Frame number: {frame_number}, does not exist.')

        if raw_bytes:
            return stream_image_as_bytes(image_data)
        else:
            file_object = convert_raw(image_data)
            return file_object

    def get_metadata(self, catalog_name, uid, frame,):
        frame_number = validate_frame_num(frame)
        dataset = return_dask_dataset(catalog_name, uid)
        try:
            beamline_energy = dataset[NEX_ENERGY_FIELD][frame_number].compute().item()
        except(IndexError):
            raise FrameDoesNotExist(f'Frame number: {frame_number}, does not exist.')
        return {NEX_ENERGY_FIELD: beamline_energy}

    def list_root_catalogs(self):
        return list(catalog)

    def get_runs(self, catalog_name) -> List:
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')
        runs = catalog[catalog_name]
        return_runs = []
        for uid in runs:
            run = {}
            run['uid'] = uid
            dataset = project(runs[uid])
            run['num_images'] = dataset[NEX_ENERGY_FIELD].shape[0]
            run[NEX_SAMPLE_NAME_FIELD] = dataset.attrs[NEX_SAMPLE_NAME_FIELD]
            return_runs.append(run)
        return return_runs


def return_dask_dataset(catalog_name, uid):
    if catalog_name not in catalog:
        raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

    runs = catalog[catalog_name]

    if uid not in runs:
        raise RunDoesNotExist(f'Run uid: {uid} does not exist')

    return project(runs[uid])


def validate_frame_num(frame):
    frame_number = frame
    if not is_integer(frame_number):
        raise BadFrameArgument('Frame number must be an integer, represented as an integer, string, or float.')
    frame_number = int(frame)

    if frame_number < 0:
        raise BadFrameArgument('Frame number must be a positive integer')
    return frame_number


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


def generate_buffer(buffer: io.BytesIO, chunk_size: int):
    reader = io.BufferedReader(buffer, chunk_size)
    for chunk in reader:
        yield chunk


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
    file_buffer = io.BytesIO()

    auto_contrast_image.save(file_buffer, format='JPEG')

    # move to beginning of file so `send_file()` will read from start    
    file_buffer.seek(0)
    return generate_buffer(file_buffer, 2048)


def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()
