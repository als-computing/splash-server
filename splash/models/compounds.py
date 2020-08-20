from pydantic import BaseModel
from typing import Optional


class NewCompound(BaseModel):
    species: Optional[str]
    produced_water_relevance: Optional[str]
    origin: Optional[str]
    fundamental_relevance: Optional[str]
    researchers: Optional[str]
    molecular_weight: Optional[str]
    aqueous_species: Optional[str]
    water_solubility: Optional[str]
    adsorption: Optional[str]
    analytical: Optional[str]
    chem_reference: Optional[str]
    purchase_options: Optional[str]
    contributors: Optional[str]


class Compound(NewCompound):
    uid: str
