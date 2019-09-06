from flask import Flask, jsonify
from flask import request, Response, make_response
from pymongo import MongoClient
from bson.json_util import dumps
# from flask_cors import CORS, cross_origin
from flask import g, abort
import json
import os
from splash.config import Config
from splash.data import MongoCollectionDao, ObjectNotFoundError, BadIdError
from splash.util import context_timer
import logging, sys
import pathlib
import jsonschema 

dirname = os.path.dirname(__file__)

API_URL_ROOT = "/api"
COMPOUNDS_URL_ROOT = API_URL_ROOT + "/compounds"
EXPERIMENTS_URL_ROOT = API_URL_ROOT + "/experiments"
RUNS_URL_ROOT = API_URL_ROOT + "/runs"

experiments_schema_file = open(os.path.join(dirname, "schema", "experiment_schema.json"))
EXPERIMENTS_SCHEMA = json.load(experiments_schema_file)
experiments_schema_file.close()

logger = logging.getLogger('splash-server')

app = Flask(__name__)



#define custom exceptions
class NoIdProvidedError(Exception):
    pass


def setup_logging():
    try:
        # flask_cors_logger = logging.getLogger('flask_cors')
        # flask_cors_logger.setLevel(logging.DEBUG)
        
        logging_level = os.environ.get("LOGLEVEL")
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

        logger.debug('testing debug')
        logger.info('testing info')
    except Exception as e:
        print("cannot setup logging: {}".format(str(e)))

setup_logging()

SPLASH_SERVER_DIR = os.environ.get("SPLASH_SERVER_DIR")
logger.info(f'Reading log file {SPLASH_SERVER_DIR}')
if SPLASH_SERVER_DIR == None:
    SPLASH_SERVER_DIR = str(pathlib.Path.home() / ".splash")


SPLASH_CONFIG_FILE = SPLASH_SERVER_DIR + "/config.cfg" if SPLASH_SERVER_DIR is not None else "/config.cfg"
config = Config(SPLASH_CONFIG_FILE)
CFG_APP_DB = 'AppDB'
CFG_WEB = 'Web'
MONGO_URL = config.get(CFG_APP_DB, 'mongo_url', fallback='localhost:27017')
WEB_SERVER_HOST = config.get(CFG_WEB, 'server_host', fallback='0.0.0.0')
WEB_SERVER_HOST = config.get(CFG_WEB, 'server_port', fallback='80')
WEB_IMAGE_FOLDER_ROOT = config.get(CFG_WEB, 'image_root_folder', fallback='images')


def get_compound_dao():
    db = MongoClient(MONGO_URL)  # , ssl=True, ssl_ca_certs=certifi.where(), connect=False)
    return MongoCollectionDao(db.efrc.compounds)

def get_experiment_dao():
    db = MongoClient(MONGO_URL)
    return MongoCollectionDao(db.efrc.experiments)

# @app.teardown_appcontext
# def teardown_db(exception):
#     db = g.pop('db')
#     if db is not None:
#         db.close()

@app.route(COMPOUNDS_URL_ROOT, methods=['GET'])
def retrieve_compounds():
    data_svc = get_compound_dao()

    logger.info("-----In retrieve_copounds")
    compounds = data_svc.retrieve_many()
    logger.info("-----In retrieve_copounds find")
    json = dumps(compounds)
    logger.info("-----In retrieve_copounds dump")
    return json



@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['GET'])
def retrieve_compound(compound_id):
    if compound_id:
        data_svc = get_compound_dao()
        compound = data_svc.retrieve(compound_id)
    else:
        raise NoIdProvidedError()
    if compound is None:
        raise ObjectNotFoundError()
    json = dumps(compound)
    return json


@app.route(COMPOUNDS_URL_ROOT, methods=['POST'])
def create_compound():
    data = json.loads(request.data)
    get_compound_dao().create(data)
    return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})


@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['PATCH'])
def update_compound(compound_id):
    data = json.loads(request.data)
    if compound_id:
        get_compound_dao().update(compound_id, data)
    else:
        raise NoIdProvidedError()
    return dumps({'message': 'SUCCESS'})

@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['DELETE'])
def delete_compound(compound_id):
    if compound_id:
        get_compound_dao().delete(compound_id)
    else:
        raise NoIdProvidedError()
    return dumps({'message': 'SUCCESS'})


@app.route(EXPERIMENTS_URL_ROOT, methods=['POST'])
def create_experiment():
    data = json.loads(request.data)
    jsonschema.validate(data, EXPERIMENTS_SCHEMA)
    get_experiment_dao().create(data)
    return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})


@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['GET'])
def retrieve_experiment(experiment_id):
    if experiment_id:
        data_svc = get_experiment_dao()
        experiment = data_svc.retrieve(experiment_id)
    else:
        raise NoIdProvidedError()
    if experiment is None:
        raise ObjectNotFoundError()
    json = dumps(experiment)
    return json
        


@app.route(EXPERIMENTS_URL_ROOT, methods=['GET'])
def retrieve_experiments():
    data_svc = get_experiment_dao()
    experiments = data_svc.retrieve_many()
    json = dumps(experiments)
    return json

@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['DELETE'])
def delete_experiment(experiment_id):
    if experiment_id:
        get_experiment_dao().delete(experiment_id)
    else:
        raise NoIdProvidedError()
    return dumps({'message': 'SUCCESS'})
    


@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['PUT'])
def update_experiment(experiment_id):
    data = json.loads(request.data)
    jsonschema.validate(data, EXPERIMENTS_SCHEMA)

    if experiment_id:
        get_experiment_dao().update(experiment_id, data)
    else:
        raise NoIdProvidedError()
    return dumps({'message': 'SUCCESS'})







@app.errorhandler(404)
def resource_not_found(error):
    logger.info("Resource not found: ", exc_info=1)
    return make_response(str({'error': 'resource not found'}), 404)


@app.errorhandler(jsonschema.exceptions.ValidationError)
def validation_error(error):
    logger.info(" Validation Error: ", exc_info=1 )
    return make_response(str(error), 400)

#This actually might never get called because trailing slashes with
#no parameters won't get routed to the route that would raise a
#NoIdProvidedError, they would get routed to a route that just 
#has the trailing slash
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

@app.errorhandler(Exception)
def general_error(error):
    logger.critical(" Houston we have a problem: ", exc_info=1)
    return make_response(str(error), 500)


def main(args=None):
    logger.info("-----In Main")
    app.run()

if __name__ == '__main__':
    main()
