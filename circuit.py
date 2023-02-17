from sympy import Symbol, Eq, Expr
from node import Node
from copy import deepcopy

class Circuit:

    def __init__(self):
        self._constants_     = {}
        self._constantsVals_ = {}
        self._generics_      = {}
        self._genericsVals_  = {}

        self._ports_         = set()
        self._nodes_         = set()
        self._elements_      = {}
        self._subcircuits_   = {}

        self._flattened_ = {}
        self._compiled_ = {}

    def constant(self, name, value):
        if name in self._constants_:
            raise Exception("Constant Already Exists")
        
        id = f"C{len(self._constants_)}"
        sym = Symbol(id, real=True)

        constant = {name : sym}
        constantValue = {name : value}
        self._constants_.update(constant)
        self._constantsVals_.update(constantValue)
        return sym

    def port(self, name):
        if name in self._ports_:
            raise Exception("Port Already Exists")
        
        self._ports_.add(name)
        return name

    def generic(self, name, value):
        if name in self._generics_:
            raise Exception("Generic Already Exists")

        id = f"G{len(self._generics_)}"
        sym = Symbol(id, real=True)
        generic = {name : sym}
        genericValue = {name : value}
        self._generics_.update(generic)
        self._genericsVals_.update(genericValue)
        return sym

    def node(self, name):
        if name in self._nodes_:
            raise Exception("Node Already Exists")
        
        self._nodes_.add(name)    
        return name

    def nodes(self, *names):
        nodes = list()
        for name in names:
            nodes.append(self.node(name))
        return nodes

    def element(self, element):
        if element.name in self._elements_.keys():
            raise Exception("Element Already Exists")
        
        elem = {element.name : element}
        self._elements_.update(elem)
        return elem

    def elements(self, *elements):
        elemSet = {}
        for elem in elements:
            elemSet.update(self.element(elem))
        return elemSet


    def subcircuit(self, circuit, name, ports, generics = {}):

        if name in self._subcircuits_:
            raise Exception("Subcircuit Already Exists")

        keys1 = circuit._ports_
        keys2 = set(ports.keys())

        port_map = {name : ports[name] for name in circuit._ports_}

        if keys1 != keys2:
            raise Exception("Invalid Port Map")
        
        keys1 = set(circuit._generics_.keys())
        keys2 = set(generics.keys())

        if (keys2 - keys1) != set():
            raise Exception("Generic from map not found in circuit")

        generic_map = {name : generics[name] for name in generics.keys()}

        subcircuit = {name : deepcopy((circuit, port_map, generic_map))}

        self._subcircuits_.update(subcircuit)
        return subcircuit

    """
    def currentThroughElement(self, name, id=0):
        if self.compiled != {}:
            return self.compiled["elements"][name].current(id)
        else:
            raise Exception("Not Yet Compiled")

    def potentialOnElement(self, name, id=0):
        if self.compiled != {}:
            return self.compiled["elements"][name].potential(id)
        else:
            raise Exception("Not Yet Compiled")

    def voltageOnElement(self, name, id0=0, id1=1):
        return self.potentialOnElement(name, id0) - self.potentialOnElement(name, id1)
    """

    def flatten(self, port_map = {}, generic_map={}, prefix=""):
        constants = deepcopy(self._constants_)
        constantsVals = deepcopy(self._constantsVals_)
        generics = deepcopy(self._generics_)
        genericsVals = deepcopy(self._genericsVals_)
        genericsVals.update(deepcopy(generic_map))

        generic_subs = {generics[key] : genericsVals[key] for key in generics.keys()}

        constant_subs = {constants[key] : constantsVals[key].subs(generic_subs) if "sympy" in str(type(constantsVals[key])) else constantsVals[key] for key in constants.keys()}
        constant_subs.update(generic_subs)

        while True:
            for name, value in constant_subs.copy().items():
                if "sympy" in str(type(value)):
                    value = value.subs(constant_subs)
                    constant_subs.update({name : value})

            if not any(["sympy" in str(type(value)) and not "numbers" in str(type(value)) for value in constant_subs.values()]):
                break

        nodes = deepcopy(self._nodes_)
        ports = {port : port for port in deepcopy(self._ports_)}
        elements = deepcopy(self._elements_)
        subcircuits = deepcopy(self._subcircuits_)
        
        for name, (subcircuit, subport_map, subgeneric_map) in subcircuits.items():            

            subgeneric_map = {name : value.subs(constant_subs) if "sympy" in str(type(value)) else value for name, value in subgeneric_map.items()}

            flattened = subcircuit.flatten(subport_map, subgeneric_map, name)
            nodes.update(flattened["nodes"])
            elements.update(flattened["elements"])
            ports.update(flattened["ports"])

        if prefix != "":
            for node in nodes.copy():
                nodes.remove(node)

                if node in port_map.keys():
                    node = port_map[node]
                elif isinstance(node, int) or isinstance(node, float):
                    pass
                else:
                    node = prefix + "_" + node

                if not isinstance(node, int) and not isinstance(node, float):
                    nodes.add(node)

            for name, port in ports.copy().items():
                del ports[name]

                name = prefix + "_" + name

                if port in port_map.keys():
                    port = port_map[port]
                elif isinstance(port, int) or isinstance(port, float):
                    pass
                else:
                    port = prefix + "_" + port

                ports.update({name : port})


            for name, element in elements.copy().items():
                del elements[name]

                elem_name = prefix + "_" + name
                element.name  = prefix + "_" + element.name
                element.values = {name : value.subs(constant_subs) if "sympy" in str(type(value)) else value for name, value in element.values.items()}
                
                newElemNodes = {}
                for name, node in element.nodes.items():
                    if node in port_map.keys():
                        node = port_map[node]
                    elif isinstance(node, int) or isinstance(node, float):
                        pass
                    else:
                        node = prefix + "_" + node

                    newElemNodes.update({name : node})                

                element.nodes = newElemNodes
                elements.update({elem_name : element})
        
        for port in port_map.values():
            if isinstance(port, int) or isinstance(port, float):
                pass
            else:
                nodes.add(port)

        flattened = {"nodes" : nodes, "elements" : elements, "ports" : ports}
        if prefix == "":
            self._flattened_ = flattened
        return flattened





    def compile(self, generics = {}):
        self._flattened_ = self.flatten(generic_map = generics)

        variables = set()
        
        nodes = {}

        for node in self._flattened_["nodes"]:
            V = Symbol(f"V{len(nodes)}", real=True)
            variables.add(V)
            nodes.update({node : Node(V)})

        elements = self._flattened_["elements"]
        ports = self._flattened_["ports"]
        #ports = {name : nodes[port] for name, port in self._flattened_["ports"].items()}
        elementsCurrents = {}
        elementsVoltages = {}

        for name, element in elements.items():

            elementCurrents = {}
            elementVoltages = {}

            for elem_node_name, elem_node in element.nodes.items():

                if elem_node in nodes.keys():
                    elementVoltages.update({elem_node_name : nodes[elem_node]()})
                else:
                    elementVoltages.update({elem_node_name : elem_node})

                I = Symbol(f"I{len(elementsCurrents)}_{len(elementCurrents)}", real=True)
                variables.add(I)
                if elem_node in nodes.keys():
                    nodes[elem_node].addCurrent(I)
                elementCurrents.update({elem_node_name : I})
        
            elementsVoltages.update({name : elementVoltages})
            elementsCurrents.update({name : elementCurrents})

        nodeEquations = {node.equations() for node in nodes.values()}
        nodes = {name : node() for name, node in nodes.items()}

        compiled = {"nodes" : nodes, "nodeEquations" : nodeEquations, "elements" : elements, "voltages" : elementsVoltages, "currents" : elementsCurrents, "variables" : variables, "ports" : ports}
        self._compiled_ = compiled
        return compiled
        



    
    def __call__(self, generics = {}):
        self._compiled_ = self.compile(generics)
        return self._compiled_


#--------------------------------------------------------------------------------