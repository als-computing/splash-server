import pytest
import json
from flask import current_app
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from splash.data.base import MongoCollectionDao
from splash.categories.users.users_service import UserService
from splash.login import User
from .testing_utils import generic_test_flask_crud
import splash.login


def execute(splash_client, method, url, expected_response_code: int):
    client_method = getattr(splash_client, method.lower())
    response = client_method(url,
                        data=json.dumps(dict({}),),
                        content_type='application/json')
    assert response.status_code == expected_response_code


@pytest.mark.usefixtures("splash_client")
def test_unauthenticated(splash_client):

    execute(splash_client, 'get', '/api/experiments', 401)
    execute(splash_client, 'post', '/api/experiments', 401)
    # execute('put', '/api/experiments')
    # execute('patch', '/api/experiments')
    # execute('delete', '/api/experiments')
    execute(splash_client, 'get', '/api/compounds', 401)
    execute(splash_client, 'post', '/api/compounds', 401)
    execute(splash_client, 'get', '/api/users', 401)
    execute(splash_client, 'post', '/api/users', 401)

#TODO: get a flask-login user into the request context and test a request
# @pytest.mark.usefixtures("splash_client", "mongodb")
# def test_authenticated(splash_client, mongodb):
#     # login_manager = LoginManager()
#     # login_manager.init_app(current_app)
#     user_dict = {
#         "uid": "you_id",
#         "given_name": "Eros",
#         "family_name": "Poli",
#         "authenticators": [
#             {
#                 "issuer": "https://accounts.google.com",
#                 "subject": "subject_123456",
#                 "email": "epoli@ventoux.org"
#             },
#             {
#                 "issuer": "accounts.google.com",
#                 "subject": "subject_123456",
#                 "email": "epoli@ventoux.org"
#             }
#         ]
#     }
    
#     user = splash.login.User(
#                     user_dict['uid'], 
#                     user_dict['authenticators'][0]['email'], 
#                     user_dict['given_name'],
#                     user_dict['family_name'],
#                     True)
    
#     userDAO = MongoCollectionDao(mongodb, 'users')
#     user_service = UserService(userDAO)
#     user_uid = user_service.create(user_dict)
#     with splash_client.application.app_context() as response:
#         with splash_client.application.test_request_context('/api/experiments'):
#             login_user(user)
#             resposne =  splash_client.get()
        
