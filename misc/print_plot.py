import sympy as sp
from solvers.symbols import t
import matplotlib.pyplot as plt
import numpy as np

def printModel(model, var = t, important = None):
    if important == None:
        for interval, solution, state in model:
            if state != "":
                print(state)
            #if var is not None:
            print(f"{var} ∈ {interval}")
            print(sp.latex(solution))
            print("-------------------------------------")
    else:
        for interval, solution, state in model:
            if state != "":
                print(state)
            #if var is not None:
            print(f"{var} ∈ {interval}")
            print({imp : imp.subs(solution) for imp in important})
            print({imp : imp.subs(solution).subs({var : interval.start}) for imp in important})
            print({imp : imp.subs(solution).subs({var : interval.end}) for imp in important})
            print("-------------------------------------")
            

def plotMeasurments(solutions, minx, maxx, step, measurments, inputVar, ax = None):

    max_scale = sp.Interval(minx, maxx)

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
                        
                    #xs = [formulax.subs(inputVar, t) for t in ts]
                    #ys = [formulay.subs(inputVar, t) for t in ts]
                    values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                    formulax = sp.simplify(formulax)
                    formulay = sp.simplify(formulay)

                    for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                    for a in sp.preorder_traversal(formulay):
                        if isinstance(a, sp.Float):
                            formulay = formulay.subs(a, round(a, 5))

                    #if xs and ys:
                    #    plt.plot(
                    #        xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                    
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
                    
                #xs = [formulax.subs(inputVar, t) for t in ts]
                #ys = [formulay.subs(inputVar, t) for t in ts]
                values = {formulax.subs(inputVar, t) : formulay.subs(inputVar, t) for t in ts}

                formulax = sp.simplify(formulax)
                formulay = sp.simplify(formulay)

                for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in sp.preorder_traversal(formulay):
                    if isinstance(a, sp.Float):
                        formulay = formulay.subs(a, round(a, 5))

                #if xs and ys:
                #    plt.plot(
                #    xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
                
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
                #xs = [formulax.subs(inputVar, t) for t in ts]
                #ys = [formulay.subs(inputVar, t) for t in ts]

                formulax = sp.simplify(formulax)
                formulay = sp.simplify(formulay)

                for a in sp.preorder_traversal(formulax):
                        if isinstance(a, sp.Float):
                            formulax = formulax.subs(a, round(a, 5))
                for a in sp.preorder_traversal(formulay):
                    if isinstance(a, sp.Float):
                        formulay = formulay.subs(a, round(a, 5))

                #if xs and ys:
                #    plt.scatter(
                #    xs, ys, label=f"{measurmentName} : {repr(formulay)}, {repr(formulax)}\n{states}")
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

    for measurment, measurmentName in measurments:

        all_ys = {}

        for interval, solution, states in solutions:
            interval = interval.intersect(max_scale)

            states = {name : state for name, state in states if state != ""}

            if interval != sp.EmptySet:
                #ts = np.arange(float(interval.start), float(interval.end), float(step))
                ts = np.linspace(float(interval.start), float(interval.end), int(np.ceil(float((interval.end - interval.start) / step))))
                
                measurment_ = measurment.subs(solution)                
                #measurmentFunc = sp.lambdify(t, measurment_, "numpy")
                measurmentFunc = lambda t_ : measurment_.subs({t : t_})
                
                ys = {
                    t_ : measurmentFunc(t_ - float(interval.start)) for t_ in ts
                }
                
                #formula = simplify(measurment_.subs({t : t - interval.start}))
                formula = sp.simplify(measurment_)
                
                formula = formula.subs({sp.Heaviside(t, 1.0) : 1.0})
                formula = formula.subs({1.0 : 1})
                
                for a in sp.preorder_traversal(formula):
                    if isinstance(a, sp.Float):
                        formula = formula.subs(a, round(a, 5))
                    elif isinstance(a, sp.Heaviside):
                        formula = formula.subs({sp.Heaviside(a.args[0], 1.0) : sp.Heaviside(a.args[0])})
                        
                            
                                

                #for key, val in all_ys.items():
                #    if abs((interval.start - step) - key) < step/2 or abs((interval.end + step) - key) < step/2:
                #        ys.update({key : val})
                        
                ts = sorted(list(ys.keys()))
                ys = {t_ : ys[t_] for t_ in ts}
                
                if ax is not None:
                    ax.plot(ys.keys(), ys.values(), label=f"{measurmentName} : ${sp.latex(formula)}$\n{states}")
                else:
                    plt.plot(ys.keys(), ys.values(), label=f"{measurmentName} : ${sp.latex(formula)}$\n{states}")
                
                all_ys.update(ys)