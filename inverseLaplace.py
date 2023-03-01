import sympy as sp
from copy import deepcopy

s = sp.Symbol("s")
#t = Symbol("t", real=True, positive=True)
t = sp.Symbol("t", real=True, nonnegative=True)

class Heaviside_(sp.Function):
    @classmethod
    def eval(cls, t):
        if t.is_number:
            return sp.Float(1.0) if t >= sp.Float(0.0) else sp.Float(0.0)
        
    def _latex(self, printer):
        t, = self.args
        _t = printer._print(t)
        return r'\theta(%s)' % (_t)

    
class DiracDelta_(sp.Function):
    @classmethod
    def eval(cls, t):
        if t.is_number:
            return sp.Float(1.0) if abs(t) < 1e-9 else sp.Float(0.0)

    def _latex(self, printer):
        t, = self.args
        _t = printer._print(t)
        return r'\delta(%s)' % (_t)

def Laplace(x, t0 = 0):
    #func = x.subs({t : t + t0}) * sp.Heaviside(t, 1.0)
    func = x.subs({t : t + t0}) * sp.Heaviside(t)
    return sp.laplace_transform(func, t, s, noconds=True)


def discriminate(exp):
    for a in sp.preorder_traversal(exp):
        if type(a) == sp.Float:
            if abs(a) < 1e-8:
                #exp = exp.subs({a : 0.0})
                pass
    return exp


def inverseLaplace(exp, debug = False):
    exp = sp.expand(exp)
    
    exp = discriminate(exp)
    
    match(type(exp)):
        
        case sp.Float:
            exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))
            #exp_t = exp_t.subs({sp.Heaviside(t) : 1})
            
        case sp.Integer:
            exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))
            #exp_t = exp_t.subs({sp.Heaviside(t) : 1})
                
        case sp.Add:
            exp_t = sum(inverseLaplace(x, debug=debug) for x in exp.args)
            
        case sp.Pow:
            numer, denom = exp.as_numer_denom()
            if abs(numer - 1) < 1e-6:
                exp = exp.apart(s)
                if type(exp) == sp.Add:
                    exp_t = inverseLaplace(exp, debug=debug)
                else:
                    exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))
                    #exp_t = exp_t.subs({sp.Heaviside(t) : 1})
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
                        #case _:
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
                    
            if diff > 0:
                match type(denom):
                    case sp.Symbol:
                        diff -= 1
                        denom = 1
                    case sp.Pow:
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
                        for a in denom.args:
                            match type(a):
                                case sp.Symbol:
                                    diff -= 1
                                    denom = denom.subs({a : 1})
                                case sp.Pow:
                                    if diff > a.args[1]:
                                        denom = denom.subs({a : 1})
                                        diff -= a.args[1]
                                    elif diff == a.args[1]:
                                        denom = denom.subs({a : 1})
                                        diff = 0
                                    else:
                                        denom = denom.subs({a : a / sp.Pow(s, diff)})
                                        diff = 0
                                case sp.Float:
                                    pass
                                case sp.Add:
                                    pass
                                case _:
                                        print(a, type(a))
                                        raise Exception("type(n) Unexpected")
                        
                    case sp.Add:
                        pass
                        
                    case _:
                        print(denom, type(denom))
                        raise Exception("type(n) Unexpected")
            
            exp = (mul / denom).apart(s)
            exp = discriminate(exp)
            
            if type(exp) == sp.Add:
                exp_t = inverseLaplace(exp, debug=debug)
            else:
                exp_t = sp.re(sp.inverse_laplace_transform(exp, s, t))
                #exp_t = exp_t.subs({sp.Heaviside(t) : 1})
            
            exp_t = sp.diff(exp_t, t, diff)
            exp_t = exp_t.subs({t : t + shift})
            exp_t = discriminate(exp_t)
            
        case _:
            raise Exception("type(exp) Unexpected")
    
    return exp_t
        
        
