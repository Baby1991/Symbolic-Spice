from copy import deepcopy
from solvers.solver import Solver
from sympy import solve, oo, Interval, EmptySet


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
                    ineqs = []
                    for state_, ineqs_ in conditions.items():
                        ineqs.extend([ineq.subs(sol) for ineq in ineqs_])

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