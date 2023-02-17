from node import Node
from sympy import Eq, oo

#--------------------------------------------------------------------------------------------------------------------------

class Component:
    """
    V1\\
    V2\\
    I1\\
    I2\\
    """

    def __init__(self, name, nodes, **values) -> None:
        self.name = name
        self.nodes = nodes
        self.Vs = {}
        self.Is = {}
        self.values = values

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
                    {}
                 )]
    
#--------------------------------------------------------------------------------------------------------------------------