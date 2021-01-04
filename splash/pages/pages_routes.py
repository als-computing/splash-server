from attr import dataclass


from fastapi import APIRouter,  Security, HTTPException
from typing import List
from pydantic import parse_obj_as, BaseModel

from . import Page, NewPage
from ..users import User
from splash.api.auth import get_current_user
from .pages_service import PagesService

pages_router = APIRouter()


@dataclass
class Services():
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


@pages_router.get("/{uid}", tags=['pages'])
def read_page(
        uid: str,
        current_user: User = Security(get_current_user)):

    page = services.pages.retrieve_one(current_user, uid)
    if page is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return page


@pages_router.get("/page_type/{page_type}", tags=["pages"], response_model=List[Page])
def get_pages_by_type(page_type: str,
                      current_user: User = Security(get_current_user),
                      page: int = 1,
                      page_size: int = 100):
    pages = services.pages.retrieve_by_page_type(current_user, page_type,)
    results = parse_obj_as(List[Page], list(pages))
    return results


@pages_router.put("/{uid}", tags=['pages'], response_model=CreatePageResponse)
def replace_page(
        uid: str,
        page: NewPage,
        current_user: User = Security(get_current_user)):
    uid = services.pages.update(current_user, page, uid)
    return CreatePageResponse(uid=uid)


@pages_router.post("", tags=['pages'], response_model=CreatePageResponse)
def create_page(
        new_page: NewPage,
        current_user: User = Security(get_current_user)):
    uid = services.pages.create(current_user, new_page)
    return CreatePageResponse(uid=uid)
