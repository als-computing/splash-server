import os
import json
import jsonschema
from flask_restful import Resource
from flask import request, make_response, Response
from splash.categories.runs.runs_service import RunService
import xarray
import sys


class Run(Resource):
    def __init__(self, run_service: RunService):
        self.run_service = run_service
        runs_schema = open_schema()
        self.validator = jsonschema.Draft7Validator(runs_schema)

    def post(self):
        payload = request.get_json(force=True)
        self.validator.validate(payload)
        catalog = payload['catalog']
        run_uid = payload['run_uid']
        preview = self.run_service.get_preview(uid=run_uid, catalog_name=catalog)
        response = Response(stream_image_as_bytes(preview))
        response.headers['Content-Type'] = 'application/octet-stream'
        #TODO: generalize image width for all images
        response.headers['image-width'] = 1024
        #TODO: generalize datatype for all images
        response.headers['data-type'] = 'uint16'
        #TODO: will images ever have more than one number representing a pixel?

        return response


def open_schema():
    dirname = os.path.dirname(__file__)
    runs_schema_file = open(os.path.join(dirname, "runs_schema.json"))
    runs_schema = json.load(runs_schema_file)
    runs_schema_file.close()
    return runs_schema


def ensure_small_endianness(dataarray):
    byteorder = dataarray.data.dtype.byteorder
    if byteorder == '=' and sys.byteorder == 'little':
        return dataarray
    elif byteorder == '<':
        return dataarray
    elif byteorder == '|':
        return dataarray
    elif byteorder == '=' and sys.byteorder == 'big':
        return dataarray.data.byteswap().newbyteorder()
    elif byteorder == '>':
        return dataarray.data.byteswap().newbyteorder()
   
        

# This function should yield the array in 32 row chunks
def stream_image_as_bytes(dataarray):
    #TODO generalize the function for any sized image
    for chunk_beginning in range(0, 1024, 32):
        chunk_end = chunk_beginning + 32
        chunk = dataarray[chunk_beginning:chunk_end].compute()
        chunk = ensure_small_endianness(chunk)
        yield bytes(chunk.data)
