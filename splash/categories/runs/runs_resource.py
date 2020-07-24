
from flask_restful import Resource
from flask import Response, send_file, request
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
        return self.run_service.get_runs(catalog)


class Run(Resource):
    def __init__(self, run_service: RunService):
        self.run_service = run_service

    def get(self, catalog, uid,):
        frame_number = request.args.get('frame', 0)
        retrieve_metadata = request.args.get('metadata', 'false')
        retrieve_metadata = retrieve_metadata == 'true'
        if retrieve_metadata is True:
            metadata = self.run_service.get_metadata(catalog_name=catalog, uid=uid, frame=frame_number)
            return metadata
        
        jpeg_file_object = self.run_service.get_image(catalog_name=catalog, uid=uid, frame=frame_number)
        return send_file(jpeg_file_object, mimetype='image/JPEG')

        #response = Response(generator)
        #response.headers['Content-Type'] = 'application/octet-stream'
        #TODO: generalize image width for all images
        #response.headers['image-width'] = 1024
        #TODO: generalize datatype for all images
        #response.headers['data-type'] = 'uint16'
        #TODO: will images ever have more than one number representing a pixel?

