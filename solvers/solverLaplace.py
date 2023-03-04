from sympy import solve, Interval, Symbol, Eq
import sympy as sp
from solvers.inverseLaplace import inverseLaplace
from copy import deepcopy
from solvers.solver import Solver

from solvers.symbols import t, s

import multiprocessing
from tqdm import tqdm
  

def inverseLaplaceProcess(item):
                    
    var, expr = item

    expr_t = inverseLaplace(expr)
    
    for a in sp.preorder_traversal(expr_t):
        if isinstance(a, sp.Heaviside):
            expr_t = expr_t.subs({sp.Heaviside(a.args[0]) : sp.Heaviside(a.args[0], 1.0)})
        elif isinstance(a, sp.DiracDelta):
            if len(a.args) > 1:
                expr_t = expr_t.subs({sp.DiracDelta(a.args[0], a.args[1]) : sp.Float(0.0)})
            else:
                expr_t = expr_t.subs({sp.DiracDelta(a.args[0]) : sp.Float(0.0)})
                
    return {var : expr_t}
    

def solveLaplace(compiled, tmax, tstep = 0.1, debugLog=True):

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

    time = 0

    previous_permutation = set()
        
    while time <= tmax:

        t_start = time
        local_time = 0

        current_solutions = []

        solverType = "Laplace"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        for states, equations, conditions in permutations:

            if states == previous_permutation:
                continue

            equations.extend(circuitEquations)
            
            if debugLog:
                print(states)
                print(equations)
                print(conditions)

            ineqs = lambda sol_t0 : [ineq.subs(sol_t0) for ineq in conditions]

            try:
                sols = solve(equations, variables, dict=True)

                if debugLog:
                    print("-------------------------------------------------")

                for sol in sols:
                    
                    if debugLog:
                        print(sol)
                        print("-------------------------------------------------")
                    
                    sol_t = {}
                    
                                    
                    if debugLog:
                        with multiprocessing.Pool() as pool:
                            for ret in pool.imap_unordered(inverseLaplaceProcess, sol.items(), chunksize=4):
                                sol_t.update(ret)
                                print(list(ret.keys())[0], list(ret.values())[0])
                                print("-----------------")
                    else:
                        with tqdm(total = len(sol.keys())) as pbar:
                            with multiprocessing.Pool() as pool:
                                for ret in pool.imap_unordered(inverseLaplaceProcess, sol.items(), chunksize=4):            
                                    sol_t.update(ret)
                                    pbar.update(1)
                        
                        
                    if debugLog:
                        print("-------------------------------------------------")
                        print(sol_t)
                    
                    #ineqs_ = sp.lambdify(t, ineqs({var : sp.Piecewise((0, abs(expr) < 1e-6), (expr, True)) for var, expr in sol_t.items()}), "numpy")
                    ineqs_ = lambda t_ : ineqs({var : expr.subs({t : t_}) for var, expr in sol_t.items()})

                    if debugLog:
                        print("-------------------------------------------------")
                        print(conditions)
                        print(ineqs_(0.0))
                        print("*****************************************")

                    if all(ineqs_(0.0)):
                        current_solutions.append(
                            (states, sol_t, ineqs_))
                        raise IndexError

            except IndexError:
                break

            finally:
                pass


        try:
            states, sol_t, ineqs_ = current_solutions[0]
            previous_permutation = states

            print(time, "\t\t\t\t\t\t\r", end="")

            while all(ineqs_(local_time)) and time <= tmax:
                local_time += tstep
                time += tstep
                print(time, "\t\t\t\t\t\t\r", end="")
            
            if not all(ineqs_(local_time)):
                print(time, "\t\t\t\t\t\t")

                currStep = tstep / 2
                i = 0
                
                while True:
                    local_time -= currStep
                    time -= currStep
                    
                    if not all(ineqs_(local_time)):
                        if i > 10:
                            break
                    else:
                        if i > 1000:
                            break
                        else:
                            local_time += currStep
                            time += currStep
                    
                    i += 1    
                    currStep = currStep / 2
                    
                    
            
            sol_t0 = {var: eq.subs({t: local_time})
                    for var, eq in sol_t.items()}
            
            for name, _ in states:

                for key, sym in voltages[name].items():
                    elements[name].values.update(
                        {f"{key}_0": sol_t0.get(sym, 0)})

                for key, sym in currents[name].items():
                    elements[name].values.update({f"I_{key}_0": sol_t0.get(sym, 0)})
                    
                elements[name].values.update({f"t_0" : time})


            
            if time <= tmax:
                solutions.append((Interval.Ropen(t_start, time), sol_t, states))
            else:
                solutions.append((Interval(t_start, time), sol_t, states))

    
            print(time, "\t\t\t\t\t\t")
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

        except IndexError:
            print("Index Error")
            break

    return solutions
    