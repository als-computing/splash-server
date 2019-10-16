from flask import Flask, Blueprint
from flask_restful import Api
from pymongo import MongoClient

app = Flask(__name__, instance_relative_config=True)
api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)
app.register_blueprint(api_blueprint)
app.config.from_object('config')
app.config.from_pyfile('config.py')

db = MongoClient(app.config['MONGO_URL'],
                 username=app.config['MONGO_APP_USER'],
                 password=app.config['MONGO_APP_PW'],
                 authSource=app.config['SPLASH_DB_NAME'],
                 authMechanism='SCRAM-SHA-256')
from splash.resources import experiments
# db = MongoClient()