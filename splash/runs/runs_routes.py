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
    ThumbDoesNotExist,
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
def read_catalog(
            catalog_name: str = Path(..., title="name of catalog"),
            current_user: User = Security(get_current_user),
            skip: Optional[int] = Query(None, ge=0),
            limit: Optional[int] = Query(None, ge=0),
            text_query: Optional[str] = Query(None),
            fromDT: Optional[int] = Query(None),
            toDT: Optional[int] = Query(None)):
    try:
        runs = (services.runs.get_runs(current_user, catalog_name, skip=skip,
                limit=limit, text_query=text_query, from_query=fromDT, to_query=toDT))
        return runs
    except CatalogDoesNotExist as e:
        logger.error(e)
        raise HTTPException(404, detail=e.args[0])
    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(500, detail=str(e))

#  temporarily removed until support is re-introduced
# @runs_router.get("/{catalog_name}/{run_uid}/image", tags=['runs'])
# def read_frame(
#         catalog_name: str = Path(..., title="catalog name"),
#         run_uid: str = Path(..., title="run uid"),
#         frame: Optional[int] = Query(None, ge=0),
#         current_user: User = Security(get_current_user)):
#     try:
#         jpeg_generator, issues = services.runs.get_slice_image(current_user, catalog_name, run_uid, frame)
#         return StreamingResponse(jpeg_generator, media_type="image/JPEG")
#     except FrameDoesNotExist as e:
#         raise HTTPException(400, detail=e.args[0])
#     except BadFrameArgument as e:
#         raise HTTPException(422, detail=e.args[0])
#     except AccessDenied:
#         raise HTTPException(403)
#     # except Exception as e:
#     #     logger.error(e)
#     #     raise HTTPException(500, detail=str(e))



@runs_router.get("/{catalog_name}/{run_uid}/metadata", tags=['runs'])
def read_run_metadata(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        current_user: User = Security(get_current_user)):
    try:
        return_metadata, issues = services.runs.get_run_metadata(current_user, catalog_name, run_uid)
        return return_metadata
    except ThumbDoesNotExist as e:
        raise HTTPException(400, detail=e.args[0])
    except BadFrameArgument as e:
        raise HTTPException(422, detail=e.args[0])
    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(500, detail=str(e))

@runs_router.get("/{catalog_name}/{run_uid}/stream/{stream_name}/configuration", tags=['runs'])
def read_stream_configuration(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        stream_name: str = Path(..., title="stream name"),
        current_user: User = Security(get_current_user)):
        return_metadata = services.runs.get_stream_configuration(current_user, catalog_name, run_uid, stream_name)
        return return_metadata

@runs_router.get("/{catalog_name}/{run_uid}/thumb", tags=['runs'])
def read_run_thumb(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        current_user: User = Security(get_current_user)):
    try:
        return_file = services.runs.get_run_thumb(current_user, catalog_name, run_uid)
        file = open(return_file, "rb")
        file.seek(0)
        return StreamingResponse(generate_chunks(file), media_type="image/PNG")
    except ThumbDoesNotExist as e:
        raise HTTPException(404, detail=e.args[0])
    except BadFrameArgument as e:
        raise HTTPException(422, detail=e.args[0])
    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(500, detail=str(e))


def generate_chunks(file):
    for chunk in iter(lambda: file.read(4096), b''):
        yield chunk
    file.close()
