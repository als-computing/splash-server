import json
from attr import dataclass

from fastapi import APIRouter,  Security, Query
from typing import List, Optional
from fastapi.exceptions import HTTPException

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


@references_router.get("/uid/{uid}", tags=['references'])
def read_reference_by_uid(
        uid: str,
        current_user: User = Security(get_current_user)):

    reference_dict = services.references.retrieve_one(current_user, uid)
    if reference_dict is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return reference_dict


@references_router.get("/doi/{doi_prefix}/{doi_postfix}", tags=['references'])
def read_reference_by_doi(
        doi_prefix: str,
        doi_postfix: str,
        current_user: User = Security(get_current_user)):
    print('HI IM HERE')
    reference_dict = services.references.retrieve_one(current_user, doi=doi_prefix + '/' + doi_postfix)
    if reference_dict is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return reference_dict


@references_router.put("/doi/{doi_prefix}/{doi_postfix}", tags=['compounds'], response_model=CreateReferenceResponse)
def replace_compound_by_doi(
        doi_prefix: str,
        doi_postfix: str,
        reference: NewReference,
        current_user: User = Security(get_current_user)):
    # It is necessary to convert to json first, then create a dict,
    #  because if we convert straight to dict
    # There are enum types in the dict that won't serialize when we try to save to Mongo
    # https://github.com/samuelcolvin/pydantic/issues/133
    uid = services().references.update(current_user, json.loads(reference.json()), doi=doi_prefix+'/'+doi_postfix)
    if uid is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return CreateReferenceResponse(uid=uid)


@references_router.put("/uid/{uid}", tags=['compounds'], response_model=CreateReferenceResponse)
def replace_compound_by_uid(
        uid: str,
        reference: NewReference,
        current_user: User = Security(get_current_user)):
    # It is necessary to convert to json first, then create a dict,
    #  because if we convert straight to dict
    # There are enum types in the dict that won't serialize when we try to save to Mongo
    # https://github.com/samuelcolvin/pydantic/issues/133
    uid = services().references.update(current_user, json.loads(reference.json()), uid=uid)
    if uid is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return CreateReferenceResponse(uid=uid)


@references_router.post("", tags=['references'], response_model=CreateReferenceResponse)
def create_reference(
        new_reference: NewReference,
        current_user: User = Security(get_current_user)):
    # It is necessary to convert to json first, then create a dict,
    #  because if we convert straight to dict
    # There are enum types in the dict that won't serialize when we try to save to Mongo
    # https://github.com/samuelcolvin/pydantic/issues/133
    uid = services.references.create(current_user, json.loads(new_reference.json()))
    return CreateReferenceResponse(uid=uid)
