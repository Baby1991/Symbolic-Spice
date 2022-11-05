from sympy import Symbol, Eq, solve, Interval, oo, EmptySet, Float, simplify, preorder_traversal, Set
import itertools
import matplotlib.pyplot as plt
import numpy as np

class Node:
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.currents = []

    def addCurrent(self, symbol):
        self.currents.append(symbol)

    def __call__(self):
        return self.symbol

    def equations(self):
        eq = 0
        for current in self.currents:
            eq += current
        return Eq(eq, 0)


class Circuit:

    def __init__(self):
        self.nodes    = []
        self.voltages = []
        self.currents = []
        self.elements = {}


    def addNode(self):
        id = len(self.nodes)
        V = Symbol(f"V_{id}", real=True)
        node = Node(V)
        self.voltages.append(V)
        self.nodes.append(node)
        return node

    def addNodes(self, num):
        return [self.addNode() for _ in range(num)]


    def addCurrent(self):
        id = len(self.currents)
        current = Symbol(f"I_{id}", real=True)
        self.currents.append(current)
        return current

    def addCurrents(self, num):
        return [self.addCurrent() for _ in range(num)]


    def addElement(self, element):
        Is = []

        for node in element.nodes:
            I = self.addCurrent()
            if isinstance(node, Node):
                node.addCurrent(I)
            Is.append(I)

        element.setCurrents(Is)
        self.elements[element.name]= element
        return element

    def addElements(self, elements):
        return [self.addElement(element) for element in elements]

    def currentThroughElement(self, name, id=0):
        return self.elements[name].current(id)



    def solve(self, debugLog = True):

        solutions = []
        permutations = itertools.product(*[elem.allModes() for elem in self.elements.values()])

        circuit = [node.equations() for node in self.nodes]
        variables = self.voltages + self.currents

        for perm in permutations:

            equations = circuit + []
            conditions = []
            states = ""
            for formula, condition, state in perm:
                equations += formula
                conditions += condition
                if state:
                    states += state + ", "
                
            states = states[:-2]

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

#--------------------------------------------------------------------------------
#--------------------------------------------------------------------------------

def printCircuitSolution(solutions, var=None):
    for interval, solution, state in solutions:
        print("-------------------------------------")
        if state != "":
            print(state)
        if var is not None:
            print(f"{var} ∈ {interval}")
        print(solution)
        print("-------------------------------------")

#--------------------------------------------------------------------------------

def plotMeasurments(solutions, minx, maxx, step, measurments, inputVar):

    max_scale = Interval(minx, maxx)

    for measurment, measurmentName in measurments:

        for interval, solution, state in solutions:
            interval = interval.intersect(max_scale)

            formula = measurment(solution)

            if isinstance(interval, Interval):
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