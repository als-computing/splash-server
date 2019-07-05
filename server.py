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
from splash.bluesky_dao import IntakeBlueSkyDao
from splash.visualization import rsoxs
from splash.util import context_timer
from bokeh.plotting import figure
from bokeh.embed import json_item
import logging

API_URL_ROOT = "/api"
COMPOUNDS_URL_ROOT = API_URL_ROOT + "/compounds"
RUNS_URL_ROOT = API_URL_ROOT + "/runs"
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
SPLASH_CONFIG_FILE = SPLASH_SERVER_DIR + "/config.cfg" if SPLASH_SERVER_DIR is not None else "/config.cfg"
config = Config(SPLASH_CONFIG_FILE)
CFG_APP_DB = 'AppDB'
CFG_WEB = 'Web'
MONGO_URL = config.get(CFG_APP_DB, 'mongo_url', fallback='localhost:27017')
WEB_SERVER_HOST = config.get(CFG_WEB, 'server_host', fallback='0.0.0.0')
WEB_SERVER_HOST = config.get(CFG_WEB, 'server_port', fallback='80')
WEB_IMAGE_FOLDER_ROOT = config.get(CFG_WEB, 'image_root_folder', fallback='images')
app = create_app()


def get_experiment_dao():
    try:
        db = MongoClient(MONGO_URL)  # , ssl=True, ssl_ca_certs=certifi.where(), connect=False)
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
    except Exception as e:
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

def naxafs_to_xy_graph(event):
    xy_obj = {'y': event['data']['det1'], 'x': event['data']['mono_chrome_motor']}
    return dumps(xy_obj)



# </editor-fold>


if __name__ == '__main__':
    logger.info("-----In Main")
    app.run()
