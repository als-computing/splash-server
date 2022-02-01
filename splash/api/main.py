import logging
from splash.service.models import SplashMetadataAllowExtra

from fastapi.responses import JSONResponse

from fastapi.encoders import jsonable_encoder

from splash.service.base import EtagMismatchError

from fastapi import FastAPI
from fastapi.requests import Request
from .config import ConfigStore
from splash.api.auth import auth_router, set_services as set_auth_services
from splash.pages.pages_routes import set_pages_service, pages_router
from splash.pages.pages_service import PagesService
from splash.users.users_routes import set_users_service, users_router
from splash.users.users_service import UsersService
from splash.references.references_routes import (
    set_references_service,
    references_router,
)
from splash.references.references_service import ReferencesService
from splash.runs.runs_routes import set_runs_service, runs_router
from splash.runs.runs_service import RunsService, TeamRunChecker
from splash.teams.teams_routes import set_teams_service, teams_router
from splash.teams.teams_service import TeamsService

logger = logging.getLogger("splash")
db = None


def init_logging():

    ch = logging.StreamHandler()
    # ch.setLevel(logging.INFO)
    # root_logger.addHandler(ch)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(ConfigStore.SPLASH_LOG_LEVEL)


app = FastAPI(
    openapi_url="/splash/api/v1/openapi.json",
    docs_url="/splash/api/docs",
    redoc_url="/splash/api/redoc",
    # swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect"
)


@app.on_event("startup")
def setup_services():
    # setup_services separated so that service_provider creation
    # is decoupled from app creation, allowing test code to
    # mock the service_provider
    from pymongo import MongoClient

    init_logging()
    db_uri = ConfigStore.MONGO_DB_URI
    db = MongoClient(db_uri).splash
    users_svc = UsersService(db, "users")
    pages_svc = PagesService(db, "pages", "pages_old")
    references_svc = ReferencesService(db, "references")
    teams_svc = TeamsService(db, "teams")
    runs_svc = RunsService(teams_svc, TeamRunChecker())
    logger.info(f"setting MONGO_DB_URI {db_uri}")
    logger.info(f"setting db {db}")

    set_auth_services(users_svc)
    set_pages_service(pages_svc)
    set_references_service(references_svc)
    set_runs_service(runs_svc)
    set_teams_service(teams_svc)
    set_users_service(users_svc)


@app.exception_handler(EtagMismatchError)
async def handle_wrong_etag(response, exc):
    return JSONResponse(
        status_code=412,
        content={
            "err": "etag_mismatch_error",
            "etag": exc.etag,
            # Parse to make sure that optional fields, such as archive,
            # are inserted as None and not left out
            "splash_md": jsonable_encoder(SplashMetadataAllowExtra.parse_obj(exc.splash_md)),
        },
    )


@app.get("/splash/api/v1/settings")
async def get_settings():
    return {"google_client_id": ConfigStore.GOOGLE_CLIENT_ID}


app.include_router(
    auth_router,
    prefix="/splash/api/v1/idtokensignin",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    users_router,
    prefix="/splash/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    pages_router,
    prefix="/splash/api/v1/pages",
    tags=["pages"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    runs_router,
    prefix="/splash/api/v1/runs",
    tags=["runs"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    teams_router,
    prefix="/splash/api/v1/teams",
    tags=["teams"],
    responses={404: {"description": "Not found"}},
)

app.include_router(
    references_router,
    prefix="/splash/api/v1/references",
    tags=["references"],
    responses={404: {"description": "Not found"}},
)
