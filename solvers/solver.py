import itertools
from circuit.circuit import Circuit

Gnd = 0

class Solver():

    circuits = {}
    main = None

    def setMain(name):
        Solver.main = Solver.circuits[name]
        return Solver.main

    def Circuit(name):
        circuit = Circuit()
        if Solver.circuits == {}:
            Solver.main = circuit
        Solver.circuits.update({name: circuit})
        return circuit

    def __call__():
        return Solver.main

    def compile(**values):
        return Solver.main.compile(values)

    def allElementPermutations(elements, voltages, currents, solverType):
        allModes = []
        
        for element_name, element in elements.items():

            elementModes = []

            modes = element.allModes(
                voltages[element_name], currents[element_name])
            for mode_name, mode in modes.items():
                mode = mode.get(solverType, mode["OP"])
                elementModes.append({(element_name ,mode_name) : mode})

            allModes.append(elementModes)

        permutations = []
        for perm in itertools.product(*allModes):
            states = set()
            equations = []
            conditions = {}
            
            for p in perm:
                for state, eqs in p.items():
                    states.add(state)
                    equations.extend(eqs["equations"])
                    if eqs["conditions"] != []:
                        conditions.update({state : eqs["conditions"]})
                
            permutations.append((states, equations, conditions))
        
        return permutations
    
    
    
    


          