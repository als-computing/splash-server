from fastapi import APIRouter, Depends, Body
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
from google.oauth2 import id_token
from google.auth.transport import requests
import logging
from typing import List, Optional
from pydantic import BaseModel, BaseConfig
from pymongo import MongoClient

from splash.auth.oauth_resources import OAuthResource, OauthVerificationError
from splash.categories.users.users_service import (
    UserService,
    MultipleUsersAuthenticatorException,
    UserNotFoundException)

from ..services import get_users_service

logger = logging.getLogger('splash-server')
from ..services import get_users_service
router = APIRouter()

LOG_VALIDATING_TOKEN_MSG = "Validating user with token {}"
# CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") + ".apps.googleusercontent.com" #TODO: Temporary solution, we will need to have a local config file

CLIENT_ID = "160817052361-5qh5p7e57jq2t537c36umh64qnlsvo2k.apps.googleusercontent.com" #TODO: Temporary solution, we will need to have a local config file

class OauthVerificationError(ValueError):
    pass


class UserNotFoundError(Exception):  # TODO: make the base class more specific
    pass


class MultipleUsersError(Exception):
    pass


class TokenRequest(BaseModel):
    token: str


class AuthenticatorModel(BaseModel):
    issuer: str
    email: str


class UserModel(BaseModel):
    email: Optional[str] = None
    giten_name: Optional[str] = None
    family_name: Optional[str] = None
    authenticators: Optional[List[AuthenticatorModel]]
    disabled: Optional[bool] = None


class TokenResponseModel(BaseModel):
    access_token: str
    user: UserModel

@router.post("", response_model=TokenResponseModel)
async def GOAuthVerify(g_token_request: TokenRequest, user_service: UserService = Depends(get_users_service)):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(g_token_request.token, requests.Request(), CLIENT_ID)

        # Or, if multiple clients access the backend server:
        # idinfo = id_token.verify_oauth2_token(token, requests.Request())
        # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
        #     raise ValueError('Could not verify audience.')

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # If auth request is from a G Suite domain:
        # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
        #     raise ValueError('Wrong hosted domain.')

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        # user = User("foo", idinfo['email'], idinfo['given_name'], idinfo['family_name'], True) 

        validate_info(idinfo)
        try:
            user_dict = user_service.get_user_authenticator(idinfo['email'])
            user_dict.pop('_id')
            # when authenticated, return a fresh access token and a refresh token
            # https://blog.tecladocode.com/jwt-authentication-and-token-refreshing-in-rest-apis/
            access_token = "foo_bar"
            response = TokenResponseModel(
                access_token=access_token,
                user=UserModel(**user_dict)
            )
            return response
            
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