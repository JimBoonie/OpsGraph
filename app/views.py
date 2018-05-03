import os
from app import app
from flask import request, render_template, jsonify
from .tools import opnet

@app.route('/')
def index():
    """
    Serve the application page.
    """

    return render_template('index.html')

@app.route('/run-simple-graph', methods=['POST'])
def run_simple_graph():
    """
    Run simple graph model and return output and node depths.
    """

    # create graph object
    graph = opnet.OpNet()

    # add nodes to graph object
    node0 = graph.add_node(double, {'data': None}, ['data'])
    node1 = graph.add_node(double, {'data': None}, ['data'])
    node2 = graph.add_node(double, {'data': None}, ['data'])

    # bind nodes with pipes
    pipe0 = graph.bind(node0, 'data', node1, 'data')
    pipe1 = graph.bind(node1, 'data', node2, 'data')

    # set first input of graph
    input_val = int(request.form['input_val'])
    node0.get_param('data').set_value(input_val)

    # run graph
    results = graph.run()

    # package response
    response = {
        'output': results[-1]['outputs']['data'],
        'depths': [r['node'].depth for r in results]
    }
    return jsonify(response)

@app.route('/run-complex-graph', methods=['POST'])
def run_complex_graph():
    """
    Run complex graph model and return output and node depths
    """

    return "run complex graph"

def double(data):
    return 2 * data