from node import Node
from sympy import Eq, oo, Symbol
from copy import deepcopy

#--------------------------------------------------------------------------------------------------------------------------

s = Symbol("s")

class Component:
    """
    V1\\
    V2\\
    I1\\
    I2\\
    """
    
    default_values = {
        
    }
    
    values = {
        
    }

    def __init__(self, name, nodes, **values) -> None:
        self.name = name
        self.nodes = nodes
        self.values = deepcopy(self.default_values)
        self.values.update(values)
    
    def __repr__(self) -> dict:
        return str({
            "name" : self.name,
            "type" : type(self).__name__,
            "nodes" : self.nodes,
            "values" : self.values,
        })
    
    """
    def __repr__(self) -> str:
        return pformat({
            "name" : self.name,
            "type" : type(self),
            "nodes" : self.nodes,
            "values" : self.values,
        })
    """
        
    """

    def setCurrents(self, Is):
        self.Is = Is

    def current(self, id=0):
        return self.Is[id]

    def potential(self, id=0):
        return self.Vs[id]

    """

    def ZeroCurrents(Is):
        return [Eq(I, 0) for I in Is.values()]

    def ZeroCurrentSum(Is):
        return [Eq(sum(Is.values()), 0)]

    def EqualVoltages(Vs):
        return [Eq(Vs[i+1],  Vs[i]) for i in range(len(Vs.values()) - 1)]

    def ShortCircuit(Vs, Is):
        return Component.ZeroCurrentSum(Is) + Component.EqualVoltages(Vs)
    
    def OpenConnection(Vs, Is):
        return Component.ZeroCurrents(Is)

    def allModes(self, Vs, Is):
        return [(
                 [
                    Eq(Vs["V1"],  Vs["V2"]), 
                    Eq(Is["I1"], -Is["I2"]), 
                 ], 
                 [
                    Eq(Vs["V1"],  Vs["V2"]),
                    Eq(Is["I1"], -Is["I2"]),
                 ],
                 [

                 ],
                    (self.name, "")
                 )]
        
    def __call__(self, Vs, Is):
        return self.allModes(Vs, Is)
    
#--------------------------------------------------------------------------------------------------------------------------