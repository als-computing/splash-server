# myapp.py

from random import random

from bokeh.layouts import column
from bokeh.models import TextInput
from bokeh.plotting import figure, curdoc
from pymongo import MongoClient
from splash.bluesky_dao import IntakeBlueSkyDao
from splash.config import Config
import logging

logger = logging.getLogger('bokehserver')
logging.basicConfig(level=logging.DEBUG)

x_array = []
y_array = []


plot = figure(plot_height=250)
plot.circle(x_array, y_array)
line = plot.line(x_array, y_array)


i = 0

ds = line.data_source

config = Config(config_file_name='/home/dylan/.splash/config.cfg')
CFG_APP_DB = 'AppDB'
CFG_WEB = 'Web'
MONGO_URL = config.get(CFG_APP_DB, 'mongo_url', fallback='localhost:27017')

def get_runs_dao():
    try:
        db = MongoClient(MONGO_URL)#, ssl=True, ssl_ca_certs=certifi.where(), connect=False)
        return IntakeBlueSkyDao(db.mds, db.mds)
    except Exception as e:
        logger.info("Unable to connect to database: " + str(e))
        print ("Unable to connect to database: " + str(e))
        return


def uid_field_callback(attr, old, new):
    logger.debug("field called")
    x_array = []
    y_array = []
    # BEST PRACTICE --- update .data in one step with a new dict
    new_data = dict()
    try:
        data_svc = get_runs_dao()
        run = data_svc.retrieve(new)
        if run is None:
            logger.error(f"run {new} is empty")

        for name, event in run():
            if name == 'event':
                y_array.append(event['data']['det1'])
                x_array.append(event['data']['mono_chrome_motor'])


    except Exception as e:
        logger.error(f"exception {str(e)}")

    new_data['x'] = x_array
    new_data['y'] = y_array
    ds.data = new_data


text_input = TextInput(value="default", title="Label:")
text_input.on_change("value", uid_field_callback)

# put the button and plot in a layout and add to the document
curdoc().add_root(column(text_input, plot))