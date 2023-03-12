from sympy import Symbol
from circuit.node import Node
from copy import deepcopy
import re
from pprint import pformat


class Circuit:

    def __init__(self):
        self._constants_ = {}
        self._generics_ = {}

        self._nodes_ = set()

        self._elements_ = {}

        self._flattened_ = {}
        self._compiled_ = {}

    def split(names):
        names = re.split("\W+", names)

        nodes = list()
        for name in names:
            nodes.append(name)

        if len(nodes) == 0:
            return None
        elif len(nodes) == 1:
            return nodes[0]
        else:
            return nodes

    def compileSubstitutions(generics, constants, values, max_recur = 16):
        substitutions = {}

        for name, value in values.items():
            generics[name]["val"] = value

        for generic in generics.values():
            substitutions.update({generic["sym"]: generic["val"]})

        recur = 0

        while any([const.atoms(Symbol) != set() for const in constants.values()]):
            for name, const in constants.items():
                try:
                    sub = const.subs(substitutions)
                    constants.update({name: sub})
                except AttributeError:
                    pass 

            if recur > max_recur:
                #print("Max Recursions Exceded")
                break
            else:
                recur += 1

        substitutions.update(constants)
        
        return substitutions

    def constant(self, name, value):
        if name in self._constants_:
            raise Exception("Constant Already Exists")
        id = f"C{len(self._constants_)}"
        sym = Symbol(id, real=True)
        constant = {sym: value}
        self._constants_.update(constant)
        return sym

    def generic(self, name, value):
        if name in self._generics_:
            raise Exception("Generic Already Exists")
        id = f"G{len(self._generics_)}"
        sym = Symbol(id, real=True)
        generic = {name: {"sym": sym, "val": value}}
        self._generics_.update(generic)
        return sym

    def element(self, *elements):
        elemSet = {}
        for element in elements:

            if element.name in self._elements_.keys():
                raise Exception("Element Already Exists")

            if isinstance(element, Subcircuit):
                # print("Subcircuit")
                # print(element.name)
                # print(element.values)

                new_nodes = {element.nodes[node] if node in element.nodes.keys(
                ) else f"{element.name}_{node}" for node in element.circuit._nodes_}
                new_nodes = {node for node in new_nodes if type(node) == str}
                self._nodes_.update(new_nodes)

                substitutions = Circuit.compileSubstitutions(element.circuit._generics_, element.circuit._constants_, element.values)

                for elem_name, elem in element.circuit._elements_.items():

                    elem_name = f"{element.name}_{elem_name}"

                    elem_nodes = {}
                    for name, node in elem.nodes.items():
                        if node in element.nodes.keys():
                            elem_nodes.update({name: element.nodes[node]})
                        elif type(node) == str:
                            elem_nodes.update({name: f"{element.name}_{node}"})
                        else:
                            elem_nodes.update({name: node})

                    elem_values = elem.values

                    for name, value in elem_values.items():
                        try:
                            elem_values.update({name : value.subs(substitutions)})
                        except AttributeError:
                            pass    

                    elem.name = elem_name
                    elem.nodes = elem_nodes
                    elem.values = elem_values

                    #print(elem)

                    self._elements_.update({elem_name: elem})
                    elemSet.update({elem_name: elem})

            else:
                # print(element)

                elem = {element.name: element}

                self._nodes_.update(
                    {node for node in element.nodes.values() if type(node) == str})

                self._elements_.update(elem)

                elemSet.update(elem)
            # print("---------------------------")

        # print("***********************************************")

        return elemSet


    def compile(self, values={}):

        circuit = self(name="", nodes=set(), **values)

        variables = set()

        nodes = {}

        for node in circuit["nodes"]:
            V = Symbol(f"V{len(nodes)}", real=True)
            variables.add(V)
            nodes.update({node: Node(V)})

        elements = circuit["elements"]

        elementsCurrents = {}
        elementsVoltages = {}

        for name, element in elements.items():

            elementCurrents = {}
            elementVoltages = {}

            for elem_node_name, elem_node in element.nodes.items():

                if elem_node in nodes.keys():
                    elementVoltages.update(
                        {elem_node_name: nodes[elem_node]()})
                else:
                    elementVoltages.update({elem_node_name: elem_node})

                I = Symbol(
                    f"I{len(elementsCurrents)}_{len(elementCurrents)}", real=True)
                variables.add(I)
                if elem_node in nodes.keys():
                    nodes[elem_node].addCurrent(I)
                elementCurrents.update({elem_node_name: I})

            elementsVoltages.update({name: elementVoltages})
            elementsCurrents.update({name: elementCurrents})

        nodeEquations = [node.equations() for node in nodes.values()]
        nodes = {name: node() for name, node in nodes.items()}

        compiled = {"nodes": nodes, "nodeEquations": nodeEquations, "elements": elements,
                    "voltages": elementsVoltages, "currents": elementsCurrents, "variables": variables}
        self._compiled_ = compiled
        return compiled

    def __repr__(self) -> str:
        return pformat({"nodes": self._nodes_, "elements": self._elements_})

    def __call__(self, name="", nodes=set(), **values):
        if name == "" and nodes == set():
            
            substitutions = Circuit.compileSubstitutions(self._generics_, self._constants_, values)
            
            for elem_name, elem in self._elements_.items():
                    for name, value in elem.values.items():
                        try:
                            sub = value.subs(substitutions)
                            elem.values.update({name : sub})
                            elem.values.update({name : float(sub)})
                            
                        except AttributeError:
                            pass    
                        except TypeError:
                            pass
                        
            return {"nodes": self._nodes_, "elements": self._elements_}
        
        elif name != "" and nodes != set():
            return Subcircuit(name, deepcopy(self), nodes, values)
        else:
            raise Exception("Bad Call")

# --------------------------------------------------------------------------------


class Subcircuit:

    def __init__(self, name, circuit, nodes, values):
        self.name = name
        self.circuit = circuit
        self.nodes = nodes
        self.values = values
