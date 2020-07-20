import os
import json


def openSchema(schema_name, current_file):
    """Opens the specified filename: `schema_name` assuming it's in the
    directory of `current_file` and returns the contents as
    a dict. Meant for opening JSON schemas for different categories """
    dirname = os.path.dirname(current_file)
    schema_file = open(os.path.join(dirname, schema_name))
    SCHEMA = json.load(schema_file)
    schema_file.close()
    return SCHEMA
