import os
import json
from flask_restful import Resource
from flask import Response, send_file
from splash.categories.runs.runs_service import RunService


class Catalogs(Resource):

    def __init__(self, run_service: RunService):
        self.run_service = run_service

    def get(self):
        return {'catalogs': self.run_service.list_catalogs()}


class Runs(Resource):
    def __init__(self, run_service: RunService):
        self.run_service = run_service

    def get(self, catalog):
        return {'runs': self.run_service.list_runs(catalog)}


class Run(Resource):
    def __init__(self, run_service: RunService):
        self.run_service = run_service

    def get(self, catalog, uid,):
        jpeg_file_object = self.run_service.get_image(catalog_name=catalog, uid=uid)
        return send_file(jpeg_file_object, mimetype='image/JPEG')

        #response = Response(generator)
        #response.headers['Content-Type'] = 'application/octet-stream'
        #TODO: generalize image width for all images
        #response.headers['image-width'] = 1024
        #TODO: generalize datatype for all images
        #response.headers['data-type'] = 'uint16'
        #TODO: will images ever have more than one number representing a pixel?

