from flask import Flask, make_response
from flask_restful import Api
from pymongo import MongoClient
import jsonschema
import logging
import os
import sys
from splash.data.base import ObjectNotFoundError, BadIdError
from splash.auth.oauth_resources import OauthVerificationError


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)


    
    app.config.from_object('config')
    # app.config.from_pyfile('config.py')
    logger = logging.getLogger('splash-server')
    try:
        logging_level = os.environ.get("LOGLEVEL", logging.DEBUG)
        print (f"Settinconfig.pg log level to {logging_level}")
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

    from splash.categories.experiments.experiments_resources import Experiments, Experiment
    api.add_resource(Experiments, "/api/experiments")
    api.add_resource(Experiment,  "/api/experiments/<uid>")

    from splash.categories.users.users_resources import Users, User
    api.add_resource(Users, "/api/users")
    api.add_resource(User,  "/api/users/<uid>")

    from splash.auth.oauth_resources import OAuthResource
    api.add_resource(OAuthResource, "/api/tokensignin")

    # connect-false because frameworks like uwsgi fork after app is obtained, and are not
    # fork-safe.
    app.db = MongoClient(app.config['MONGO_URL'], connect=False)[app.config['MONGO_DB_NAME']]

    @app.errorhandler(404)
    def resource_not_found(error):
        logger.info("Resource not found: ", exc_info=1)
        return make_response(str({'error': 'resource_not_found', 'message':'resource not found'}), 404)

    @app.errorhandler(jsonschema.exceptions.ValidationError)
    def validation_error(error):
        logger.info(" Validation Error: ", exc_info=1 )
        return make_response(str({"error": "validation_error", 'message':str(error)}), 400)

    @app.errorhandler(TypeError)
    def type_error(error):
        logger.info(" TypeError ", exc_info=1)
        return make_response(str({"error":"type_error", "message": str(error)}), 400)

    # This actually might never get called because trailing slashes with
    # no parameters won't get routed to the route that would raise a
    # NoIdProvidedError, they would get routed to a route that just
    # has the trailing slash
    @app.errorhandler(NoIdProvidedError)
    def no_id_provided_error(error):
        logger.info("No Id Provided Error: ", exc_info=1)
        return make_response(str({'error':'no_id_provided','message': 'no id provided'}), 400)

    @app.errorhandler(ObjectNotFoundError)
    def object_not_found_error(error):
        logger.info(" Object Not Found Error: ", exc_info=1 )
        return make_response(str({'error': 'object_not_found', 'message':'object not found'}), 404)

    @app.errorhandler(BadIdError)
    def bad_id_error(error):
        logger.info(" Bad ID error: ", exc_info=1)
        return make_response(str({"error": "bad_id_error", "message": "bad id error"}), 400)

    @app.errorhandler(ValueError)
    def value_error(error):
        logger.info(" ValueError ", exc_info=1)
        return make_response(str({"error": "value_error", 'message': str(error)}), 400)
    
    @app.errorhandler(OauthVerificationError)
    def value_error(error):
        logger.info(" OauthVerificationError ", exc_info=1)
        return make_response(str({"error":"oauth_verification_error", 'message': "oauth verification error"}), 500)

    @app.errorhandler(Exception)
    def general_error(error):
        logger.critical(" Houston we have a problem: ", exc_info=1)
        return make_response(str({"error":"server_error", 'message': "oops, something went wrong on our end"}, 500))
    return app


# define custom exceptions
class NoIdProvidedError(Exception):
    pass
