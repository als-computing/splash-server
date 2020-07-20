import logging
import jsonschema
import json
import os
from flask import request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token
)
from flask_restful import Resource

from google.oauth2 import id_token
from google.auth.transport import requests
from splash.categories.users.users_service import (
    UserService,
    MultipleUsersAuthenticatorException,
    UserNotFoundException)
from splash.resource.base import MalformedJsonError

LOG_VALIDATING_TOKEN_MSG = "Validating user with token {}"

logger = logging.getLogger('splash-server')


class OauthVerificationError(ValueError):
    pass


class UserNotFoundError(Exception):  # TODO: make the base class more specific
    pass


class MultipleUsersError(Exception):
    pass


class OAuthResource(Resource):

    def __init__(self, user_service: UserService):
        self.CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") + ".apps.googleusercontent.com" #TODO: Temporary solution, we will need to have a local config file
        AUTH_SCHEMA = open_schema()
        self.validator = jsonschema.Draft7Validator(AUTH_SCHEMA)
        self.user_service = user_service

    def post(self):
        try:
            payload = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise MalformedJsonError(e) from None
        try:
            self.validator.validate(payload)
            token = payload['token']
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), self.CLIENT_ID)

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
                user_dict = self.user_service.get_user_authenticator(idinfo['email'])
                user_dict.pop('_id')
                # when authenticated, return a fresh access token and a refresh token
                # https://blog.tecladocode.com/jwt-authentication-and-token-refreshing-in-rest-apis/
                access_token = create_access_token(identity=user_dict['uid'], fresh=True)
                refresh_token = create_refresh_token(user_dict['uid'])
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user': user_dict
                }, 200
               
            except UserNotFoundException:
                # it's possible that we want to not throw anpi error,
                # so that the client has a chance to le the user register
                raise UserNotFoundError('User not registered') from None

        except ValueError as e:
            # This should catch any ValueErrors that come from the the id_token.verify_oauth2_token
            # However, there are still possible connection errors from that function that may
            # go uncaught
            raise OauthVerificationError(e) from None
        except MultipleUsersAuthenticatorException:
            raise MultipleUsersError from None


def validate_info(token):
    logger.info(LOG_VALIDATING_TOKEN_MSG.format(token))
    if 'email_verified' not in token or not token['email_verified']:
        raise OauthVerificationError('user email not verified')


def open_schema():
    dirname = os.path.dirname(__file__)
    auth_schema_file = open(os.path.join(dirname, "auth_schema.json"))
    AUTH_SCHEMA = json.load(auth_schema_file)
    auth_schema_file.close()
    return AUTH_SCHEMA
