import json

from bson.json_util import dumps
from flask import jsonify, request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from splash.service.base import Service


class MalformedJsonError(json.JSONDecodeError):
    def __init__(self, error: json.JSONDecodeError):
        super().__init__(error.msg, error.doc, error.pos)


class AuthenticatedResource(Resource):
    def __init__(self):
        self.method_decorators = [jwt_required]
        super().__init__()


class MultiObjectResource(AuthenticatedResource):

    def __init__(self, service: Service):
        super().__init__()
        self.service = service

    def get(self):
        page_number = request.args.get('frame', 1)
        results = self.service.retrieve_multiple(page_number)
        data = {"total_results": results[0], "results": list(results[1])}
        return data

    def post(self):
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise MalformedJsonError(e) from None

        issues = self.service.validate(data)

        if len(issues) == 0:
            self.service.create(data)
            return {'message': 'CREATE SUCCESS', 'uid': str(data['uid'])}
        errors = []
        for issue in issues:
            errors.append({'description': issue.description, 'location': issue.location})
        return {'error': 'validation_error', 'errors': errors}, 400

class SingleObjectResource(AuthenticatedResource):
    def __init__(self, service: Service):
        super().__init__()
        self.service = service

    def get(self, uid):
        results = self.service.retrieve_one(uid)
        return results

    def put(self, uid):
        try:
            data = json.loads(request.data)
        except json.JSONDecodeError as e:
            raise MalformedJsonError(e) from None

        issues = self.service.validate(data)

        if len(issues) == 0:
            self.service.update(data)
            return {'message': 'UPDATE SUCCESS', 'uid': str(data['uid'])}
        errors = []
        for issue in issues:
            errors.append({'description': issue.description, 'location': issue.location})
        return {'error': 'validation_error', 'errors': errors}, 400
