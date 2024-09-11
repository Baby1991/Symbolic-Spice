import sympy as sp
import matplotlib.pyplot as plt
import numpy as np

def printModel(model, var, measurments = []):
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
            

def plotMeasurments(solutions, inputVar, minVar, maxVar, step, measurments, ax = None):

    max_scale = sp.Interval(minVar, maxVar)

    if ax is None:
        plt.figure()


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
                        
    if ax is None:
        plt.grid()
