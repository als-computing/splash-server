from flask import Flask, make_response
from flask_restful import Api
from pymongo import MongoClient
import jsonschema
import logging
import os
import sys
from splash.data.base import ObjectNotFoundError, BadIdError


def create_app(db):
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)

    from splash.categories.experiments.experiments_resources import Experiments, Experiment
    api.add_resource(Experiments, "/api/experiments")
    api.add_resource(Experiment,  "/api/experiments/<uid>")

    from splash.categories.users.users_resources import Users, User
    api.add_resource(Users, "/api/users")
    api.add_resource(User,  "/api/users/<uid>")
    
    app.config.from_object('config')
    app.config.from_pyfile('config.py')
    logger = logging.getLogger('splash-server')
    try:
        logging_level = os.environ.get("LOGLEVEL", logging.DEBUG)
        print (f"Setting log level to {logging_level}")
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
    
    if db:
        app.db = db
    else:
        app.db = MongoClient(app.config['MONGO_URL'],
                             username=app.config['MONGO_APP_USER'],
                             password=app.config['MONGO_APP_PW'],
                             authSource=app.config['SPLASH_DB_NAME'],
                             authMechanism='SCRAM-SHA-256')

    @app.errorhandler(404)
    def resource_not_found(error):
        logger.info("Resource not found: ", exc_info=1)
        return make_response(str({'error': 'resource not found'}), 404)

    @app.errorhandler(jsonschema.exceptions.ValidationError)
    def validation_error(error):
        logger.info(" Validation Error: ", exc_info=1 )
        return make_response(str(error), 400)

    @app.errorhandler(TypeError)
    def type_error(error):
        logger.info(" TypeError ", exc_info=1)
        return make_response(str(error), 400)

    # This actually might never get called because trailing slashes with
    # no parameters won't get routed to the route that would raise a
    # NoIdProvidedError, they would get routed to a route that just
    # has the trailing slash
    @app.errorhandler(NoIdProvidedError)
    def no_id_provided_error(error):
        logger.info("No Id Provided Error: ", exc_info=1)
        return make_response(str({'error': 'no id provided'}), 400)

    @app.errorhandler(ObjectNotFoundError)
    def object_not_found_error(error):
        logger.info(" Object Not Found Error: ", exc_info=1 )
        return make_response(str({'error': 'object not found'}), 404)

    @app.errorhandler(BadIdError)
    def bad_id_error(error):
        logger.info(" Bad ID error: ", exc_info=1)
        return make_response(str(error), 400)

    @app.errorhandler(ValueError)
    def value_error(error):
        logger.info(" ValueError ", exc_info=1)
        return make_response(str(error), 400)

    @app.errorhandler(Exception)
    def general_error(error):
        logger.critical(" Houston we have a problem: ", exc_info=1)
        return make_response(str(error), 500)

    return app


# define custom exceptions
class NoIdProvidedError(Exception):
    pass
