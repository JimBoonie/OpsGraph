from random import randint

class OpNet:
    """
    Manager class for all created nodes, ports, and pipes.
    """

    def __init__(self):
        self.nodes = []
        self.pipes = []

    def add_node(self, op, params, outputs, name=None):
        """
        Add new node to net.
        """

        if name is None:
            name = op.__name__ + "-{:04}".format(randint(0, 9999))
        new_node = Node(op, name, params, outputs)
        self.nodes.append(new_node)
        return new_node

    def remove_node(self, node):
        """
        Unbind pipes attached to node and remove node from net.
        """

        for param in node.params:
            if isinstance(param._value, Pipe):
                self.unbind(param._value)

        for output in node.outputs:
            if isinstance(output._value, Pipe):
                self.unbind(output._value)

        # remove pipe from opnet internal list
        located = False
        for idx, n in enumerate(self.nodes):
            if n is node:
                del self.nodes[idx]
                located = True
                break

        if not located:
            raise ValueError("node not found in this instance of OpNet.")

        node = None
        return node

    def _add_pipe(self, node1_output, node2_param):
        """
        Add new pipe to net.
        """

        pipe = Pipe(node1_output, node2_param)
        self.pipes.append(pipe)
        return pipe

    def _remove_pipe(self, pipe):
        """
        Unbind pipe and remove from net.
        """

        # remove pipe from references in its bound parameters
        pipe.source._value = None
        pipe.output._value = None

        # remove references to parameters from pipe
        pipe.source = None
        pipe.output = None

        # remove pipe from opnet internal list
        located = False
        for idx, c in enumerate(self.pipes):
            if c is pipe:
                del self.pipes[idx]
                located = True
                break

        if not located:
            raise ValueError("pipe not found in this instance of OpNet.")

    def bind(self, node1, node1_output_name, node2, node2_param_name):
        """
        Connect OUTPUT_NAME of NODE1 to PARAM_NAME of NODE2 via a new pipe.
        """

        node1_output = node1.get_output(node1_output_name)
        node2_param = node2.get_param(node2_param_name)

        return self._add_pipe(node1_output, node2_param)

    def unbind(self, pipe):
        """
        Disconnect ports from pipe and remove pipe from net.
        """

        self._remove_pipe(pipe)

        # set pipe to None
        pipe = None
        return pipe

    def get_root_nodes(self):
        """
        Return list of nodes that have non-pipe inputs.
        """

        rootnodes = []
        for node in self.nodes:
            if any(not isinstance(p._value, Pipe) for p in node.params):
                rootnodes.append(node)

        return rootnodes

    def _walk_pipes_for_depth(self, node, depth=0):
        """
        Traverse output pipes from node to determine depth of node.
        """

        new_depth = depth
        for output in node.outputs:
            if isinstance(output._value, Pipe):
                dest_node = output._value.output.node
                new_depth = min(depth, self._walk_pipes_for_depth(dest_node, depth + 1))
            
        node.depth = new_depth
        return new_depth

    def _compute_depths(self):
        """
        Traverse graph from root nodes and assign depth to all nodes.
        """

        rootnodes = self.get_root_nodes()

        for rootnode in rootnodes:
            self._walk_pipes_for_depth(rootnode)

    def run(self):
        """
        Evaluate all node operations in ascending order of depth.
        """

        self._compute_depths()
        sorted_nodes = sorted(self.nodes, key=lambda x: x.depth)
        results = []
        for node in sorted_nodes:
            print("!!!!!!!!!!!!!!!!!!!!!!!")
            print(node.name)
            for p in node.params:
                print("{}: {}".format(p.name, p.get_value()))
            result = {
                'node': node,
                'outputs': node.execute()
            }
            print(result)
            print("Depth: {}".format(node.depth))
            results.append(result)

        return results

class Node:
    """
    Represents an operation and its associated input parameters and outputs.
    """

    def __init__(self, op, name, params, outputs):
        """
        Create new node.

        Inputs:
            op: Reference to function.
            name: Name to identify this Node.
            params: Dictionary of parameters to function defined in 'op'. The key 
                is the name of the parameter and the value is its assigned value. 
                Set to None if you intend to connect a pipe to it.
            outputs: List of strings with arbitrary names for ordered outputs of 
                function 'op'.
        """

        self.op = op
        self.name = name
        self.params = [Param(name, self, value) for (name, value) in params.items()]
        self.outputs = [Output(name, self) for name in outputs]
        self.depth = None

    def __repr__(self):
        return "<Node op:{} name:{} params:{} outputs:{} depth:{}>".format(
            self.op, self.name, self.params, self.outputs, self.depth
        )

    def __str__(self):
        return "Node: \
                    \n\top: {} \
                    \n\tname: {} \
                    \n\tparams: {} \
                    \n\toutputs: {} \
                    \n\tdepth: {}".format(
            self.op, self.name, self.params, self.outputs, self.depth
        )

    def get_param(self, name):
        """
        Return parameter with given name from node.
        """

        target_param = None
        for param in self.params:
            if param.name == name:
                target_param = param
                break

        if target_param is None:
            raise NameError("{0} was not found in params of node2.".format(name))

        return target_param

    def get_output(self, name):
        """
        Return output with given name from node.
        """

        target_output = None
        for output in self.outputs:
            if output.name == name:
                target_output = output
                break

        if target_output is None:
            raise NameError("{0} was not found in outputs of node1.".format(name))

        return target_output

    def unpack_params(self):
        """
        Return dict of params with key as name and source as value.
        """

        return {param.name: param.get_value() for param in self.params}

    def list_outputs(self):
        """
        Return list of output names.
        """

        return [output.name for output in self.outputs]

    def param_values(self):
        """
        Return dict with param names as keys and param values as values.
        """

        return {param.name: param.get_value() for param in self.params}

    def output_values(self):
        """
        Return dict with output names as keys and output values as values.
        """

        return {output.name: output.get_value() for output in self.outputs}

    def execute(self):
        """
        Run operation stored at node. 
        """

        outs = self.op(**self.unpack_params())
        outs = ensure_is_listlike(outs)
        print(outs)

        # store outputs as value
        for (s_out, out) in zip(self.outputs, outs):
            s_out.set_value(out)

        # convert to dict for output
        outs = {name: out for (name, out) in zip(self.list_outputs(), outs)}
        return outs

class Port:
    """
    Represents a value for a given parameter or output of a Node along with its 
    management logic.
    """

    def __init__(self, name, node, value=None, datatypes=(None,)):
        self.name = name
        self.node = node
        self._value = value

        datatypes = ensure_is_listlike(datatypes)
        self.datatypes = datatypes

    def get_value(self):
        """
        Return value stored at this port.
        """

        if isinstance(self._value, Pipe):
            return self._value.value
        else:
            return self._value

    def set_value(self, value):
        """
        Set value stored at this port.
        """

        if isinstance(self._value, Pipe):
            self._value.value = value
        else:
            self._value = value

class Param(Port):
    """
    Subclass of Port with behavior specific to operation parameters.
    """

    pass

class Output(Port):
    """
    Subclass of Port with behavior specific to operation outputs.
    """

    pass

class Pipe:
    """
    Manages a connection between the Output of a given Node and the Param of 
    another Node.
    """

    def __init__(self, source, output):
        source._value = self
        output._value = self
        self.source = source
        self.output = output
        self.value = None

def ensure_is_listlike(thing):
    """
    Check if THING is list or tuple and, if neither, converts to list.
    """

    if not isinstance(thing, (list, tuple)):
        thing = [thing,]

    return thing
