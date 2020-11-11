from fastapi import FastAPI

from .config import ConfigStore
from splash.api.auth import auth_router, set_services as set_auth_services
from splash.compounds.compounds_routes import set_compounds_service, compounds_router
from splash.compounds.compounds_service import CompoundsService
from splash.users.users_routes import set_users_service, users_router
from splash.users.users_service import UsersService
from splash.runs.runs_routes import set_runs_service, runs_router
from splash.runs.runs_service import RunsService
from splash.runs.runs_service import RunsService


app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    # swagger_ui_oauth2_redirect_url="/api/docs/oauth2-redirect"
)


@app.on_event("startup")
def setup_services():
    # setup_services separated so that service_provider creation
    # is decoupled from app creation, allowing test code to
    # mock the service_provider
    from pymongo import MongoClient
    db_uri = ConfigStore.MONGO_DB_URI
    db = MongoClient(db_uri).splash
    users_svc = UsersService(db, 'users')
    compounds_svc = CompoundsService(db, 'compounds')
    runs_svc = RunsService()
    set_users_service(users_svc)
    set_compounds_service(compounds_svc)
    set_runs_service(runs_svc)
    set_auth_services(users_svc)

@app.get("/api/v1/settings")
async def get_settings():
    return {"google_client_id": ConfigStore.GOOGLE_CLIENT_ID}

app.include_router(
    auth_router,
    prefix="/api/v1/idtokensignin",
    tags=["tokens"],
    responses={404: {"description": "Not found"}},

)

app.include_router(
    users_router,
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    compounds_router,
    prefix="/api/v1/compounds", 
    tags=["compounds"],
    responses={404: {"description": "Not found"}}
)

app.include_router(
    runs_router,
    prefix="/api/v1/runs",
    tags=["runs"],
    responses={404: {"description": "Not found"}}
)
