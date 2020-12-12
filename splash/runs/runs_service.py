import logging
from typing import List


from databroker import catalog
from databroker.projector import project_summary_dict

from xarray import Dataset

from . import RunSummary
from ..users import User
from ..service.authorization import TeamBasedChecker, Action, AccessDenied
from ..teams.teams_service import TeamsService
from ..teams import Team
import sys
import numpy as np
from PIL import Image, ImageOps
import io

logger = logging.getLogger("splash.runs_service")


class TeamRunChecker(TeamBasedChecker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: User, run_data_session: List[str], action: Action, teams=List[Team], **kwargs):
        if action == Action.RETRIEVE:
            # This rule is simple...check if the user
            # is a member the team that matches the run
            if not run_data_session or len(run_data_session) == 0:
                return False
            for team in teams:
                if team.name in run_data_session:
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

    def _get_user_teams(self, user: User):
        user_teams = self.teams_service.get_user_teams(user, user.uid)
        if not user_teams:
            if logger.isEnabledFor(logging.INFO):
                logger.info(f"User {user.name} not a member of any team, can't view runs")
            raise AccessDenied("User not a member of any teams")
        return list(user_teams)

    def _get_run(self, user: User, catalog_name, uid):
        # get the user's teams...if they're not in one, get out quick
        user_teams = self._get_user_teams(user)

        # can this user see the run?
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')
        run = catalog[catalog_name][uid]

        if not run:
            raise RunDoesNotExist(f'Run uid: {uid} does not exist')

        run_auth = run.metadata['start'].get('data_session')
        if run_auth is None:
            raise AccessDenied

        if not self.checker.can_do(user, run_auth, Action.RETRIEVE, teams=user_teams):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"User {user.name} can't retrieve {catalog_name}: {uid}")
            raise AccessDenied
        return run

    def get_run_thumb(self, user: User, catalog_name, uid, slice=0):
        """Retrieves image preview of run specified by `catalog_name` and `uid`.
        Returns a file object representing a compressed jpeg image by default.
        If `raw_bytes` is set to `True`, then it returns a generator
        for streaming the entire image as bytes"""

        run = self._get_run(user, catalog_name, uid)
        try:
            run['thumbnail']
        except KeyError:
            raise FrameDoesNotExist("run does not have thumbnail stream")
        thumb_key = ""
        try:
            thumb_key = list(run.thumbnail.to_dask().keys())[0]  # this is a kludge, get first key of dataset
        except IndexError:
            raise FrameDoesNotExist("stream field empty, no slices for thumbnail")
        dataset = run.thumbnail.to_dask()[thumb_key]
        image_data = None
        try:
            if not slice:
                slice = 0
            image_data = dataset[slice]
        except(IndexError):
            raise FrameDoesNotExist(f'Frame number: {slice}, does not exist.')
        return convert_raw(image_data)   

    #  temporarily removed until support is re-introduced
    # def get_slice_image(self, user: User, catalog_name, uid, slice=0, raw_bytes=False, image_field=None):
    #     """Retrieves image preview of run specified by `catalog_name` and `uid`.
    #     Returns a file object representing a compressed jpeg image by default.
    #     If `raw_bytes` is set to `True`, then it returns a generator
    #     for streaming the entire image as bytes"""

    #     dataset, issues = self._get_run(user, catalog_name, uid)
    #     dataset, issues = project_xarray(run)
    #     image_data = dataset['image_data'].squeeze()

    #     try:
    #         if not slice:
    #             slice = 0
    #         image_data = image_data[slice]
    #     except(IndexError):
    #         raise FrameDoesNotExist(f'Frame number: {slice}, does not exist.')

    #     if raw_bytes:
    #         return stream_image_as_bytes(image_data), issues
    #     else:
    #         file_object = convert_raw(image_data)
    #         return file_object, issues

    # def get_slice_data(self, user: User, catalog_name, uid, slice=0):
    #     """Retrieves non-image, single point data of a run's slice specified by `catalog_name` and `uid`.
    #     Returns a file object representing a compressed jpeg image by default.
    #     If `raw_bytes` is set to `True`, then it returns a generator
    #     for streaming the entire image as bytes"""

    #     dataset, issues = self._get_projected_dataset(user, catalog_name, uid)
    #     image_data = dataset['image_data'].squeeze()

    #     try:
    #         if not slice:
    #             slice = 0
    #         image_data = image_data[slice]
    #     except(IndexError):
    #         raise FrameDoesNotExist(f'Frame number: {slice}, does not exist.')

    def get_run_metadata(self, user: User, catalog_name, uid) -> RunSummary:
        run = self._get_run(user, catalog_name, uid)
        dataset, issues = project_summary_dict(run)
        run_summary = run_summary_from_dataset(uid, dataset)
    
        return run_summary, issues

    def list_root_catalogs(self):
        return list(catalog)

    def get_runs(self,
                 user: User,
                 catalog_name,
                 skip=0,
                 limit=100,
                 text_query=None,
                 from_query=None,
                 to_query=None) -> List[RunSummary]:
        if catalog_name not in catalog:
            raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')

        user_teams = list(self.teams_service.get_user_teams(user, user.uid))
        teams_list = []
        for team in user_teams:
            teams_list.append(team.name)
        query = self._build_runs_query(teams_list, text_query, from_query, to_query)
        # runs = catalog[catalog_name].search({"data_session": {"$in": teams_list}})
        runs = catalog[catalog_name].search(
            query,
            skip=skip,
            limit=limit)
        if len(runs) == 0:
            logger.info(f'catalog: {catalog_name} has no runs')
            return []

        return_runs = []
        for uid in runs:
            try:
                run_auth = runs[uid].metadata['start'].get('data_session')
                if run_auth is None:
                    continue
                if not self.checker.can_do(user, run_auth, Action.RETRIEVE, teams=user_teams):
                    if logger.isEnabledFor(logging.DEBUG):
                        logger.debug(f"User {user.name} can't retrieve {catalog_name}: {uid}")
                    continue
                dataset, issues = project_summary_dict(runs[uid])
                if issues and logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"projection encountered issues: {str(issues)}")
                run_summary = run_summary_from_dataset(uid, dataset)
                return_runs.append(run_summary)
            except Exception as e:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"skipping run: {e.args[0]}")

            # can this user see this run?          
        return return_runs

    @staticmethod
    def _build_runs_query(teams=None, text_search=None, from_query=None, to_query=None):
        queries = []
        queries.append({"data_session": {"$in": teams}})
        if text_search:
            queries.append({"$text": {"$search": text_search}})
        if from_query:
            queries.append({"time": {"$gte": from_query}})
        if to_query:
            queries.append({"time": {"$lte": to_query}})
        query = {"$and": queries}
        return query


def run_summary_from_dataset(uid: str, dataset: Dataset) -> RunSummary:
    run = {}
    run['uid'] = uid
    # run['data_session'] = dataset.get('data_session')
    run['experimenter_name'] = dataset.get('experimenter_name')
    run['experiment_title'] = dataset.get('experiment_title')
    run['collection_date'] = dataset.get('collection_time')
    run['instrument_name'] = dataset.get('instrument_name')
    run['sample_name'] = dataset.get('sample_name')
    run['station'] = dataset.get('instrument_name')
    return RunSummary(**run)


# def validate_frame_num(frame):
#     frame_number = frame
#     if not is_integer(frame_number):
#         raise BadFrameArgument('Frame number must be an integer, represented as an integer, string, or float.')
#     frame_number = int(frame)

#     if frame_number < 0:
#         raise BadFrameArgument('Frame number must be a positive integer')
#     return frame_number


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
