from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from splash.categories.runs.runs_service import RunService

from ..services import get_runs_service

router = APIRouter()


class CatalogModel(BaseModel):
    name: str


class RunModel(BaseModel):
    uid: str
    num_images: int
    sample_name: str


class RunMetadataModel(BaseModel):
    energy: float


@router.get("", tags=["runs"], response_model=List[CatalogModel])
def read_catalogs(runs_service: RunService = Depends(get_runs_service)):
    catalog_names = runs_service.list_catalogs()
    catalogs = [CatalogModel(name=catalog_name) for catalog_name in catalog_names]
    return catalogs


@router.get("/{catalog_name}", tags=['runs'], response_model=List[RunModel])
def read_catalog(
            catalog_name: str = Path(..., title="name of catalog"),
            runs_service: RunService = Depends(get_runs_service)):

    runs = runs_service.get_runs(catalog_name)
    return_runs = []
    for run in runs:
        return_runs.append(RunModel(
                           uid=run.get('uid'),
                           num_images=run.get('num_images'),
                           sample_name=run.get('/entry/sample/name')))
    return return_runs


@router.get("/{catalog_name}/{run_uid}/image", tags=['runs'], response_model=RunModel)
def read_frame(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        frame: Optional[int] = 0,
        runs_service: RunService = Depends(get_runs_service)):

    jpeg_generator = runs_service.get_image(catalog_name=catalog_name, uid=run_uid, frame=frame)
    return StreamingResponse(jpeg_generator, media_type="image/JPEG")


@router.get("/{catalog_name}/{run_uid}/metadata", tags=['runs'], response_model=RunMetadataModel)
def read_frame_metadata(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        frame: Optional[int] = 0,
        runs_service: RunService = Depends(get_runs_service)):

    return_metadata = runs_service.get_metadata(catalog_name=catalog_name, uid=run_uid, frame=frame)
    return RunMetadataModel(energy=return_metadata.get('/entry/instrument/monochromator/energy'))
