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

    # create graph object
    graph = opnet.OpNet()

    # add nodes to graph object
    node0 = graph.add_node(double, {'data': None}, ['data'])
    node1 = graph.add_node(split, {'data': None, 'n': 2}, ['data1', 'data2'])
    node2 = graph.add_node(add_together, {'data1': None, 'data2': None}, ['data'])
    node3 = graph.add_node(add_together, {'data1': None, 'data2': None}, ['data'])
    node4 = graph.add_node(split, {'data': None, 'n': 2}, ['data1', 'data2', 'data3'])
    node5 = graph.add_node(add_together, {'data1': None, 'data2': None}, ['data'])
    node6 = graph.add_node(double, {'data': None}, ['data'])
    node7 = graph.add_node(add_together, {'data1': None, 'data2': None}, ['data'])
    node8 = graph.add_node(double, {'data': None}, ['data'])

    # bind nodes with pipes
    pipe0 = graph.bind(node0, 'data', node1, 'data')
    pipe1 = graph.bind(node1, 'data1', node2, 'data1')
    pipe2 = graph.bind(node2, 'data', node3, 'data1')
    pipe3 = graph.bind(node1, 'data2', node7, 'data1')
    pipe4 = graph.bind(node4, 'data1', node2, 'data2')
    pipe5 = graph.bind(node4, 'data2', node5, 'data1')
    pipe6 = graph.bind(node4, 'data3', node6, 'data')
    pipe7 = graph.bind(node5, 'data', node3, 'data2')
    pipe8 = graph.bind(node6, 'data', node7, 'data2')
    pipe9 = graph.bind(node7, 'data', node8, 'data')
    pipe10 = graph.bind(node8, 'data', node5, 'data2')

    # set first inputs of graph
    input_val = int(request.form['input_val'])
    node0.get_param('data').set_value(input_val)
    node4.get_param('data').set_value(input_val)

    print(node0.params)

    # run graph
    results = graph.run()

    # package response
    response = {
        'output': results[-1]['outputs']['data'],
        'depths': [r['node'].depth for r in results]
    }
    return jsonify(response)

def double(data):
    return 2 * data

def split(data, n):
    return [data for _ in range(n)]

def add_together(data1, data2):
    return data1 + data2