from sympy import solve, oo, Interval, Float, simplify, preorder_traversal, Set, Union, EmptySet, Symbol
import sympy as sp

import matplotlib.pyplot as plt
import numpy as np
import itertools
from copy import deepcopy

from circuit import Circuit

Gnd = 0
s = Symbol("s")
t = Symbol("t", positive=True)

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
        Solver.circuits.update({name : circuit})
        return circuit
    
    def __call__():
        return Solver.main
    
    def compile(**values):
        return Solver.main.compile(values)
    

    def solveOP(compiled, debugLog = True):

        compiled = deepcopy(compiled)

        variables        = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements         = compiled["elements"]
        voltages         = compiled["voltages"]
        currents         = compiled["currents"]

        if debugLog:
            print(variables)
            print(circuitEquations)
            print(elements)
            print(voltages)
            print(currents)

        solutions = []

        permutations = itertools.product(*[elements[key].allModes(voltages[key], currents[key]) for key in elements.keys()])

        for perm in permutations:

            equations = list(circuitEquations)
            conditions = []
            states = {}
            for formulaOP, formulaTran, condition, state in perm:
                       
                equations += formulaOP
                conditions += condition
                if state:
                    states.update(state)

            if debugLog:
                print(equations)
                print(conditions)
                print(states)

            sols = solve(equations, variables, dict=True)

            for sol in sols:
                try:

                    if debugLog:
                        print(sol)

                    if any(not node in sol for node in variables):
                        if debugLog:
                            print("Invalid solution")
                        continue

                    ineqs = [ineq.subs(sol) for ineq in conditions]
                    
                    if debugLog:
                        print(ineqs)

                    if all(x == True for x in ineqs):
                        if debugLog:
                            print("Always True")
                        solutions.append((Interval(-oo, oo), sol, states))
                        continue

                    if any(x == False for x in ineqs):
                        if debugLog:
                            print("Always False")
                        continue

                    interval = solve(ineqs).as_set()

                    if debugLog:
                            print(interval)

                    if interval != EmptySet:
                        solutions.append((interval, sol, states))

                except Exception as e:
                    if debugLog:
                        print(e)

            if debugLog:
                print("-------------------------------------")

        return solutions


    
    def solveTran(compiled, tmax, tstep = 0.01, debugLog=True):
        
        compiled = deepcopy(compiled)
        
        variables        = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements         = compiled["elements"]
        voltages         = compiled["voltages"]
        currents         = compiled["currents"]

        """
        if debugLog:
            print(variables)
            print(circuitEquations)
            print(elements)
            print(voltages)
            print(currents)
        """

        solutions = []

        time = 0
        while time <= tmax:
            
            t_start = time
            local_time = 0
            
            current_solutions = []
            
            permutations = itertools.product(*[elements[key].allModes(voltages[key], currents[key]) for key in elements.keys()])
            for perm in permutations:

                equations = list(circuitEquations)
                conditions = []
                states = {}
                names = set()
                
                for formulaOP, formulaTran, condition, (name, state) in perm:
                                    
                    if formulaTran == []:
                        formulaTran = formulaOP
                    equations += formulaTran
                    
                    conditions += condition
                    names.add(name)
                    
                    if state:
                        states.update({name : state})

                if debugLog:
                    print(names)
                    print(equations)
                    print(conditions)
                    print(states)
                
                try:
                    sols = solve(equations, variables, dict=True)
                    
                    for sol in sols:
                        #print(sol)
                        #print("-------------------------------------------------")
                        
                        sol_t = {var : sp.inverse_laplace_transform(eq.apart(s), s, t) for var, eq in sol.items()}
                        #print(sol_t)
                            
                        #print("-------------------------------------------------")
                            
                        sol_t0 = {var : eq.subs({t : local_time}) for var, eq in sol_t.items()}
                        #print(sol_t0)
                        #print("-------------------------------------------------")
                        
                        ineqs = [ineq.subs(sol_t0) for ineq in conditions]
                        #print(ineqs)
                        #print("-------------------------------------------------")
                        
                        if all(ineqs):
                            current_solutions.append((names, states, sol_t, conditions))
                        
                        #print("*****************************************")

                except Exception as e:
                    print(e)
            
            names, states, sol_t, conditions = current_solutions[0]
            print(names, states, sol_t, conditions)
            
            ineqs = [True]
            while all(ineqs) and time <= tmax:
                sol_t0 = {var : eq.subs({t : local_time}) for var, eq in sol_t.items()}
                ineqs = [ineq.subs(sol_t0) for ineq in conditions]
                
                local_time += tstep
                time += tstep
            
            sol_t0 = {var : eq.subs({t : local_time}) for var, eq in sol_t.items()}
            for name in names:
                
                for key, sym in voltages[name].items():
                    elements[name].values.update({f"{key}_0" : sol_t0.get(sym, 0)})
                    
                for key, sym in currents[name].items():
                    elements[name].values.update({f"I_{key}_0" : sol_t0[sym]})
            
            sol_t = {var : eq.subs({t : t - t_start}) for var, eq in sol_t.items()}
            solutions.append((Interval(t_start, time - tstep), sol_t, states))
            
            print(time)
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
                
            """
            
            
                
            """
        
        return solutions
    
    

    def printModel(model, var):
        for interval, solution, state in model:
            print("-------------------------------------")
            if state != "":
                print(state)
            if var is not None:
                print(f"{var} ∈ {interval}")
            print(solution)
            print("-------------------------------------")

        print("***************************************************************************************************************")


