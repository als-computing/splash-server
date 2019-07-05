from pymongo import MongoClient
from bluesky.plans import scan, count
from bluesky.run_engine import RunEngine
from suitcase.mongo_normalized import Serializer
from bluesky.callbacks.core import CallbackBase
# from databroker import Broker
from ophyd.sim import SynSignal, det1, det2, det4, motor1, motor2, motor3

from splash.config import Config
# import numpy as np
import pandas as pd
import queue

step = 0
data = pd.read_csv('test/nexafs_2.csv')

energy_queue = queue.Queue()
absorption_queue = queue.Queue()

for energy in data['Beamline Energy']:
    energy_queue.put(energy)

for absorption in data['TEY signal']:
    absorption_queue.put(absorption)

def import_metadata():

    bec = MyCallback()
    RE = RunEngine({})
    RE.subscribe(bec)
    # db = Broker.named('temp')
    # RE.subscribe(db)func(

    #RE(count(dets))
    RE(generate_nexafs_scan_data())


def get_energy():
    return energy_queue.get()

def get_absorption():
    return absorption_queue.get()

def generate_nexafs_scan_data():
    # xas = SynSignal(name='det1',  func=get_absorption)

    mono_chrome_motor = SynSignal(name='mono_chrome_motor',  func=get_energy, labels={'motors'})
    xas = SynSignal(name='det1',  func=get_absorption,   labels={'detectors'})
    plan = scan([xas],
                mono_chrome_motor, 0, 10,
                len(data),
                md = {'sample_name': 'dilithium crystal'})
    return plan





class MyCallback(CallbackBase):

    def __init__(self):
        from pathlib import Path
        config_file = str(Path.home() / '.splash' / 'config.cfg')
        config = Config(config_file)
        mongo_url = config.get('AppDB', 'mongo_url', fallback='localhost:27017')
        print (f"using mongo db: {mongo_url}")
        self.client = MongoClient(mongo_url)
        self.serializer = Serializer(self.client['mds'], self.client['assets'])

    def __call__(self, name, doc):
        CallbackBase.__call__(self, name, doc)
        # if name == 'start':
        #     self.serializer.start(doc)
        # print (str(name) + str(doc))

    def event(self, doc):
        self.serializer.event(doc)

    def bulk_events(self, doc):
        self.serializer.bulk_events()

    def resource(self, doc):
        self.serializer.resource(doc)

    def datum(self, doc):
        self.serializer.datum(doc)

    def bulk_datum(self, doc):
        self.serializer.bulk_datum(doc)

    def descriptor(self, doc):
        self.serializer.descriptor(doc)

    def start(self, doc):
        self.serializer.start(doc)
        print ('uid: ' + doc['uid'])

    def stop(self, doc):
        self.serializer.stop(doc)


# class XASSignal(SynSignal):
#     def __init__(self, name, motor, motor_field, center, Imax, sigma=1,
#                  noise=None, noise_multiplier=1, random_state=None, **kwargs):
#         if noise not in ('poisson', 'uniform', None):
#             raise ValueError("noise must be one of 'poisson', 'uniform', None")
#         self._motor = motor
#
#         if random_state is None:
#             random_state = np.random
#
#         def func():
#             m = motor.read()[motor_field]['value']
#             v = Imax * np.exp(-(m - center) ** 2 / (2 * sigma ** 2))
#             if noise == 'poisson':
#                 v = int(random_state.poisson(np.round(v), 1))
#             elif noise == 'uniform':
#                 v += random_state.uniform(-1, 1) * noise_multiplier
#             return v
#         super().__init__(func=func, name=name, **kwargs)

if __name__ == '__main__':
    import_metadata()