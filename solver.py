from sympy import solve, oo, Interval, Float, simplify, preorder_traversal, Set, Union, EmptySet, Symbol
import sympy as sp

import matplotlib.pyplot as plt
import numpy as np
import itertools
from copy import deepcopy

from circuit import Circuit

from component import Component

Gnd = 0
s = Symbol("s")
t = Symbol("t", real=True, positive=True)


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
                
                default = {"equations": element.default_equations(
                    voltages[element_name], currents[element_name]), "conditions": element.default_conditions(voltages[element_name], currents[element_name])}
                
                mode = mode.get(solverType, default)
                elementModes.append({(element_name ,mode_name) : mode})

            allModes.append(elementModes)

        permutations = []
        for perm in itertools.product(*allModes):
            states = set()
            equations = []
            conditions = []
            
            for p in perm:
                for state, eqs in p.items():
                    states.add(state)
                    equations.extend(eqs["equations"])
                    conditions.extend(eqs["conditions"])
                
            permutations.append((states, equations, conditions))
        
        return permutations
    
        

    def solveOP(compiled, debugLog=True):

        compiled = deepcopy(compiled)

        variables = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements = compiled["elements"]
        voltages = compiled["voltages"]
        currents = compiled["currents"]

        if debugLog:
            print(variables)
            print(circuitEquations)
            print(elements)
            print(voltages)
            print(currents)
            print("***************************************")

        solutions = []

        solverType = "OP"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        for states, equations, conditions in permutations:

            equations.extend(circuitEquations)

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

                    if any(type(conditionSet) == list for conditionSet in conditions):

                        for conditionSet in conditions:
                            ineqs = [ineq.subs(sol) for ineq in conditionSet]

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

                    else:
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

    def solveLaplace(compiled, tmax, tstep=0.01, debugLog=True):

        compiled = deepcopy(compiled)

        variables = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements = compiled["elements"]
        voltages = compiled["voltages"]
        currents = compiled["currents"]

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

            solverType = "Laplace"
            permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

            for states, equations, conditions in permutations:

                equations.extend(circuitEquations)
                
                if debugLog:
                    print(states)
                    print(equations)
                    print(conditions)

                try:
                    sols = solve(equations, variables, dict=True)

                    for sol in sols:
                        
                        for key in sol.keys():
                            print(key, sol[key])
                        
                        
                        sol = {var: 0 if abs(eq.subs({s : 1})) < 1e-6 else eq for var, eq in sol.items()}
                        
                        for key in sol.keys():
                            for a in preorder_traversal(sol[key]):
                                if isinstance(a, Float):
                                    if abs(a) < 1:
                                        sol[key] = sol[key].subs({a : 0})
                        
                        sol = {var: sp.simplify(sp.simplify(eq).apart(s)) for var, eq in sol.items()}
                        
                        
                        
                        print(sol)
                        print("-------------------------------------------------")

                        sol_t = {var: sp.re(sp.inverse_laplace_transform(
                            eq, s, t)) for var, eq in sol.items()}
                        
                        print(sol_t)
                        #print("-------------------------------------------------")

                        sol_t0 = {var: eq.subs({t: local_time})
                                  for var, eq in sol_t.items()}
                        
                        #print(sol_t0)
                        #print("-------------------------------------------------")
                        print("*****************************************")

                        ineqs = [ineq.subs(sol_t0) for ineq in conditions]
                        #print(ineqs)
                        #print("-------------------------------------------------")

                        if all(ineqs):
                            current_solutions.append(
                                (states, sol_t, conditions))

                except Exception as e:
                    print(e)
                    
                #print("*****************************************")

            states, sol_t, conditions = current_solutions[0]
            #print(states, sol_t, conditions)

            ineqs = [True]
            while all(ineqs) and time <= tmax:
                sol_t0 = {var: eq.subs({t: local_time})
                          for var, eq in sol_t.items()}
                ineqs = [ineq.subs(sol_t0) for ineq in conditions]

                local_time += tstep
                time += tstep

            sol_t0 = {var: eq.subs({t: local_time})
                      for var, eq in sol_t.items()}
            for name, _ in states:

                for key, sym in voltages[name].items():
                    elements[name].values.update(
                        {f"{key}_0": sol_t0.get(sym, 0)})

                for key, sym in currents[name].items():
                    elements[name].values.update({f"I_{key}_0": sol_t0.get(sym, 0)})

            sol_t = {var: eq.subs({t: t - t_start})
                     for var, eq in sol_t.items()}
            #solutions.append((Interval(t_start, time - tstep), sol_t, states))
            solutions.append((Interval.Ropen(t_start, time), sol_t, states))

            if debugLog:
                print(time)
                print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            else:
                print(f"\r{round(time, 6)}\t", end="")

        return solutions

    def solveACDC(compiled, debugLog=True):
        compiled = deepcopy(compiled)

        variables = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements = compiled["elements"]
        voltages = compiled["voltages"]
        currents = compiled["currents"]

        if debugLog:
            print(variables)
            print(circuitEquations)
            print(elements)
            print(voltages)
            print(currents)
            print("***************************************")


        solverType = "OP"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        opSolution = None

        for states, equations, conditions in permutations:

            equations.extend(circuitEquations)

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

                    if any(type(conditionSet) == list for conditionSet in conditions):

                        for conditionSet in conditions:
                            ineqs = [ineq.subs(sol) for ineq in conditionSet]

                            if debugLog:
                                print(ineqs)

                            if all(x == True for x in ineqs):
                                if debugLog:
                                    print(sol, states)
                                
                                opSolution = (sol, states)

                                continue

                    else:
                        ineqs = [ineq.subs(sol) for ineq in conditions]

                        if debugLog:
                            print(ineqs)

                        if all(x == True for x in ineqs):
                            if debugLog:
                                print(sol, states)
                            
                            opSolution = (sol, states)

                            continue

                except Exception as e:
                    pass
                    if debugLog:
                        print(e)



        sol, states = opSolution                
        for name, _ in states:
            for key, sym in voltages[name].items():
                elements[name].values.update(
                    {f"{key}_0": sol.get(sym, 0)})
            for key, sym in currents[name].items():
                elements[name].values.update({f"I_{key}_0": sol.get(sym, 0)})    
                        
                                    
        solutions = []

        solverType = "AC+DC"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        for states, equations, conditions in permutations:

            equations.extend(circuitEquations)

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

                    if any(type(conditionSet) == list for conditionSet in conditions):

                        for conditionSet in conditions:
                            ineqs = [ineq.subs(sol) for ineq in conditionSet]

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

                    else:
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

    def solveSmallSignal(compiled, debugLog=True):
        compiled = deepcopy(compiled)

        variables = compiled["variables"]
        circuitEquations = compiled["nodeEquations"]
        elements = compiled["elements"]
        voltages = compiled["voltages"]
        currents = compiled["currents"]

        if debugLog:
            print(variables)
            print(circuitEquations)
            print(elements)
            print(voltages)
            print(currents)
            print("***************************************")


        solverType = "OP"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        opSolution = None

        for states, equations, conditions in permutations:

            equations.extend(circuitEquations)

            #if debugLog:
            #    print(equations)
            #    print(conditions)
            #    print(states)

            sols = solve(equations, variables, dict=True)

            for sol in sols:
                try:
                    #if debugLog:
                    #    print(sol)

                    if any(not node in sol for node in variables):
                        #if debugLog:
                        #    print("Invalid solution")
                        continue

                    if any(type(conditionSet) == list for conditionSet in conditions):

                        for conditionSet in conditions:
                            ineqs = [ineq.subs(sol) for ineq in conditionSet]

                            if debugLog:
                                print(ineqs)

                            if all(x == True for x in ineqs):
                                if debugLog:
                                    print(sol, states)
                                
                                opSolution = (sol, states)

                                continue

                    else:
                        ineqs = [ineq.subs(sol) for ineq in conditions]

                        if debugLog:
                            print(ineqs)

                        if all(x == True for x in ineqs):
                            if debugLog:
                                print(sol, states)
                            
                            opSolution = (sol, states)

                            continue

                except Exception as e:
                    pass
                    #if debugLog:
                    #    print(e)



        sol, states = opSolution                
        for name, _ in states:
            for key, sym in voltages[name].items():
                elements[name].values.update(
                    {f"{key}_0": sol.get(sym, 0)})
            for key, sym in currents[name].items():
                elements[name].values.update({f"I_{key}_0": sol.get(sym, 0)})    
                        
        print(elements)     
                        
        solutions = []

        solverType = "SmallSignal"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        for states, equations, conditions in permutations:

            equations.extend(circuitEquations)

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

                    if any(type(conditionSet) == list for conditionSet in conditions):

                        for conditionSet in conditions:
                            ineqs = [ineq.subs(sol) for ineq in conditionSet]

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

                    else:
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


