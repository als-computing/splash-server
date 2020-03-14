import json
import os

import jsonschema
from bson.json_util import dumps
from flask import request, current_app, app
from flask_restful import Resource
from splash.data import (BadIdError, MongoCollectionDao,
                         ObjectNotFoundError)

dirname = os.path.dirname(__file__)
experiments_schema_file = open(os.path.join(dirname, "experiment_schema.json"))
EXPERIMENTS_SCHEMA = json.load(experiments_schema_file)
experiments_schema_file.close()

class Experiments(Resource):
    def __init__(self, ):
        self.dao = MongoCollectionDao(current_app.db.splash.experiments)
        super()

   

    def get(self):
        try:
            pageNum = request.args.get('page', 1)
            if pageNum is None or pageNum <= 0:
                raise ValueError("Page parameter must be positive")
            results = self.dao.retrieve_many(page=pageNum)
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
        self.dao.create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})

    def put(self):
        data = json.loads(request.data)
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)

        if 'uid' in data:
            self.dao().update(data)
        else:
            raise BadIdError()
        return dumps({'message': 'SUCCESS'})

class Experiment(Resource):
    def __init__(self, ):
        self.dao = MongoCollectionDao(current_app.db.splash.experiments)
        super()


    def get(self, uid):
        results = self.dao.retrieve(uid)
        return json.dumps(results)
 
    def post(self):
        data = json.loads(request.data)
        jsonschema.validate(data, EXPERIMENTS_SCHEMA)
        self.dao.create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})
