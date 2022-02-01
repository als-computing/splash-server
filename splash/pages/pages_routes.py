from starlette.responses import JSONResponse
from splash.api.models import PatchBody
from attr import dataclass


from fastapi import APIRouter, Security, HTTPException, Response
from typing import List, Optional
from fastapi.param_functions import Header, Query
from pydantic import parse_obj_as, BaseModel

from . import Page, NewPage, UpdatePage
from ..users import User
from splash.api.auth import get_current_user
from .pages_service import PagesService
from ..service.base import ArchiveConflictError, ObjectNotFoundError, RestoreConflictError, VersionNotFoundError
from ..service import VersionedSplashMetadata

pages_router = APIRouter()


@dataclass
class Services:
    pages: PagesService

services = Services(None)


def set_pages_service(pages_svc: PagesService):
    services.pages = pages_svc


class NumVersionsResponse(BaseModel):
    number: int


class CreatePageResponse(BaseModel):
    uid: str
    splash_md: VersionedSplashMetadata


@pages_router.get("", tags=["pages"], response_model=List[Page])
def read_pages(
    current_user: User = Security(get_current_user),
    page: Optional[int] = Query(1, gt=0),
    page_size: Optional[int] = Query(10, gt=0),
):
    pages = services.pages.retrieve_multiple(
        current_user, page=page, page_size=page_size
    )
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.get(
    "/num_versions/{uid}", tags=["pages"], response_model=NumVersionsResponse
)
def get_num_versions(uid: str, current_user: User = Security(get_current_user)):
    try:
        num_versions = services.pages.get_num_versions(current_user, uid)
    except ObjectNotFoundError:
        raise HTTPException(status_code=404, detail="object not found")
    return NumVersionsResponse(number=num_versions)


@pages_router.get("/page_type/{page_type}", tags=["pages"], response_model=List[Page])
def get_pages_by_type(
    page_type: str,
    current_user: User = Security(get_current_user),
    page: Optional[int] = Query(1, gt=0),
    page_size: Optional[int] = Query(10, gt=0),
):
    pages = services.pages.retrieve_by_page_type(
        current_user, page_type, page, page_size
    )
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.get("/archived", tags=["pages"], response_model=List[Page])
def retrieve_archived_pages(
    current_user: User = Security(get_current_user),
    page: Optional[int] = Query(1, gt=0),
    page_size: Optional[int] = Query(10, gt=0),
):
    pages = services.pages.retrieve_archived(
        current_user, page, page_size
    )
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.get("/{uid}", tags=["pages"])
def read_page(
    uid: str,
    version: Optional[int] = Query(None, gt=0),
    current_user: User = Security(get_current_user),
):

    if version is not None:
        try:
            page = services.pages.retrieve_version(current_user, uid, version)
        except VersionNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="version not found",
            )
        except ObjectNotFoundError:
            raise HTTPException(
                status_code=404,
                detail="object not found",
            )
        return page
    else:
        page = services.pages.retrieve_one(current_user, uid)
        if page is None:
            raise HTTPException(
                status_code=404,
                detail="object not found",
            )
        return page


@pages_router.put(
    "/{uid}",
    tags=["pages"],
    response_model=CreatePageResponse,
)
def replace_page(
    uid: str,
    page: UpdatePage,
    current_user: User = Security(get_current_user),
    if_match: Optional[str] = Header(None),
):
    try:
        update_response = services.pages.update(current_user, page, uid, etag=if_match)
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="object not found",
        )

    return update_response


@pages_router.patch(
    "/{uid}",
    tags=["pages"],
    response_model=CreatePageResponse,
)
def patch_page(
    uid: str,
    patch_body: PatchBody,
    current_user: User = Security(get_current_user),
    if_match: Optional[str] = Header(None),
):
    try:
        archive_response = services.pages.archive_action(current_user, patch_body.archive_action, uid, etag=if_match)
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="object not found",
        )
    except ArchiveConflictError:
        return JSONResponse(
            status_code=409,
            content={"err": "already_archived"},
        )

    except RestoreConflictError:
        return JSONResponse(
            status_code=409,
            content={"err": "not_archived"},
        )

    return archive_response


@pages_router.post("", tags=["pages"], response_model=CreatePageResponse)
def create_page(new_page: NewPage, current_user: User = Security(get_current_user)):
    response = services.pages.create(current_user, new_page)
    return response
