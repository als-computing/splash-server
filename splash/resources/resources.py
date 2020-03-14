from bson.json_util import dumps
from flask import request
from flask_restful import Resource
import json
from splash.service.data import BadIdError


class DAOResource(Resource):
    def __init__(self, dao):
        self.dao = dao
        super().__init__()


class MultiObjectResource(DAOResource):
    def __init__(self, dao):
        super().__init__(dao)

    def get(self):
        try:
            pageNum = request.args.get('page', 1)
            if pageNum is None or pageNum <= 0:
                raise ValueError("Page parameter must be positive")
            results = self.dao.retrieve_multiple(pageNum)
            data = {"total_results": results[0], "results": results[1]}
            json = dumps(data)
            return json
        except ValueError as e:
            if str(e) == "Page parameter must be positive":
                raise e from None
            raise TypeError("page parameter must be a positive integer") from None
        
    def post(self):
        data = json.loads(request.data)
        self.dao.create(data)
        return dumps({'message': 'CREATE SUCCESS', 'uid': str(data['uid'])})


class SingleObjectResource(DAOResource):
    def __init__(self, dao):
        super().__init__(dao)

    def get(self, uid):
        results = self.dao.retrieve(uid)
        return dumps(results)

    def put(self):
        data = json.loads(request.data)

        if 'uid' in data:
            self.dao().update(data)
        else:
            raise BadIdError()
        return dumps({'message': 'SUCCESS'})