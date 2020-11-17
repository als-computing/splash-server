from logging import log
from attr import dataclass
import logging
from typing import List, Optional


from fastapi import APIRouter, Path, Security, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..service.authorization import AccessDenied
from ..users import User
from . import RunSummary
from .runs_service import (
    CatalogDoesNotExist,
    FrameDoesNotExist,
    BadFrameArgument,
    RunsService)

from splash.api.auth import get_current_user

logger = logging.getLogger("splash.runs_router")

runs_router = APIRouter()


@dataclass
class Services():
    runs: RunsService


services = Services(None)


def set_runs_service(runs_svc: RunsService):
    services.runs = runs_svc


@runs_router.get("", tags=["runs"], response_model=List[str])
def read_catalogs(
        current_user: User = Security(get_current_user)):

    catalog_names = services.runs.list_root_catalogs()
    return catalog_names


@runs_router.get("/{catalog_name}", tags=['runs'], response_model=List[RunSummary])
async def read_catalog(
            catalog_name: str = Path(..., title="name of catalog"),
            current_user: User = Security(get_current_user)):
    try:
        runs = services.runs.get_runs(current_user, catalog_name)
        return runs
    except CatalogDoesNotExist as e:
        logger.error(e)
        raise HTTPException(404, detail=e.args[0])
    except Exception as e:
        logger.error(e)
        raise HTTPException(500, detail=e.args[0])


@runs_router.get("/{catalog_name}/{run_uid}/image", tags=['runs'])
def read_frame(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        field: str = Query(..., title="field containing image"),
        frame: Optional[int] = Query(None, ge=0),
        current_user: User = Security(get_current_user)):
    try:
        jpeg_generator = services.runs.get_slice_image(current_user, catalog_name, run_uid, field, frame)
        return StreamingResponse(jpeg_generator, media_type="image/JPEG")
    except FrameDoesNotExist as e:
        raise HTTPException(400, detail=e.args[0])
    except BadFrameArgument as e:
        raise HTTPException(422, detail=e.args[0])
    except AccessDenied as e:
        raise HTTPException(403, detail=e.args[0])
    except Exception as e:
        logger.error(e)
        raise HTTPException(500, detail=e.args[0])



@runs_router.get("/{catalog_name}/{run_uid}/metadata", tags=['runs'])
def read_frame_metadata(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        frame: Optional[int] = Query(None, ge=0),
        current_user: User = Security(get_current_user)):
    try:
        return_metadata = services.runs.get_slice_metadata(current_user, catalog_name, run_uid, frame)
        return return_metadata
    except FrameDoesNotExist as e:
        raise HTTPException(400, detail=e.args[0])
    except BadFrameArgument as e:
        raise HTTPException(422, detail=e.args[0])
    except Exception as e:
        logger.error(e)
        raise HTTPException(500, detail=e.args[0])
