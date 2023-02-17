from sympy import solve, oo, Interval, Float, simplify, preorder_traversal, Set, Union, EmptySet
import matplotlib.pyplot as plt
import numpy as np
import itertools

class Solver():

    def solveDC(compiled, debugLog = True):

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
            for formulaDC, formulaAC, condition, state in perm:
                equations += formulaDC
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