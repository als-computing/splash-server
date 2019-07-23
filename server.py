from flask import Flask, jsonify
from flask import request, Response
from pymongo import MongoClient
from bson.json_util import dumps
from flask_cors import CORS, cross_origin
from flask import g, abort
import json
import os
from splash.config import Config
from splash.data import MongoCollectionDao, ObjectNotFoundError, BadIdError
from splash.visualization import rsoxs
from splash.util import context_timer
from bokeh.plotting import figure
from bokeh.embed import json_item
import logging
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

app = None
logger = logging.getLogger('simple_example')


def setup_logging():
    try:
        flask_cors_logger = logging.getLogger('flask_cors')
        flask_cors_logger.setLevel(logging.DEBUG)
        logging_level = os.environ.get("LOGLEVEL")

        logger.setLevel(logging.DEBUG)

        # create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # add formatter to ch
        ch.setFormatter(formatter)

        # add ch to logger
        logger.addHandler(ch)


    except Exception as e:
        print("cannot setup logging: {}".format(str(e)))


def create_app():
    app = Flask(__name__)
    CORS(app)
    setup_logging()
    # app.app_context().push()
    return app


# if app is None:
#     app = create_app()
SPLASH_SERVER_DIR = os.environ.get("SPLASH_SERVER_DIR")
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
app = create_app()


def get_compound_dao():
    try:
        db = MongoClient(MONGO_URL)  # , ssl=True, ssl_ca_certs=certifi.where(), connect=False)
        return MongoCollectionDao(db.efrc.compounds)
    except Exception as e:
        logger.info("Unable to connect to database: " + str(e))
        print("Unable to connect to database: " + str(e))
        return

def get_experiment_dao():
    try:
        db = MongoClient(MONGO_URL)
        return MongoCollectionDao(db.efrc.experiments)
    except Exception as e:
        logger.info("Unable to connect to database: " + str(e))
        print("Unable to connect to database: " + str(e))
        return

# @app.teardown_appcontext
# def teardown_db(exception):
#     db = g.pop('db')
#     if db is not None:
#         db.close()

@app.route(COMPOUNDS_URL_ROOT, methods=['GET'])
def retrieve_compounds():
    try:
        data_svc = get_compound_dao()

        logger.info("-----In retrieve_copounds")
        compounds = data_svc.retrieve_many()
        logger.info("-----In retrieve_copounds find")
        json = dumps(compounds)
        logger.info("-----In retrieve_copounds dump")
        return json
    except Exception as e:
        logger.warning(str(e))
        return dumps({'error': str(e)})


@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['GET'])
def retrieve_compound(compound_id):
    try:
        data_svc = get_compound_dao()
        compound = data_svc.retrieve(compound_id)
        if compound is None:
            abort(404)
        json = dumps(compound)
        return json
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, str(BadIdError))


@app.route(COMPOUNDS_URL_ROOT, methods=['POST'])
def create_compound():
    try:
        data = json.loads(request.data)
        get_compound_dao().create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})
    except Exception as e: # TODO: make the except blocks more specific to different error types
        return dumps({'error': str(e)})


@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['PATCH'])
def update_compound(compound_id):
    try:
        data = json.loads(request.data)
        if compound_id:
            get_compound_dao().update(compound_id, data)
        else:
            abort(400, "id not provided")
        return dumps({'message': 'SUCCESS'})
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, e)


@app.route(COMPOUNDS_URL_ROOT + "/<compound_id>", methods=['DELETE'])
def delete_compound(compound_id):
    try:
        if compound_id:
            get_compound_dao().delete(compound_id)
        return dumps({'message': 'SUCCESS'})
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, e)


@app.route(EXPERIMENTS_URL_ROOT, methods=['POST'])
def create_experiment():
    try:
        data = json.loads(request.data)
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)
        get_experiment_dao().create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})
    except jsonschema.exceptions.ValidationError as e:
        abort(400, e)
    except Exception as e: # TODO: make the except blocks more specific to different error types
        logger.warning(str(e))
        abort(500)


@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['GET'])
def retrieve_experiment(experiment_id):
    try:
        data_svc = get_experiment_dao()
        experiment = data_svc.retrieve(experiment_id)
        if experiment is None:
            abort(404)
        json = dumps(experiment)
        return json 
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, str(BadIdError))
    except Exception as e:
        logger.warning(str(e))
        abort(500)
        


@app.route(EXPERIMENTS_URL_ROOT, methods=['GET'])
def retrieve_experiments():
    try:
        data_svc = get_experiment_dao()
        experiments = data_svc.retrieve_many()
        json = dumps(experiments)
        return json
    except Exception as e:
        logger.warning(str(e))
        return dumps({'error': str(e)})


@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['DELETE'])
def delete_experiment(experiment_id):
    try:
        if experiment_id:
            get_experiment_dao().delete(experiment_id)
        return dumps({'message': 'SUCCESS'})
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, e)
    except Exception as e:
        logger.warning(str(e))
        abort(500)


@app.route(EXPERIMENTS_URL_ROOT + "/<experiment_id>", methods=['PUT'])
def update_experiment(experiment_id):
    try:
        data = json.loads(request.data)
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)

        if experiment_id:
            get_experiment_dao().update(experiment_id, data)
        else:
            abort(400, "id not provided")
        return dumps({'message': 'SUCCESS'})
    except jsonschema.exceptions.ValidationError as e:
        abort(400, e)
    except ObjectNotFoundError as e:
        abort(404)
    except BadIdError as e:
        abort(400, e)
    except Exception as e:
        logger.warning(str(e))
        abort(500)



# </editor-fold>
def main(args=None):
    logger.info("-----In Main")
    app.run(debug=True)

if __name__ == '__main__':
    main()
