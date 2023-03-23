import sympy as sp
from copy import deepcopy

import lcapy

if __name__ == "__main__":
    from symbols import *
else:
    from solvers.symbols import *

t0 = sp.Symbol("t_0", real=True, positive=True)


class U(sp.Function):
    @classmethod
    def eval(cls, t):
        if t.is_number:
            return 1 if t >= 0 else 0

    def _latex(self, printer):
        t, = self.args
        _t = printer._print(t)
        return r'u(%s)' % (_t)

class Delta(sp.Function):
    @classmethod
    def eval(cls, t):
        if t.is_number:
            return sp.oo if t == 0 else 0

    def _latex(self, printer):
        t, = self.args
        _t = printer._print(t)
        return r'\delta(%s)' % (_t)


myFunctions = {"Delta": lambda t: sp.oo if t == 0 else 0, "U": lambda t: 1 if t >= 0 else 0,
               "UnitStep": lambda n: 1 if n >= 0 else 0, "UnitImpulse": lambda n: 1 if n == 0 else 0}
myFunctionsReal = {"Delta": lambda t: 1 if abs(
    t) <= 1e-6 else 0, "U": lambda t: 1 if t >= 0 else 0}



__inverseLaplaceTransforms__ = {1/s: U(t), 1/s**2: t * U(t),
                                1/(1 + s**2): sp.sin(t) * U(t), s/(1 + s**2): sp.cos(t) * U(t)}



def Laplace(x, t0=0):

    try:
        func = x.subs({t: t + t0}) * sp.Heaviside(t)
    except AttributeError:
        func = x * sp.Heaviside(t)

    return sp.laplace_transform(func, t, s, noconds=True)


