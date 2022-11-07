from circuit import Node
from sympy import Eq, oo

#--------------------------------------------------------------------------------------------------------------------------

class Component:
    def __init__(self, name, nodes) -> None:
        self.name = name
        self.nodes = nodes
        self.Vs = []
        self.Is = []

        for V in nodes:
            if isinstance(V, Node):
                self.Vs.append(V())
            else:
                self.Vs.append(V)

    def setCurrents(self, Is):
        self.Is = Is

    def Dir(self):
        return [(
                 [
                    Eq(self.Vs[0],  self.Vs[1]),
                    Eq(self.Is[0], -self.Is[1]),
                 ], 
                 [

                 ],
                    ""
                    #f"{self.name}_SC"
                 )]

    def current(self, id=0):
        return self.Is[id]

    def potential(self, id=0):
        return self.Vs[id]

    def allModes(self):
        return self.Dir()

#--------------------------------------------------------------------------------------------------------------------------