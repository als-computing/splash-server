import json
from bson.json_util import dumps

import bokeh
print('bokeh:', bokeh.__path__)

from splash.data import BadIdError
from bokeh.plotting import figure
from bokeh.embed import json_item


def naxafs_to_xy_graph(event):
    xy_obj = {'y': event['data']['det1'], 'x': event['data']['mono_chrome_motor']}
    return dumps(xy_obj)


def retrieve_run(dao, run_uid):
    run = dao.retrieve(run_uid)
    if run is None:
        raise BadIdError()

    def generate():
        yield '{"metadata": ' + dumps(run.metadata)+',"data": ['
        is_first  = True
        for name, event in run():
            if name == 'event':
                yield ',' + naxafs_to_xy_graph(event) if not is_first else naxafs_to_xy_graph(event)
                if is_first:
                    is_first = False

        yield "]}"
    return generate()


def get_nexafs_bokeh_plot(dao, run_uid, div_id):
    '''
    Returns a fully-created bokeh plot of nexafs data
    :param dao: data service for retrieving runs.
    :param run_uid: uid of the run to retrive
    :param div_id: id of the div in the DOM to attach to in html once this payload is sent to the browser
    :return:
    '''
    x_array = []
    y_array = []

    run = dao.retrieve(run_uid)
    if run is None:
        raise BadIdError()

    for name, event in run():
        if name == 'event':
            y_array.append(event['data']['det1'])
            x_array.append(event['data']['mono_chrome_motor'])

    plot = figure(plot_height=250)
    plot.circle(x_array, y_array)
    plot.line(x_array, y_array)
    # script, div = components(plot, wrap_script=False)
    # return jsonify({'div': div, 'script': script})
    return json.dumps(json_item(plot, div_id))

def get_nexafs_matrix(dao, run_uid):
    '''
    Returns a dictionary with x and y arrays. This should be changed to
    a more efficient serialization of arrays as well as be turned into a generator
    :param dao:
    :param run_uid:
    :return:
    '''
    x_array = []
    y_array = []
    run = dao.retrieve(run_uid)
    if run is None:
        raise BadIdError()

    for name, event in run():
        if name == 'event':
            y_array.append(event['data']['det1'])
            x_array.append(event['data']['mono_chrome_motor'])

    return_dict = {'x': x_array, 'y': y_array}
    return json.dumps(return_dict)