def printModel(model, var):
    for interval, solution, state in model:
        if state != "":
            print(state)
        if var is not None:
            print(f"{var} ∈ {interval}")
        print(solution)
        print("-------------------------------------")

def plotMeasurments(solutions, minx, maxx, step, measurments, inputVar):

    max_scale = Interval(minx, maxx)

    for measurmentx, measurmenty, measurmentName in measurments:

        for interval, solution, states in solutions:
            interval = interval.intersect(max_scale)

            states = {name : state for name, state in states if state != ""}

            formulax = measurmentx.subs(solution)
            formulay = measurmenty.subs(solution)

            if isinstance(interval, Union):

                intervals = interval.args
                for interval in intervals:
                    start, end = float(interval.start), float(interval.end)
                    numP = int((end - start) / step)
                    ts = list(np.linspace(start, end, numP))
                    if len(ts) < 2:
                        ts = [start, end]
                        
                    #xs = [formulax.subs(inputVar, t) for t in ts]
                    #ys = [formulay.subs(inputVar, t) for t in ts]
                    values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                    formulax = simplify(formulax)
                    formulay = simplify(formulay)

                    for a in preorder_traversal(formulax):
                        if isinstance(a, Float):
                            formulax = formulax.subs(a, round(a, 5))
                    for a in preorder_traversal(formulay):
                        if isinstance(a, Float):
                            formulay = formulay.subs(a, round(a, 5))

                    #if xs and ys:
                    #    plt.plot(
                    #        xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                    if len(values.items()) > 2:
                        plt.plot(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                        )
                    elif len(values.items()) == 1:
                        plt.scatter(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")

            elif isinstance(interval, Interval):

                start, end = float(interval.start), float(interval.end)
                numP = int((end - start) / step)
                ts = list(np.linspace(start, end, numP))
                if len(ts) < 2:
                    ts = [start, end]
                    
                #xs = [formulax.subs(inputVar, t) for t in ts]
                #ys = [formulay.subs(inputVar, t) for t in ts]
                values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                formulax = simplify(formulax)
                formulay = simplify(formulay)

                for a in preorder_traversal(formulax):
                        if isinstance(a, Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in preorder_traversal(formulay):
                    if isinstance(a, Float):
                        formulay = formulay.subs(a, round(a, 5))

                #if xs and ys:
                #    plt.plot(
                #    xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                if len(values.items()) > 2:
                    plt.plot(
                        values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                    )
                elif len(values.items()) == 1:
                    plt.scatter(
                        values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                    

            elif isinstance(interval, Set):

                ts = list(interval)
                
                values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}
                #xs = [formulax.subs(inputVar, t) for t in ts]
                #ys = [formulay.subs(inputVar, t) for t in ts]

                formulax = simplify(formulax)
                formulay = simplify(formulay)

                for a in preorder_traversal(formulax):
                        if isinstance(a, Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in preorder_traversal(formulay):
                    if isinstance(a, Float):
                        formulay = formulay.subs(a, round(a, 5))

                #if xs and ys:
                #    plt.scatter(
                #    xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                if values:
                    plt.scatter(
                        values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")


def plotTranMeasurments(solutions, mint, maxt, step, measurments):

    max_scale = Interval(mint, maxt)

    for measurment, measurmentName in measurments:

        for interval, solution, states in solutions:
            interval = interval.intersect(max_scale)

            states = {name : state for name, state in states if state != ""}

            if interval != EmptySet:
                ts = np.arange(interval.start, interval.end, step)

                values = [
                    {var: value.subs({t: time}) for var, value in solution.items()} for time in ts]
                
                formula = simplify(measurment.subs(solution))
                for a in preorder_traversal(formula):
                    if isinstance(a, Float):
                        formula = formula.subs(a, round(a, 5))

                ys = [measurment.subs(value) for value in values]

                plt.plot(ts, ys, label=f"{measurmentName} : {repr(formula)}\n{states}")
