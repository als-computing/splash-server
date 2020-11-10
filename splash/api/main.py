from starlette.config import Config
from fastapi import FastAPI
from .config import ConfigStore
from .routers import users, auth, compounds, runs
from splash.service import ServiceProvider
from splash.api import set_service_provider, get_service_provider


def setup_services():
    # setup_services separated so that service_provider creation
    # is decoupled from app creation, allowing test code to
    # mock the service_provider
    from pymongo import MongoClient
    db_uri = ConfigStore.MONGO_DB_URI
    db = MongoClient(db_uri).splash
    service_provider = ServiceProvider(db)
    return service_provider


if get_service_provider() is None:
    set_service_provider(setup_services())

app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect"
)


@app.get("/api/v1/settings")
async def get_settings():
    return {"google_client_id": ConfigStore.GOOGLE_CLIENT_ID}

app.include_router(
    auth.router,
    prefix="/api/v1/idtokensignin",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},

)

app.include_router(
    users.router,
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    compounds.router,
    prefix="/api/v1/compounds", 
    tags=["compounds"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    runs.router,
    prefix="/api/v1/runs",
    tags=["runs"],
    responses={404: {"description": "Not found"}}
)
