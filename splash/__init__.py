from flask import Flask, make_response, current_app, jsonify
from flask_restful import Api
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token
)
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pymongo import MongoClient
import jsonschema
from json import dumps
import logging
import os
import sys
from werkzeug.exceptions import BadRequest

from splash.data.base import ObjectNotFoundError, BadIdError
from splash.auth.oauth_resources import OauthVerificationError
from splash.categories.users.users_service import UserService
from splash.data.base import MongoCollectionDao
import splash.login

class ErrorPropagatingApi(Api):
    """Flask-Restful has its own error handling facilities, this propagates errors to flask"""

    def error_router(self, original_handler, e):
        return original_handler(e)

def create_app(db=None):
    app = Flask(__name__, instance_relative_config=True)
    api = ErrorPropagatingApi(app)
    jwt = JWTManager(app)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY')
    app.config.from_object('config')
    logger = logging.getLogger('splash-server')
    try:
        logging_level = os.environ.get("LOGLEVEL", logging.DEBUG)
        print(f"Settinconfig.pg log level to {logging_level}")
        logger.setLevel(logging_level)

        # create console handler and set level to debug
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging_level)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)
    except Exception as e:
        print("cannot setup logging: {}".format(str(e)))

    
    # connect-false because frameworks like uwsgi fork after app is obtained, and are not
    # fork-safe.
    if db is None:
        app.db = MongoClient(app.config['MONGO_URL'], connect=False)[app.config['MONGO_DB_NAME']]
    else:
        app.db = db

    userDAO = MongoCollectionDao(app.db, 'users') # this whole service/dao connection will change soon
    app.user_service = UserService(userDAO)

    from splash.categories.experiments.experiments_resources import Experiments, Experiment
    api.add_resource(Experiments, "/api/experiments")
    api.add_resource(Experiment,  "/api/experiments/<uid>")

    from splash.categories.compounds.compounds_resources import Compound, Compounds
    api.add_resource(Compounds, "/api/compounds")
    api.add_resource(Compound,  "/api/compounds/<uid>")

    from splash.categories.users.users_resources import Users, User
    api.add_resource(Users, "/api/users")
    api.add_resource(User,  "/api/users/<uid>")

    from splash.auth.oauth_resources import OAuthResource
    api.add_resource(OAuthResource, "/api/tokensignin", resource_class_kwargs={'user_service': app.user_service})

    @app.errorhandler(404)
    def resource_not_found(error):
        logger.info("Resource not found: ", exc_info=1)
        return make_response(dumps({"error": "resource_not_found", "message":"resource not found"}), 404)

    @app.errorhandler(jsonschema.exceptions.ValidationError)
    def validation_error(error):
        logger.info(" Validation Error: ", exc_info=1 )
        return make_response(dumps({"error": "validation_error", "message":str(error)}), 400)

    @app.errorhandler(TypeError)
    def type_error(error):
        logger.info(" TypeError ", exc_info=1)
        return make_response(dumps({"error":"type_error", "message": "Type Error"}), 400)

    # This actually might never get called because trailing slashes with
    # no parameters won't get routed to the route that would raise a
    # NoIdProvidedError, they would get routed to a route that just
    # has the trailing slash
    @app.errorhandler(NoIdProvidedError)
    def no_id_provided_error(error):
        logger.info("No Id Provided Error: ", exc_info=1)
        return make_response(dumps({"error":"no_id_provided","message": "no id provided"}), 400)

    @app.errorhandler(ObjectNotFoundError)
    def object_not_found_error(error):
        logger.info(" Object Not Found Error: ", exc_info=1 )
        return make_response(dumps({"error": "object_not_found", "message":"object not found"}), 404)

    @app.errorhandler(BadIdError)
    def bad_id_error(error):
        logger.info(" Bad ID error: ", exc_info=1)
        return make_response(dumps({"error": "bad_id_error", "message": "bad id error"}), 400)

    @app.errorhandler(ValueError)
    def value_error(error):
        logger.info(" ValueError ", exc_info=1)
        return make_response(dumps({"error": "value_error", "message": "Value Error"}), 400)

    @app.errorhandler(OauthVerificationError)
    def oauth_error(error):
        logger.info(" OauthVerificationError ", exc_info=1)
        return make_response(dumps({"error": "oauth_verification_error", "message": "oauth verification error"}), 500)

    @app.errorhandler(BadRequest)
    def badd_request(error):
        logger.info(" ValueError ", exc_info=1)
        return make_response(dumps({"error": "value_error", "message": "Value Error"}), error.code)

    @app.errorhandler(Exception)
    def general_error(error):
        logger.critical(" Houston we have a problem: ", exc_info=1)
        return make_response(dumps({"error": "server_error", "message": "oops, something went wrong on our end"}), 500)
    return app


# define custom exceptions
class NoIdProvidedError(Exception):
    pass

