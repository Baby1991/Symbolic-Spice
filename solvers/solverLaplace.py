from sympy import solve, Interval, Symbol, Eq
import sympy as sp
from solvers.inverseLaplace import myFunctions, IDLT0, inverseLaplaceNew, bilinearDiscretify, Delta, U, __inverseLaplaceTransforms__
from copy import deepcopy
from solvers.solver import Solver

import lcapy

from solvers.symbols import t, s

import multiprocessing
from tqdm import tqdm


def inverseLaplaceProcess(item):
    var, expr = item
    
    try:
        expr_t = inverseLaplaceNew(expr)
    except AttributeError:
        expr_t = sp.inverse_laplace_transform(expr, s, t)        
    
    for a in sp.preorder_traversal(expr_t):
        if isinstance(a, sp.Heaviside):
            expr_t = expr_t.subs({sp.Heaviside(a.args[0]) : U(a.args[0])})
            
        elif isinstance(a, sp.DiracDelta):
            if len(a.args) > 1:
                expr_t = expr_t.subs({sp.DiracDelta(a.args[0], a.args[1]) : Delta(a.args[0])})
            else:
                expr_t = expr_t.subs({sp.DiracDelta(a.args[0]) : Delta(a.args[0])})
        
    return (var, expr_t)
        

def solveLaplace(compiled, tmax, tstep = 0.1, workerN = 4, debugLog=0):

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
    failed_states = set()

    solvedLaplace = deepcopy(__inverseLaplaceTransforms__)

    time = 0
        
    while time <= tmax:

        t_start = time
        
        time += tstep
        local_time = tstep

        current_solutions = []

        solverType = "Laplace"
        permutations = Solver.allElementPermutations(elements, voltages, currents, solverType)

        for states, equations, conditions in permutations:
            
            if states.intersection(failed_states):
                continue

            equations.extend(circuitEquations)
            
            if debugLog:
                print({(name, state) for name, state in states if state != ""})
                print(equations)
                print(conditions)
     
            importantVariables = set()
            for conds in conditions.values():
                for cond in conds:
                    importantVariables.update(cond.atoms(sp.Symbol))

            if debugLog:
                print(importantVariables)

            try:
                sols = solve(equations, variables, dict=True)

                if debugLog:
                    print("-------------------------------------------------")

                for sol in sols:
                    
                    """
                    if debugLog:
                        print(sol)
                    
                    for var, expr in deepcopy(sol).items():
                        atoms = expr.atoms(Symbol).difference({s})
                        if atoms:
                            for sym in atoms:
                                expr = expr.subs(sym, sp.Float(0.0))
                                sol[sym] = sp.Float(0.0)
                            sol[var] = expr
                    """     
                    
                    if debugLog:
                        print(sol)
                        print("-------------------------------------------------")                    

                    sol_t0 = {var : IDLT0(expr) for var, expr in sol.items() if var in importantVariables}

                    conditions_t0 = {state : [cond.subs(sol_t0) for cond in conds] for state, conds in conditions.items()}

                    if debugLog:
                        print(sol_t0)
                        print(conditions)
                        print(conditions_t0)
                        print("*****************************************")

                    if all(all(conds) for conds in conditions_t0.values()):
                        current_solutions.append(
                            (states, sol, conditions))
                        raise IndexError

            except IndexError:
                break

            finally:
                pass

        #print(current_solutions)

        try:
            states, sol, conditions = current_solutions[0]

            sol_t = {}
                        
            for item in sol.items():
                if debugLog > 1:
                    print(*item)

                var, expr = item
                
                for solvedExpr, solvedExpr_t in solvedLaplace.items():
                    ratio = expr / solvedExpr
                    if ratio.is_number:
                        sol_t[var] = ratio * solvedExpr_t
                        continue
                
                item_t = inverseLaplaceProcess(item)
                
                var, expr_t = item_t
                
                solvedLaplace[expr] = expr_t
                
                if debugLog > 1:
                    print(expr_t)
                
                sol_t[var] = expr_t
                
                
                    
            ineqs = {state : [sp.lambdify(t, cond.subs(sol_t), myFunctions) for cond in conds] for state, conds in conditions.items()}
            ineqs_ = lambda t_ : {state : [cond(t_) for cond in conds] for state, conds in ineqs.items()}
            
            
            print("vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv")
            print(time, "\t\t\t\t\t\t\r", end="")

            while all(all(conds) for conds in ineqs_(local_time).values()) and time <= tmax:
                local_time += tstep
                time += tstep
                print(time, "\t\t\t\t\t\t\r", end="")
            
            if not all(all(conds) for conds in ineqs_(local_time).values()):
                print(time, "\t\t\t\t\t\t")

                currStep = tstep / 2
                i = 0
                p = 0
                
                while True:
                    if local_time > currStep:
                        local_time -= currStep
                        time -= currStep
                        
                        if not all(all(conds) for conds in ineqs_(local_time).values()):
                            if i > 10:
                                break
                        else:
                            if i > 1000:
                                break
                            else:
                                local_time += currStep
                                time += currStep
                        
                        i += 1
                    else:
                        p += 1
                        if p > 10:
                            break
                            
                    currStep = currStep / 2
                    
                failed_states = set()
                for state, conditions in ineqs_(local_time).items():
                    if not any(conditions):
                        failed_states.add(state)

                if debugLog:
                    print("Changed state: ", failed_states)                    
                    
            
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
            print(218, "Index Error")
            break

    return solutions
    