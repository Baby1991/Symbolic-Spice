from copy import deepcopy
from solvers.solver import Solver
from sympy import solve, oo, Interval, EmptySet


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