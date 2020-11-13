from datetime import datetime
import logging
from os import name
from typing import Any, Dict, List, Optional

from databroker import catalog
from databroker.projector import project_xarray
from pydantic import BaseModel, Field
from xarray import Dataset

from splash.models.users import UserModel
from splash.service.authorization import TeamBasedChecker, Action
from splash.teams.service import TeamsService
from splash.teams.models import Team
import sys
import numpy as np
from PIL import Image, ImageOps
import io

SPLASH_DATA_FIELD = 'splash_data'
SPLASH_DARKS_FIELD = 'splash_darks'
SPLASH_ENERGY_FIELD = 'splash_energy'
SPLASH_SAMPLE_NAME_FIELD = 'splash_sample_name'
SPLASH_DATA_COLLECTOR_FIELD = 'splash_collector'


logger = logging.getLogger("splash_server.runs_service")


class DataPoint(BaseModel):
    value: Any
    units: Optional[str]


class RunSummary(BaseModel):
    # beamline_energy: Optional[DataPoint] = Field(None, title="Beamline energy")
    collector_name: str = Field(None, title="name of user or entity that performed collection")
    collection_team: str = Field(None, title="Team that collected the run. e.g. PI name, safety form, proposal number")
    team: str = Field(None, title="Team that collected the data")
    collection_date: datetime = Field(None, title="run colleciton date")
    instrument_name: Optional[str] = Field(
        None, title="name of the instrument (beamline, etc) where data collection was performed")
    num_data_images: Optional[int] = Field(None, title="number of data collection images")
    sample_name: Optional[str] = Field(None, title="sample name")
    uid: str

    class Config:
        title = "Summary information for a run, intended to be used by "\
              "applications when a brief view is needed, as in a list of runs"


class TeamRunChecker(TeamBasedChecker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: UserModel, run: RunSummary, action: Action, teams=List[Team], **kwargs):
        if action == Action.RETRIEVE:
            # This rule is simple...check if the user
            # is a member the team that matches the run
            for team in teams:
                if team.name == run.collection_team:
                    return True
        return False


class CatalogDoesNotExist(Exception):
    pass


class RunDoesNotExist(Exception):
    pass


class BadFrameArgument(Exception):
    pass


class FieldDoesNotExist(Exception):
    pass


class FrameDoesNotExist(Exception):
    pass


class RunsService():
    def __init__(self, teams_service: TeamsService, checker: TeamRunChecker):
        self.teams_service = teams_service
        self.checker = checker

    def get_image(self, catalog_name, uid, frame, raw_bytes=False):
        """Retrieves image preview of run specified by `catalog_name` and `uid`.
        Returns a file object representing a compressed jpeg image by default.
        If `raw_bytes` is set to `True`, then it returns a generator
        for streaming the entire image as bytes"""
        frame_number = validate_frame_num(frame)
        dataset = return_dask_dataset(catalog_name, uid)
        image_data = dataset[SPLASH_DATA_FIELD].squeeze()

        try:
            image_data = image_data[frame_number]
        except(IndexError):
            raise FrameDoesNotExist(f'Frame number: {frame_number}, does not exist.')

        if raw_bytes:
            return stream_image_as_bytes(image_data)
        else:
            file_object = convert_raw(image_data)
            return file_object

    def get_slice_metadata(self, user: UserModel, catalog_name, uid, field, slice) -> List:
        user_teams = self.teams_service.get_user_teams(user, user.uid)
        if not user_teams:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f"User {user.name} not a member of any team, can't view runs")
            return []
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')
        slice = validate_frame_num(slice)
        dataset = project_xarray(catalog[catalog_name][uid])
       
        if field not in dataset:
            raise FieldDoesNotExist(f'Field {field} not created after projecting {catalog_name}: {uid}')

        # can this user see it?
        run_summary = run_summary_from_dataset(uid, dataset)
        if not self.checker.can_do(user, run_summary, Action.RETRIEVE, teams=user_teams):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"User {user.name} can't retrieve {catalog_name}: {uid}")
            return []
        try:
            return dataset[field].attrs['configuration'][slice]
        except(IndexError):
            raise FrameDoesNotExist(f'Slice number: {slice}, does not exist.')


    def list_root_catalogs(self):
        return list(catalog)


    def get_runs(self, user: UserModel, catalog_name) -> List[RunSummary]:
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')
        runs = catalog[catalog_name]
        if len(runs) == 0:
            logger.info(f'catalog: {catalog_name} has no runs')
            return []
        user_teams = self.teams_service.get_user_teams(user, user.uid)
        if not user_teams:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f"User {user.name} not a member of any team, can't view runs")
            return []
        return_runs = []
        for uid in runs:
            dataset = project_xarray(runs[uid])
            run_summary = run_summary_from_dataset(uid, dataset)
            # can this user see this run?
            if not self.checker.can_do(user, run_summary, Action.RETRIEVE, teams=user_teams):
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"User {user.name} can't retrieve {catalog_name}: {uid}")
                continue
            return_runs.append(run_summary)
        return return_runs


def return_dask_dataset(catalog_name, uid):
    if catalog_name not in catalog:
        raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

    runs = catalog[catalog_name]

    if uid not in runs:
        raise RunDoesNotExist(f'Run uid: {uid} does not exist')

    return project_xarray(runs[uid])


def run_summary_from_dataset(uid: str, dataset: Dataset):
    run = {}
    run['uid'] = uid
    run['collector_name'] = dataset.attrs.get('collector_name')
    run['collection_team'] = dataset.attrs.get('collection_team')
    run['collection_date'] = dataset.attrs.get('collection_date')
    run['instrument_name'] = dataset.attrs.get('instrument_name')
    run['sample_name'] = dataset.attrs.get('sample_name')
    run['station'] = dataset.attrs.get('station')
    run['num_data_images'] = dataset.attrs.get('num_data_images')
    run['num_data_images'] = dataset.attrs.get('num_data_images')
    return RunSummary(**run)


def validate_frame_num(frame):
    frame_number = frame
    if not is_integer(frame_number):
        raise BadFrameArgument('Frame number must be an integer, represented as an integer, string, or float.')
    frame_number = int(frame)

    if frame_number < 0:
        raise BadFrameArgument('Frame number must be a positive integer')
    return frame_number


# def guess_stream_field(catalog: BlueskyRun):
#     # TODO: use some metadata (techniques?) for guidance about how to get a preview

#     for stream in ['primary', *bluesky_utils.streams_from_run(catalog)]:
#         descriptor = bluesky_utils.descriptors_from_stream(catalog, stream)[0]
#         fields = bluesky_utils.fields_from_descriptor(descriptor)
#         for field in fields:
#             field_ndims = bluesky_utils.ndims_from_descriptor(descriptor, field)
#             if field_ndims > 1:
#                 return stream, field


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
