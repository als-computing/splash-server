from attr import dataclass


from fastapi import APIRouter,  Security, HTTPException
from typing import List
from pydantic import parse_obj_as, BaseModel

from . import Compound, NewCompound
from ..users import User
from splash.api.auth import get_current_user
from .compounds_service import CompoundsService

compounds_router = APIRouter()


@dataclass
class Services():
    compounds: CompoundsService


services = Services(None)


def set_compounds_service(compounds_svc: CompoundsService):
    services.compounds = compounds_svc


class CreateCompoundResponse(BaseModel):
    uid: str


@compounds_router.get("", tags=["compounds"], response_model=List[Compound])
def read_compounds(current_user: User = Security(get_current_user)):
    compounds = services.compounds.retrieve_multiple(current_user, 1)
    results = parse_obj_as(List[Compound], list(compounds))
    return results


@compounds_router.get("/{uid}", tags=['compounds'])
def read_compound(
        uid: str,
        current_user: User = Security(get_current_user)):

    compound = services.compounds.retrieve_one(current_user, uid)
    if compound is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return compound


@compounds_router.put("/{uid}", tags=['compounds'], response_model=CreateCompoundResponse)
def replace_compound(
        uid: str,
        compound: NewCompound,
        current_user: User = Security(get_current_user)):
    uid = services.compounds.update(current_user, compound, uid)
    return CreateCompoundResponse(uid=uid)


@compounds_router.post("", tags=['compounds'], response_model=CreateCompoundResponse)
def create_compound(
        new_compound: NewCompound,
        current_user: User = Security(get_current_user)):
    uid = services.compounds.create(current_user, new_compound)
    return CreateCompoundResponse(uid=uid)
