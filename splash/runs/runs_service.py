import logging
from pathlib import Path
import time

from typing import List

from databroker import catalog
from databroker.projector import project_summary_dict
from pydantic.tools import T

from xarray import Dataset

from . import RunSummary
from ..users import User
from ..service.authorization import TeamBasedChecker, Action, AccessDenied
from ..teams.teams_service import TeamsService
from ..teams import Team

logger = logging.getLogger("splash.runs_service")


class TeamRunChecker(TeamBasedChecker):
    def __init__(self):
        super().__init__()

    def can_do(self, user: User, run_data_groups: List[str], action: Action, teams=List[Team], **kwargs):
        if action == Action.RETRIEVE:
            # This rule is simple...check if the user
            # is a member the team that matches the run
            if not run_data_groups or len(run_data_groups) == 0:
                return False
            for team in teams:
                if team.name in run_data_groups:
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


class ThumbDoesNotExist(Exception):
    pass


class RunsService():
    def __init__(self, teams_service: TeamsService, checker: TeamRunChecker):
        self.teams_service = teams_service
        self.checker = checker
        self._catalog_cache = {}  # caching names saves several orders of magitude on accessing for, say, thumbnails

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
        # print("about to lock")
        # catalog_lock.acquire()
        # print("past lock")
        before = time.perf_counter()
        requested_catalog = None
        run = None
        requested_catalog = self._catalog_cache.get(catalog_name)
        if not requested_catalog:
            try:
                requested_catalog = catalog[catalog_name]
                self._catalog_cache[catalog_name] = requested_catalog
            except KeyError:
                raise CatalogDoesNotExist(f'Catalog name: {catalog_name} is not a catalog')
        
        try:
            run = requested_catalog[uid]
        except KeyError:
            raise RunDoesNotExist(f'Run uid: {uid} does not exist')

        run_auth = run.metadata['start'].get('data_groups')
        if run_auth is None:
            raise AccessDenied

        if not self.checker.can_do(user, run_auth, Action.RETRIEVE, teams=user_teams):
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"User {user.name} can't retrieve {catalog_name}: {uid}")
            raise AccessDenied
        return run, requested_catalog

    def get_run_thumb(self, user: User, catalog_name, uid):
        """Retrieves image preview of run specified by `catalog_name` and `uid`.
        Returns a file object representing a compressed jpeg image by default.
        If `raw_bytes` is set to `True`, then it returns a generator
        for streaming the entire image as bytes"""
        requested_catalog = self._get_run(user, catalog_name, uid)[1]
        try:
            thumbs_dir = Path(requested_catalog.root_map['thumbs'])
        except KeyError:
            raise ThumbDoesNotExist((f"catalog {catalog_name} does not have a thumbnail root configured." +
                                    "The the intake cofiguration for this source, there must be a root_map entry" +
                                    "called thuumbs."))

        file_name = uid + ".png"
        file = thumbs_dir / file_name
        if not file.exists():
            raise ThumbDoesNotExist(f"Thumb file does not exist for catalog {catalog_name} and uid {uid}")
        return file

    #  temporarily removed until support is re-introduced
    # def get_slice_image(self,     user: User, catalog_name, uid, slice=0, raw_bytes=False, image_field=None):
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
        run = self._get_run(user, catalog_name, uid)[0]
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
                run_auth = runs[uid].metadata['start'].get('data_groups')
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
        queries.append({"data_groups": {"$in": teams}})
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
    run['experimenter_name'] = dataset.get('experimenter_name')
    run['experiment_title'] = dataset.get('experiment_title')
    run['collection_date'] = dataset.get('collection_time')
    run['instrument_name'] = dataset.get('instrument_name')
    run['sample_name'] = dataset.get('sample_name')
    run['station'] = dataset.get('instrument_name')
    return RunSummary(**run)
