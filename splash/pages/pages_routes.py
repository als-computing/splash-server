from attr import dataclass


from fastapi import APIRouter, Security, HTTPException
from typing import List, Optional
from fastapi.param_functions import Query
from pydantic import parse_obj_as, BaseModel

from . import Page, NewPage
from ..users import User
from splash.api.auth import get_current_user
from .pages_service import PagesService
from ..service.base import ObjectNotFoundError, VersionNotFoundError

pages_router = APIRouter()


@dataclass
class Services:
    pages: PagesService


services = Services(None)


def set_pages_service(pages_svc: PagesService):
    services.pages = pages_svc


class CreatePageResponse(BaseModel):
    uid: str


@pages_router.get("", tags=["pages"], response_model=List[Page])
def read_pages(current_user: User = Security(get_current_user)):
    pages = services.pages.retrieve_multiple(current_user, 1)
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.get("/{uid}", tags=["pages"])
def read_page(
    uid: str, version: Optional[int] = Query(None, gt=0), current_user: User = Security(get_current_user)
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


@pages_router.get("/page_type/{page_type}", tags=["pages"], response_model=List[Page])
def get_pages_by_type(
    page_type: str,
    current_user: User = Security(get_current_user),
    page: int = 1,
    page_size: int = 100,
):
    pages = services.pages.retrieve_by_page_type(
        current_user,
        page_type,
    )
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.put("/{uid}", tags=["pages"], response_model=CreatePageResponse)
def replace_page(
    uid: str, page: NewPage, current_user: User = Security(get_current_user)
):
    try:
        uid = services.pages.update(current_user, page, uid)
    except ObjectNotFoundError:
        raise HTTPException(
                status_code=404,
                detail="object not found",
            )
    return CreatePageResponse(uid=uid)


@pages_router.post("", tags=["pages"], response_model=CreatePageResponse)
def create_page(new_page: NewPage, current_user: User = Security(get_current_user)):
    uid = services.pages.create(current_user, new_page)
    return CreatePageResponse(uid=uid)
