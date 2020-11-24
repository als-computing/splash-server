from attr import dataclass

from fastapi import APIRouter,  Security, Query
from typing import List, Optional

from pydantic.tools import parse_obj_as
from . import Reference, NewReference, CreateReferenceResponse
from ..users import User
from splash.api.auth import get_current_user
from .references_service import ReferencesService

references_router = APIRouter()


@dataclass
class Services():
    references: ReferencesService


services = Services(None)


def set_references_service(references_svc: ReferencesService):
    services.references = references_svc


@references_router.get("", tags=["references"], response_model=List[Reference])
def read_references(
        current_user: User = Security(get_current_user),
        page: int = 1,
        page_size: int = 100,
        search: Optional[str] = Query(None, max_length=50)):

    if search is not None:
        print(search)
        query = {
            '$or': [
                {'reference': {'$regex': search, '$options': 'i'}},
                {'doi_url': {'$regex': search, '$options': 'i'}}
            ]
        }
        references = services.references.retrieve_multiple(current_user, page=page, page_size=page_size, query=query)
    else:
        references = services.references.retrieve_multiple(current_user, page=page, page_size=page_size)
    results = parse_obj_as(List[Reference], list(references))
    return results


@references_router.get("/{uid}", tags=['references'])
def read_reference(
        uid: str,
        current_user: User = Security(get_current_user)):

    reference_dict = services.references.retrieve_one(current_user, uid)
    return reference_dict

# @router.put("/{uid}", tags=['compounds'], response_model=CreateCompoundResponse)
# def replace_compound(
#        uid: str,
#        compound: NewCompound,
#        current_user: UserModel = Security(get_current_user)):
#    uid = services().compounds.update(current_user, compound.dict(), uid)
#    return CreateCompoundResponse(uid=uid)


@references_router.post("", tags=['references'], response_model=CreateReferenceResponse)
def create_reference(
        new_reference: NewReference,
        current_user: User = Security(get_current_user)):
    uid = services.references.create(current_user, new_reference.dict())
    return CreateReferenceResponse(uid=uid)
