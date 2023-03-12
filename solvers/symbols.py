from sympy import Symbol

from lcapy import s, t
from lcapy.discretetime import n, dt, z

#s = Symbol("s")
#t = Symbol("t", real=True, positive=True)

s = s.sympy
t = t.sympy
n = n.sympy
z = z.sympy

t0 = Symbol("t_0", real=True, positive=True)
n0 = Symbol("n_0", positive = True)