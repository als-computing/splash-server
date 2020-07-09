import os
import json
import jsonschema
from flask_restful import Resource
from flask import request, make_response
from splash.categories.runs.runs_service import RunService


class RunResource(Resource):
    def __init__(self, run_service: RunService):
        self.run_service = run_service
        runs_schema = open_schema()
        self.validator = jsonschema.Draft7Validator(runs_schema)

    def get(self):
        payload = request.get_json(force=True)
        self.validator.validate(payload)
        catalog = payload['catalog']
        run_uid = payload['run_uid']
        preview = self.run_service.get_preview(uid=run_uid, catalog_name=catalog)
        response = make_response(preview.to_dict())
        response.headers['content-type'] = 'application/octet-stream'
        return response


def open_schema():
    dirname = os.path.dirname(__file__)
    runs_schema_file = open(os.path.join(dirname, "runs_schema.json"))
    runs_schema = json.load(runs_schema_file)
    runs_schema_file.close()
    return runs_schema
