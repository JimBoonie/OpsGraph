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

@app.route('/run-simple-graph')
def run_simple_graph():
    """
    Run simple graph model and return output and node depths.
    """
    
    return "run simple graph"

@app.route('/run-complex-graph')
def run_complex_graph():
    """
    Run complex graph model and return output and node depths
    """

    return "run complex graph"