def plotMeasurments(solutions, minx, maxx, step, measurments, inputVar):

    max_scale = Interval(minx, maxx)

    for measurment, measurmentName in measurments:

        for interval, solution, state in solutions:
            interval = interval.intersect(max_scale)

            formula = measurment(solution)

            if isinstance(interval, Union):

                intervals = interval.args
                for interval in intervals:
                    start, end = float(interval.start), float(interval.end)
                    numP = int((end - start) / step)
                    xs = list(np.linspace(start, end, numP))
                    if len(xs) < 2:
                        xs =[start, end]
                    ys = [formula.subs(inputVar, x) for x in xs]

                    formula = simplify(formula)

                    for a in preorder_traversal(formula):
                        if isinstance(a, Float):
                            formula = formula.subs(a, round(a, 5))

                    if xs and ys:
                        plt.plot(xs, ys, label=f"{measurmentName} : {repr(formula)}\n{state}")


            elif isinstance(interval, Interval):
                
                start, end = float(interval.start), float(interval.end)
                numP = int((end - start) / step)
                xs = list(np.linspace(start, end, numP))
                if len(xs) < 2:
                    xs =[start, end]
                ys = [formula.subs(inputVar, x) for x in xs]

                formula = simplify(formula)

                for a in preorder_traversal(formula):
                    if isinstance(a, Float):
                        formula = formula.subs(a, round(a, 5))

                if xs and ys:
                    plt.plot(xs, ys, label=f"{measurmentName} : {repr(formula)}\n{state}")

            elif isinstance(interval, Set):
                
                xs = list(interval)
                ys = [formula.subs(inputVar, x) for x in xs]

                formula = simplify(formula)

                for a in preorder_traversal(formula):
                    if isinstance(a, Float):
                        formula = formula.subs(a, round(a, 5))

                if xs and ys:
                    plt.scatter(xs, ys, label=f"{measurmentName} : {repr(formula)}\n{state}")
                    
def plotTranMeasurments(solutions, mint, maxt, step, measurments):
    
    max_scale = Interval(mint, maxt)

    for measurment, measurmentName in measurments:

        for interval, solution, state in solutions:
            interval = interval.intersect(max_scale)

            ts = np.arange(interval.start, interval.end, step)
            
            values = [{var : value.subs({t : time}) for var, value in solution.items()} for time in ts]
            
            ys = [measurment(value) for value in values]
            
            plt.plot(ts, ys, label=f"{measurmentName} : {state}")
                
