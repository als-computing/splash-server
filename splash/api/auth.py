from attr import dataclass
from datetime import datetime, timedelta
import logging
from typing import Optional, List
from fastapi import (
    APIRouter,
    Depends,
    Body,
    HTTPException,
    status,
    Form
)
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from google.oauth2 import id_token
from google.auth.transport import requests
from jose import JWTError, jwt
from pydantic import BaseModel
from .config import ConfigStore


from splash.users.users_service import (
    UsersService,
    MultipleUsersAuthenticatorException,
    UserNotFoundException)
from splash.models.users import UserModel

logger = logging.getLogger('splash_server.auth')

auth_router = APIRouter()

LOG_VALIDATING_TOKEN_MSG = "Validating user with token {}"
ALGORITHM = "HS256"

# Modification of https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/


class TokenRequestModel(BaseModel):
    token: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_uid: str
    scopes: List[str]


class TokenResponseModel(BaseModel):
    access_token: str
    user: UserModel


@dataclass
class Services():
    users: UsersService


services = Services(None)


def set_services(users_service: UsersService):
    services.users = users_service


# oauth2_scheme dependency alllows fastapi to interrogate the Authorization: Beaarer <token>
# header sent from the splash client. It's very close to working with the swagger UI, but not quite...
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=ConfigStore.OAUTH_AUTH_URL,
    tokenUrl=ConfigStore.OAUTH_TOKEN_URL,
    auto_error=True,
    scopes={'email': 'profile'}
)


class OauthVerificationError(ValueError):   
    pass


class UserNotFoundError(Exception):  # TODO: make the base class more specific
    pass


class MultipleUsersError(Exception):
    pass


class RedirctVerifierModel(BaseModel):
    grant_type: str
    code: str
    client_id: str
    redirect_uri: str


# @router.post("/verifier", tags=["tokens"], response_model=TokenResponseModel)
# # https://developers.google.com/identity/protocols/oauth2/openid-connect
# def outh_redirect_verifier(client_id: str = Form(...), code: str = Form(...), grant_type: str = Form(...), redirect_uri: str = Form(...)):
#     response = py_requests.post(url="https://oauth2.googleapis.com/token", data={"client_id": client_id, "client_secret": ConfigStore.GOOGLE_CLIENT_SECRET, "code": code, "grant_type": grant_type, "redirect_uri": redirect_uri})
#     return {"success": "yep"}


@auth_router.post("", tags=["tokens"], response_model=TokenResponseModel)
def id_token_verify(
        g_token_request: TokenRequestModel,
        auth_provider: Optional[str] = None):

    if auth_provider != 'google':
        return None
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(
            g_token_request.token,
            requests.Request(),
            ConfigStore.GOOGLE_CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        validate_info(idinfo)
        try:
            user_dict = services.users.get_user_authenticator(idinfo['email'])
            # when authenticated, return a fresh access token and a refresh token
            # https://blog.tecladocode.com/jwt-authentication-and-token-refreshing-in-rest-apis/
            access_token_expires = timedelta(minutes=ConfigStore.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                {"sub": user_dict['uid'], "scopes": ['splash']},
                expires_delta=access_token_expires)

            response = TokenResponseModel(
                access_token=access_token,
                user=UserModel(**user_dict)
            )
            return response
            # return  {"access_token": access_token, "token_type": "bearer"}   

        except UserNotFoundException:
            # it's possible that we want to not throw anpi error,
            # so that the client has a chance to le the user register
            raise UserNotFoundError('User not registered') from None
        except ValueError as e:
            # This should catch any ValueErrors that come from the the id_token.verify_oauth2_token
            # However, there are still possible connection errors from that function that may
            # go uncaught
            raise OauthVerificationError(e) from None

    except MultipleUsersAuthenticatorException as e:
        # raise MultipleUsersError from None
        raise e


def validate_info(token):
    logger.info(LOG_VALIDATING_TOKEN_MSG.format(token))
    if 'email_verified' not in token or not token['email_verified']:
        raise OauthVerificationError('user email not verified')


def create_access_token(
            data: dict,
            expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, ConfigStore.TOKEN_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
            security_scopes: SecurityScopes,
            token: str = Depends(oauth2_scheme)):

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, ConfigStore.TOKEN_SECRET_KEY, algorithms=[ALGORITHM])
        user_uid: str = payload.get("sub")
        if user_uid is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(user_uid=user_uid, scopes=token_scopes)
    except JWTError as e:
        logger.error("exception loggine in", exc_info=e)
        raise credentials_exception
    user_dict = services.users.insecure_get_user(user_uid)

    if user_dict is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return UserModel(**user_dict)
