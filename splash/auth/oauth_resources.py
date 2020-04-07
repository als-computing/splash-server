from bson.json_util import dumps
from os import environ
from flask import current_app
from flask import request
from flask_restful import Resource
from google.oauth2 import id_token
from google.auth.transport import requests

CLIENT_ID = environ.get("GOOGLE_CLIENT_ID") + ".apps.googleusercontent.com" #TODO: Temporary solution, we will need to have a local config file
#TODO: Find out how to handle errors for this endpoint

class OAuthResource(Resource):
    def post(self):
        try:
            #TODO: Verify the schema before blindly assigning this to a variable
           
            token = request.get_json()['token']
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
        except ValueError:
            raise 
            pass

                