from sympy import Symbol

s = Symbol("s")
#t = Symbol("t", real=True, nonnegative=True)
t = Symbol("t", real=True, positive=True)
t0 = Symbol("t_0", real=True, positive=True)