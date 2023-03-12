import sympy as sp
from solvers.symbols import t, t0
from solvers.inverseLaplace import myFunctionsReal
import matplotlib.pyplot as plt
import numpy as np

def printModel(model, var = t, measurments = []):
    if measurments == []:
        for interval, solution, states in model:
            print({(name, state) for name, state in states if state != ""})
            #if var is not None:
            print(f"{var} ∈ {interval}")
            print(solution)
            print("-------------------------------------")
    else:
        for interval, solution, states in model:
            print({(name, state) for name, state in states if state != ""})
            #if var is not None:
            print(f"{var} ∈ {interval}")
            for expr in measurments:
                print(expr, " : ")
                sp.pprint(sp.simplify(expr.subs(solution)))
            print("-------------------------------------")
            

def plotMeasurments(solutions, mint, maxt, step, measurments, inputVar, ax = None):

    max_scale = sp.Interval(mint, maxt)

    for measurmentx, measurmenty, measurmentName in measurments:

        for interval, solution, states in solutions:
            interval = interval.intersect(max_scale)

            states = {name : state for name, state in states if state != ""}

            formulax = measurmentx.subs(solution)
            formulay = measurmenty.subs(solution)

            if isinstance(interval, sp.Union):

                intervals = interval.args
                for interval in intervals:
                    start, end = float(interval.start), float(interval.end)
                    numP = int((end - start) / step)
                    ts = list(np.linspace(start, end, numP))
                    if len(ts) < 2:
                        ts = [start, end]
                    
                    values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                    formulax = sp.simplify(formulax)
                    formulay = sp.simplify(formulay)

                    for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                    for a in sp.preorder_traversal(formulay):
                        if isinstance(a, sp.Float):
                            formulay = formulay.subs(a, round(a, 5))

                    
                    if ax is not None:
                        if len(values.items()) > 2:
                            ax.plot(
                                values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                            )
                        elif len(values.items()) == 1:
                            ax.scatter(
                                values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                    else:
                        if len(values.items()) > 2:
                            plt.plot(
                                values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                            )
                        elif len(values.items()) == 1:
                            plt.scatter(
                                values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")

            elif isinstance(interval, sp.Interval):

                start, end = float(interval.start), float(interval.end)
                numP = int((end - start) / step)
                ts = list(np.linspace(start, end, numP))
                if len(ts) < 2:
                    ts = [start, end]
                    
                values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                formulax = sp.simplify(formulax)
                formulay = sp.simplify(formulay)

                for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in sp.preorder_traversal(formulay):
                    if isinstance(a, sp.Float):
                        formulay = formulay.subs(a, round(a, 5))

                
                if ax is not None:
                    if len(values.items()) > 2:
                        ax.plot(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                        )
                    elif len(values.items()) == 1:
                        ax.scatter(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                else:
                    if len(values.items()) > 2:
                        plt.plot(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}"
                        )
                    elif len(values.items()) == 1:
                        plt.scatter(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                    
                
                    

            elif isinstance(interval, sp.Set):

                ts = list(interval)
                
                values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                formulax = sp.simplify(formulax)
                formulay = sp.simplify(formulay)

                for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in sp.preorder_traversal(formulay):
                    if isinstance(a, sp.Float):
                        formulay = formulay.subs(a, round(a, 5))

                
                if ax is not None:
                    if values:
                        ax.scatter(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                else:
                    if values:
                        plt.scatter(
                            values.keys(), values.values(), label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")


def plotTranMeasurments(solutions, mint, maxt, step, measurments, ax=None):

    max_scale = sp.Interval(mint, maxt)

    for measurmentx, measurmenty, measurmentName in measurments:

        all_ys = {}

        for interval_, solution, states in solutions:
            interval = interval_.intersect(max_scale)

            states = {name : state for name, state in states if state != ""}

            if interval != sp.EmptySet:
                
                ts = np.linspace(float(interval.start), float(interval.end), int(np.ceil(float((interval.end - interval.start) / step))))
                
                formulax = measurmentx.subs(solution)
                formulay = measurmenty.subs(solution)

                formulax = formulax.subs(t0, t + float(interval_.start))
                formulay = formulay.subs(t0, t + float(interval_.start))
                
                #print(formulax, formulay)
                
                valx = sp.lambdify(t, formulax, [myFunctionsReal, "numpy"])
                valy = sp.lambdify(t, formulay, [myFunctionsReal, "numpy"])
                
                values = {valx(t_ - float(interval_.start)) : valy(t_ - float(interval_.start)) for t_ in ts}
                
                formulax = sp.simplify(formulax)
                formulay = sp.simplify(formulay)
                
                """
                formula = formula.subs({sp.Heaviside(t, 1.0) : 1.0})
                formula = formula.subs({1.0 : 1})
                
                for a in sp.preorder_traversal(formula):
                    if isinstance(a, sp.Float):
                        formula = formula.subs(a, round(a, 5))
                    elif isinstance(a, sp.Heaviside):
                        formula = formula.subs({sp.Heaviside(a.args[0], 1.0) : sp.Heaviside(a.args[0])})
                """     
                        
                xs = sorted(list(values.keys()))
                values = {x : values[x] for x in xs}
                
                if ax is not None:
                    ax.plot(values.keys(), values.values(), label=f"{measurmentName} : (${sp.latex(formulax)}$, ${sp.latex(formulay)}$)\n{states}")
                else:
                    plt.plot(values.keys(), values.values(), label=f"{measurmentName} : (${sp.latex(formulax)}$, ${sp.latex(formulay)}$)\n{states}")
                
                all_ys.update(values)