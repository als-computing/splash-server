from bson.json_util import dumps
import jsonschema
import json
import os
from flask import current_app
from flask import request
from flask_restful import Resource
from google.oauth2 import id_token
from google.auth.transport import requests

dirname = os.path.dirname(__file__)
auth_schema_file = open(os.path.join(dirname, "auth_schema.json"))
AUTH_SCHEMA = json.load(auth_schema_file)
auth_schema_file.close()


CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID") + ".apps.googleusercontent.com" #TODO: Temporary solution, we will need to have a local config file
#TODO: Create error handling for if the user is not found in the mongo database
#TODO: integrate this with mongo 
class OauthVerificationError(ValueError):
    pass

class UserNotFoundError(Exception): #TODO: make the base class more specific
    pass

class OAuthResource(Resource):
        def post(self):
            try: 
                validator = jsonschema.Draft7Validator(AUTH_SCHEMA)
                json = request.get_json(force=True)
                validator.validate(json)
                token = json['token']
                # Specify the CLIENT_ID of the app that accesses the backend:
                idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)

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
                userid = idinfo['sub']
                return dumps({'message':'LOGIN SUCCESS', 'token': 'SERVER TOKEN GOES HERE'}) #TODO: return an actual token
            except ValueError as e: #This should catch any ValueErrors that come from the the id_token.verify_oauth2_token
                #However, there are still possible connection errors from that function that may 
                #go uncaught
                raise OauthVerificationError(e) from None


                