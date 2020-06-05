from bson.json_util import dumps
from flask import request, jsonify
from flask_login import login_required
from flask_restful import Resource
import json
from splash.data.base import BadIdError


class DAOResource(Resource):
    method_decorators = [login_required]
    
    def __init__(self, dao):
        self.dao = dao
        super().__init__()


class MultiObjectResource(DAOResource):
    def __init__(self, dao):
        super().__init__(dao)

    def get(self):
        try:
            pageNum = int(request.args.get('page', 1))
            if pageNum is None or pageNum <= 0:
                raise ValueError("Page parameter must be positive")
            results = self.dao.retrieve_paged(pageNum, page_size=0)
            data = {"total_results": results[0], "results": list(results[1])}
            return data
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
        return results

    def put(self, uid):
        data = request.data

        if 'uid' in data:
            self.dao().update(uid)
        else:
            raise BadIdError()
        return dumps({'message': 'SUCCESS'})