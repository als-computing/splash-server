from attr import dataclass

from splash.compounds.compounds_service import CompoundsService
from attr import dataclass
from fastapi import APIRouter,  Security
from typing import List
from pydantic import parse_obj_as, BaseModel

from splash.models.compounds import Compound, NewCompound
from splash.models.users import UserModel
from splash.api.auth import get_current_user

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
def read_compounds(current_user: UserModel = Security(get_current_user)):
    compounds = services.compounds.retrieve_multiple(current_user, 1)
    results = parse_obj_as(List[Compound], list(compounds))
    return results


@compounds_router.get("/{uid}", tags=['compounds'])
def read_compound(
        uid: str,
        current_user: UserModel = Security(get_current_user)):

    compound_dict = services.compounds.retrieve_one(current_user, uid)
    return (Compound(**compound_dict))

@compounds_router.put("/{uid}", tags=['compounds'], response_model=CreateCompoundResponse)
def replace_compound(
        uid: str,
        compound: NewCompound,
        current_user: UserModel = Security(get_current_user)):
    uid = services.compounds.update(current_user, compound.dict(), uid)
    return CreateCompoundResponse(uid=uid)


@compounds_router.post("", tags=['compounds'], response_model=CreateCompoundResponse)
def create_compound(
        new_compound: NewCompound,
        current_user: UserModel = Security(get_current_user)):
    uid = services.compounds.create(current_user, new_compound.dict())
    return CreateCompoundResponse(uid=uid)
