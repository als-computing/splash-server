import logging
import os
import sys
import json
from json import dumps

import jsonschema
from flask import Flask, current_app, jsonify, make_response, Response
from flask_jwt_extended import (JWTManager, create_access_token,
                                create_refresh_token)
from flask_restful import Api
from jwt.exceptions import ExpiredSignatureError, PyJWTError
from pymongo import MongoClient
from werkzeug.exceptions import BadRequest

from splash.data.base import ObjectNotFoundError, UidInDictError, MongoCollectionDao, BadIdError
from splash.auth.oauth_resources import OauthVerificationError, UserNotFoundError, MultipleUsersError
from splash.service.base import BadPageArgument
from splash.resource.base import MalformedJsonError
from splash.categories.users.users_service import UserService
from splash.categories.runs.runs_service import RunDoesNotExist,\
     CatalogDoesNotExist, BadFrameArgument, FrameDoesNotExist, RunService
from splash.categories.compounds.compounds_service import CompoundsService
from splash.categories.experiments.experiments_service import ExperimentService
from splash.categories.experiments.experiments_resources import Experiment, Experiments
from splash.categories.compounds.compounds_resources import Compound, Compounds
from splash.categories.users.users_resources import User, Users
from splash.helpers.middleware import setup_metrics

class ErrorPropagatingApi(Api):
    """Flask-Restful has its own error handling facilities, this propagates errors to flask"""

    def error_router(self, original_handler, e):
        return original_handler(e)


def create_app(db=None):
    CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
    app = Flask(__name__, instance_relative_config=True)
    api = ErrorPropagatingApi(app)
    jwt = JWTManager(app)
    app.secret_key = os.environ.get('FLASK_SECRET_KEY')
    setup_metrics(app)

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
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - \
                                        %(message)s')

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
    app.run_service = RunService()

    experimentsDAO = MongoCollectionDao(app.db, 'experiments')
    app.experiments_service = ExperimentService(experimentsDAO)

    compoundsDAO = MongoCollectionDao(app.db, 'compounds')
    app.compounds_service = CompoundsService(compoundsDAO)

    api.add_resource(Compounds, "/api/compounds", resource_class_kwargs={"service": app.compounds_service})
    api.add_resource(Compound,  "/api/compounds/<uid>", resource_class_kwargs={"service": app.compounds_service})

    api.add_resource(Experiments, "/api/experiments", resource_class_kwargs={"service": app.experiments_service})
    api.add_resource(Experiment,  "/api/experiments/<uid>", resource_class_kwargs={"service": app.experiments_service})

    api.add_resource(Users, "/api/users", resource_class_kwargs={"service": app.user_service})
    api.add_resource(User,  "/api/users/<uid>", resource_class_kwargs={"service": app.user_service})

    from splash.auth.oauth_resources import OAuthResource
    api.add_resource(OAuthResource, "/api/tokensignin", resource_class_kwargs={'user_service': app.user_service})

    from splash.categories.runs.runs_resource import Run, Runs, Catalogs
    api.add_resource(Catalogs, '/api/runs', resource_class_kwargs={"run_service": app.run_service})
    api.add_resource(Runs, '/api/runs/<catalog>', resource_class_kwargs={"run_service": app.run_service})
    api.add_resource(Run, "/api/runs/<catalog>/<uid>", resource_class_kwargs={"run_service": app.run_service})

    @app.errorhandler(FrameDoesNotExist)
    def frame_does_not_exist(error):
        logger.info("Bad frame argument: ", exc_info=1)
        return make_response(dumps({"error": "frame_does_not_exist", "message": str(error)}), 404)

    @app.errorhandler(BadFrameArgument)
    def bad_frame_argument(error):
        logger.info("Bad frame argument: ", exc_info=1)
        return make_response(dumps({"error": "bad_frame_argument", "message": str(error)}), 400)

    @app.errorhandler(RunDoesNotExist)
    def run_not_found(error):
        logger.info("Run not found: ", exc_info=1)
        return make_response(dumps({"error": "run_not_found", "message": str(error)}), 404)

    @app.errorhandler(CatalogDoesNotExist)
    def catalog_not_found(error):
        logger.info("Catalog not found: ", exc_info=1)
        return make_response(dumps({"error": "catalog_not_found", "message": str(error)}), 404)
    @app.errorhandler(UidInDictError)
    def uid_error(error):
        logger.info(" UidError: ")
        return make_response(dumps({"error": "uid_field_not_allowed", "message": "uid field not allowed"}), 400)

    @app.errorhandler(MalformedJsonError)
    def malformed_json(error: MalformedJsonError):
        logger.info("Malformed JSON: ", exc_info=1)
        return make_response(dumps({"error": "malformed_json", "message": error.msg, "position": error.pos, }), 400)

    @app.errorhandler(BadPageArgument)
    def bad_page_arg(error):
        logger.info("Bad Page argument: ", exc_info=1)
        return make_response(dumps({"error": "bad_page_argument", "message": str(error)}), 400)
    @app.errorhandler(UserNotFoundError)
    def user_not_found(error):
        logger.info(" User Not Found: ", exc_info=1)
        return make_response(dumps({"error": "user_not_found", "message": "user not found"}), 401)

    @app.errorhandler(MultipleUsersError)
    def multiple_users(error):
        logger.info(" Multiple Users: ", exc_info=1)
        return make_response(dumps({"error": "multiple_users", "message": "Multiple Users"}), 403)

    @app.errorhandler(404)
    def resource_not_found(error):
        logger.info("Resource not found: ", exc_info=1)
        return make_response(dumps({"error": "resource_not_found", "message": "resource not found"}), 404)

    @app.errorhandler(jsonschema.exceptions.ValidationError)
    def validation_error(error):
        logger.info(" Validation Error: ", exc_info=1 )
        return make_response(dumps({"error": "validation_error", "message": str(error)}), 400)

    @app.errorhandler(TypeError)
    def type_error(error):
        logger.info(" TypeError ", exc_info=1)
        return make_response(dumps({"error": "type_error",
                             "message": "Type Error"}), 400)

    # This actually might never get called because trailing slashes with
    # no parameters won't get routed to the route that would raise a
    # NoIdProvidedError, they would get routed to a route that just
    # has the trailing slash
    @app.errorhandler(NoIdProvidedError)
    def no_id_provided_error(error):
        logger.info("No Id Provided Error: ", exc_info=1)
        return make_response(dumps({"error": "no_id_provided",
                             "message": "no id provided"}), 400)

    @app.errorhandler(ObjectNotFoundError)
    def object_not_found_error(error):
        logger.info(" Object Not Found Error: ", exc_info=1)
        return make_response(dumps({"error": "object_not_found",
                             "message": "object not found"}), 404)

    @app.errorhandler(BadIdError)
    def bad_id_error(error):
        logger.info(" Bad ID error: ", exc_info=1)
        return make_response(dumps({"error": "bad_id_error", "message": str(error)}), 400)

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