def inverseLaplace(exp, debug=False):
    exp = sp.expand(exp)

    match(type(exp)):

        case sp.Float:
            exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))

        case sp.Integer:
            exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))

        case sp.Add:
            exp_t = 0
            for x in exp.args:
                exp_t += inverseLaplace(x, debug=debug)

        case sp.Pow:
            numer, denom = exp.as_numer_denom()
            denom = sp.factor(denom)

            if isinstance(denom, sp.Mul):
                for x in denom.args:
                    if isinstance(x, sp.Add):
                        for y in x.args:
                            if isinstance(y, sp.Float):
                                if abs(y) < 1.0:
                                    denom /= y

            for x in sp.preorder_traversal(denom):
                if isinstance(x, sp.Float):
                    if sp.Integer(x) == x:
                        denom = denom.subs({x: sp.Integer(x)})

            if abs(numer - 1) < 1e-6:
                exp = (numer / denom).apart(s)
                if type(exp) == sp.Add:
                    exp_t = inverseLaplace(exp, debug=debug)
                else:
                    exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))

            else:
                print(numer, type(numer))
                raise Exception("Unexpected Pow")

        case sp.Mul:
            numer, denom = exp.as_numer_denom()
            denom = sp.factor(denom)

            diff = 0
            mul = 1
            shift = 0

            if type(denom) == sp.Mul:
                for n in deepcopy(denom).args:
                    match type(n):
                        case sp.exp:
                            shift -= n.args[0] / s
                            denom /= n
                        # case _:
                        #    print(n, type(n))
                        #    raise Exception("type(n) Unexpected")

            if type(numer) == sp.Mul:
                for n in numer.args:
                    if n.is_number:
                        mul *= n
                    else:
                        match type(n):
                            case sp.Symbol:
                                diff += 1
                            case sp.Pow:
                                diff += n.args[1]
                            case sp.exp:
                                shift += n.args[0] / s
                            case _:
                                print(n, type(n))
                                raise Exception("type(n) Unexpected")
            else:
                if numer.is_number:
                    mul *= numer
                else:
                    match type(numer):
                        case sp.Symbol:
                            diff += 1
                        case sp.Pow:
                            diff += numer.args[1]
                        case sp.exp:
                            shift += numer.args[0] / s
                        case _:
                            print(numer, type(numer))
                            raise Exception("type(n) Unexpected")

            match type(denom):
                case sp.Symbol:
                    if diff > 0:
                        diff -= 1
                        denom = 1
                case sp.Pow:
                    if diff > 0:
                        if diff > denom.args[1]:
                            denom = 1
                            diff -= denom.args[1]
                        elif diff == denom.args[1]:
                            denom = 1
                            diff = 0
                        else:
                            denom /= sp.Pow(s, diff)
                            diff = 0
                case sp.Mul:
                    for a in deepcopy(denom).args:
                        match type(a):
                            case sp.Symbol:
                                if diff > 0:
                                    diff -= 1
                                    denom /= a
                            case sp.Pow:
                                if diff > 0:
                                    if diff > a.args[1]:
                                        denom = denom.subs({a: 1})
                                        diff -= a.args[1]
                                    elif diff == a.args[1]:
                                        denom = denom.subs({a: 1})
                                        diff = 0
                                    else:
                                        denom = denom.subs(
                                            {a: a / sp.Pow(s, diff)})
                                        diff = 0
                            case sp.Float:
                                # pass
                                denom /= a
                                mul /= a
                            case sp.Add:
                                pass
                            case sp.Mul:
                                pass
                            case _:
                                print(a, type(a))
                                raise Exception("type(n) Unexpected")

                case sp.Add:
                    pass

                case _:
                    print(denom, type(denom))
                    raise Exception("type(n) Unexpected")

            if diff > 0:
                for i in range(diff, -1, -1):
                    try:
                        exp_ = ((s ** i) * mul / denom).apart(s)

                        if type(exp_) == sp.Add:
                            exp_t = inverseLaplace(exp_, debug=debug)
                        else:
                            exp_t = sp.re(
                                sp.inverse_laplace_transform(exp_, s, t))

                        exp_t = sp.diff(exp_t, t, diff - i)
                        exp_t = exp_t.subs({t: t + shift}) * \
                            sp.Heaviside(t + shift)

                        break
                    except Exception:
                        continue
            else:
                exp = (mul / denom).apart(s)

                if type(exp) == sp.Add:
                    exp_t = inverseLaplace(exp, debug=debug)
                else:

                    if isinstance(denom, sp.Mul):
                        for x in denom.args:
                            if isinstance(x, sp.Add):
                                for y in x.args:
                                    if isinstance(y, sp.Float):
                                        if abs(y) < 1.0:
                                            denom /= y
                    else:
                        if isinstance(denom, sp.Add):
                            for y in denom.args:
                                if isinstance(y, sp.Float):
                                    if abs(y) < 1.0:
                                        denom /= y

                    for x in sp.preorder_traversal(denom):
                        if isinstance(x, sp.Float):
                            if abs(sp.Integer(x) - x) < 1e-9:
                                denom = denom.subs({x: sp.Integer(x)})

                    exp_t = sp.re(
                        mul * sp.inverse_laplace_transform(1 / denom, s, t))

                exp_t = exp_t.subs({t: t + shift}) * sp.Heaviside(t + shift)

        case _:
            print(exp, type(exp))
            raise Exception("type(exp) Unexpected")

    return exp_t


def IDLT0(F):
    return sp.limit(s * F, s, sp.oo)

def IDZT0(expr_z):
    return sp.limit(expr_z, z, sp.oo)
    
def bilinearDiscretify(expr, ts=1):
    expr = lcapy.expr(str(expr))
    expr_z = expr.bilinear_transform().subs(dt, ts).simplify().sympy
    return expr_z

def inverseSequence(expr, N, ts=1):
    sequence = []
    expr_z = bilinearDiscretify(expr, ts)
    for i in range(N):
        sequence.append(IDZT0(z ** i * (expr_z - sum([sequence[n] / z**n for n in range(len(sequence))]))))
    return sequence


def inverseLaplaceNew(expr):
    expr = lcapy.expr(str(expr))
    expr_t = (expr*s/s).ILT(causal=True)
    expr_t = sp.simplify(sp.trigsimp(sp.re(expr_t.sympy)))
    return expr_t


def LaplaceNew(expr_t, t_=0):

    try:
        expr_t = expr_t.subs({t: t0})
        expr_t = expr_t.subs({t0: t0 + t_})
        expr_t = expr_t.subs({t0: t})
    except AttributeError:
        expr_t = expr_t

    expr_t *= sp.Heaviside(t)

    expr_t = lcapy.expr(str(expr_t))
    # expr = expr_t(s, causal=True)
    expr = expr_t(s)
    expr = sp.simplify(expr.sympy)
    return expr


if __name__ == "__main__":
    # print(inverseLaplace(61820502691519.0/(2.5e+20*s + 2.5e+17)))

    expr = 0.0588235294117647
    print(inverseLaplaceNew(expr))