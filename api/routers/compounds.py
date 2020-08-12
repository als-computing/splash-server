from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from typing import List
from pydantic import parse_obj_as
from splash.models.compounds import Compound, NewCompound
from splash.categories.compounds.compounds_service import CompoundsService
from ..services import get_compounds_service

router = APIRouter()


@router.get("", tags=["compounds"], response_model=List[Compound])
def read_compounds(compounds_service: CompoundsService = Depends(get_compounds_service)):
    compounds = compounds_service.retrieve_multiple(1)
    results = parse_obj_as(List[Compound], compounds)
    return results


@router.get("/{uid}", tags=['compounds'])
def read_compound(uid: str, compounds_service: CompoundsService = Depends(get_compounds_service)):
    compound_dict = compounds_service.retrieve_one(uid)
    return (Compound(**compound_dict))


@router.post("", tags=['compounds'])
def create_compound(user: NewCompound, compounds_service: CompoundsService = Depends(get_compounds_service)):
    uid = compounds_service.create(dict(user))
    return uid
