from bson.json_util import dumps
from flask import request
from flask_restful import Resource
import json
import jsonschema 
import os
from splash import app, api, db
from splash.data import MongoCollectionDao, ObjectNotFoundError, BadIdError

dao = MongoCollectionDao(db.splash.experiments)
dirname = os.path.dirname(__file__)
experiments_schema_file = open(os.path.join(dirname, "experiment_schema.json"))
EXPERIMENTS_SCHEMA = json.load(experiments_schema_file)
experiments_schema_file.close()


class Experiments(Resource):
    def get(self):
        try:
            pageNum = request.args.get('page', 1)
            if pageNum is None or pageNum <= 0:
                raise ValueError("Page parameter must be positive")
            results = dao.retrieve_many(page=pageNum)
            data = {"total_results": results[0], "results": results[1]}
            json = dumps(data)
            return json
        except ValueError as e:
            if str(e) == "Page parameter must be positive":
                raise e from None
            raise TypeError("page parameter must be a positive integer") from None

    def post(self):
        data = json.loads(request.data)
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)
        dao.create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})

api.add_resource(Experiments, "/api/experiments")
