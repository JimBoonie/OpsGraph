var box_defaults = {
    strokeColor: 'black',
    fillColor: 'blue',
    strokeWidth: 6,
    hoverStrokeColor: 'green'
};

var input_defaults = {
    fillColor: 'black',
    hoverFillColor: 'green'
};

var output_defaults = {
    fillColor: 'black',
    hoverFillColor: 'red'
};

var node_defaults = {
    port_radius: 15,
    port_spacing: 10,
    text_offset: [0, -10],
    depth_offset: [0, 10]
};

var node_name_defaults = {
    justification: 'left',
    fillColor: 'black',
    fontSize: '1em'
}

var node_depth_defaults = {
    justification: 'center',
    fillColor: 'white',
    fontSize: '2em'
}
 
var pipe_props = {
    strokeColor: 'black',
    strokeWidth: 6
}

var hitOptions = {
    segments: true,
    stroke: true,
    fill: true,
    tolerance: 5
};

function assignProperties(path, properties) {
    for (key in properties) {
        path[key] = properties[key];
    }
}

function Node(op, n_inputs, n_outputs, position, node_props, box_props) {
    this.inputs = [];
    this.outputs = [];
    this.op_name = op;            // to identify op on server
    this.display_name = op;
    this.createPorts = function(n_ports, port_type, port_defaults) {
        var box_corner = this.group.firstChild.point;
        var sp = node_props.port_spacing;
        var r = node_props.port_radius;
        for (var i = 0; i < n_ports; i++) {
            // create port group
            var port = new Group();
            port.num = i;
            port.obj_type = port_type;
            port.node = this;
            port.value = undefined;

            // create port path
            var offset = i * (sp + 2 * r) + sp + r;
            if (port_type == "output") {
                var center = [box_corner[0] + box_w, box_corner[1] + offset];
            } else {
                var center = [box_corner[0], box_corner[1] + offset];
            }
            var port_path = new Path.Circle({
                center: center, 
                radius: r
            });
            port.appendTop(port_path);
            assignProperties(port_path, port_defaults);
            port_path.onMouseEnter = function(event) {
                this.previousFillColor = this.fillColor;
                this.fillColor = this.hoverFillColor;
            };
            port_path.onMouseLeave = function(event) {
                this.fillColor = this.previousFillColor;
            };

            this.group.appendTop(port);
            if (port_type == "output") {
                this.outputs.push(port);
            } else {
                this.inputs.push(port);
            }
        }
    }

    this.delete = function() {
        // remove all ports and their pipes and paper paths
        for (var i = 0; i < this.inputs.length; i++) {
            var input = this.inputs[i];
            if (input.value instanceof Pipe) {
                input.value.delete();
            }
            input.value = undefined;
            input.children[0].remove();
        }
        this.inputs = [];
        for (var i = 0; i < this.outputs.length; i++) {
            var output = this.outputs[i];
            if (output.value instanceof Pipe) {
                output.value.delete();
            }
            output.value = undefined;
            output.children[0].remove();
        }
        this.outputs = [];

        // remove own group
        this.group.remove();
        this.group = undefined;
    }

    // create box for node base
    var n_ports = n_inputs > n_outputs ? n_inputs : n_outputs;
    var sp = node_props.port_spacing;
    var r = node_props.port_radius;
    var box_w = 100;
    var box_h = (n_ports - 1) * (sp + 2 * r) + 2 * (sp + r);
    var box = new Path.Rectangle({
        point: position,
        size: [box_w, box_h],
    }); 
    assignProperties(box, box_props);
    box.onMouseEnter = function(event) {
        this.previousStrokeColor = this.strokeColor;
        this.strokeColor = this.hoverStrokeColor;
    };
    box.onMouseLeave = function(event) {
        this.strokeColor = this.previousStrokeColor;
    }; 

    // create display name object
    var t_off = node_props.text_offset;
    var text_position = [position[0] + t_off[0], position[1] + t_off[1]];
    var disp_name_path = new PointText({
        point: text_position,
        content: this.display_name  
    });
    assignProperties(disp_name_path, node_name_defaults);

    // create node depth object
    var d_off = node_props.depth_offset;
    var depth_position = [position[0] + box_w / 2 + d_off[0], 
                          position[1] + box_h / 2 + d_off[1]];
    var node_depth_path = new PointText({
        point: depth_position,
        content: "?"  
    });
    assignProperties(node_depth_path, node_depth_defaults);
    node_depth_path.bringToFront();

    // create group for all items
    this.group = new Group([box, disp_name_path, node_depth_path]);
    this.group.node = this;
    this.group.obj_type = "node";

    // create ports for inputs and outputs
    this.createPorts(n_inputs, "input", input_defaults);
    this.createPorts(n_outputs, "output", output_defaults);

    return this;
}

function Pipe(props, output, input) {
    // create line to add as pipe
    // line is added as property of group but is NOT child of group
    if (typeof input !== 'undefined') {
        var endpoint = input.position;
    } else {
        var endpoint = output.position;
    }
    this.line = new Path.Line(output.position, endpoint);
    assignProperties(this.line, props);
    this.line.sendToBack();

    // function to delete itself
    this.delete = function() {
        if (this.input) {
            this.input.value = undefined;
        }
        if (this.output) {
            this.output.value = undefined;
        }
        this.input = undefined;
        this.output = undefined;
        this.line.remove();
        this.line = undefined;
    }

    // add references to link pipe and output
    output.value = this;
    this.output = output;

    // add references to link pipe and input, if given
    if (typeof input !== 'undefined') {
        input.value = this;
        this.input = input;
    } else {
        this.input = undefined;
    }

    return this;
}

Array.prototype.clear = function() {
    for (var i = this.length - 1; i >= 0; i--) {
        this[i].delete();
        this.splice(i, 1);
    }
}

var active_graph = undefined;
var nodes = [];
var pipes = [];
function openSimpleGraph() {
    active_graph = '/run-simple-graph';

    pipes.clear();
    nodes.clear();

    nodes.push(new Node('double', 1, 1, [100, 100], node_defaults, box_defaults));
    nodes.push(new Node('double', 1, 1, [300, 100], node_defaults, box_defaults));
    nodes.push(new Node('double', 1, 1, [500, 100], node_defaults, box_defaults));

    pipes.push(new Pipe(pipe_props, nodes[0].outputs[0], nodes[1].inputs[0]));
    pipes.push(new Pipe(pipe_props, nodes[1].outputs[0], nodes[2].inputs[0]));
}

function openComplexGraph() {
    active_graph = '/run-complex-graph';

    nodes.clear();
    console.log(active_graph);
}

function run() {
    $.ajax({
        type: 'POST',
        url: active_graph,
        async: true,
        data: {
            'input_val': 2
        },
        success: function(response) {
            console.log(response);
        }
    });
}

var folder_id_root = "folder-";
$(document).ready(function() {
    document.getElementById('simple-graph-button').onclick = openSimpleGraph;
    document.getElementById('complex-graph-button').onclick = openComplexGraph;
    document.getElementById('run-button').onclick = run;

    openSimpleGraph();
});
