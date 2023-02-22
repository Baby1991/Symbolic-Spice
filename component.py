from node import Node
from sympy import Eq, oo, Symbol
from copy import deepcopy

# --------------------------------------------------------------------------------------------------------------------------

s  = Symbol("s")

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
        
        """
        for key in self.nodes.keys():
            self.values.update({f"{key}_0": 0})
            self.values.update({f"I_{key}_0": 0})
        """
        
        self.values.update(values)

    def __repr__(self) -> dict:
        return str({
            "name": self.name,
            "type": type(self).__name__,
            "nodes": self.nodes,
            "values": self.values,
        })

    def ZeroCurrents(Is):
        return [Eq(I, 0) for I in Is.values()]

    def ZeroCurrentSum(Is):
        return [Eq(sum(Is.values()), 0)]

    def EqualVoltages(Vs):
        Vs = list(Vs.values())
        return [Eq(Vs[i+1],  Vs[i]) for i in range(len(Vs) - 1)]

    def ShortCircuit(Vs, Is):
        return Component.ZeroCurrentSum(Is) + Component.EqualVoltages(Vs)

    def OpenConnection(Vs, Is):
        return Component.ZeroCurrents(Is)


    def default_equations(self, Vs, Is):
        return {
            *Component.ShortCircuit(Vs, Is),
        }
    
    def default_conditions(self, Vs, Is):
        return {
            
        }


    def allModes(self, Vs, Is):
        return {
                "": {
                    "OP": {
                        "equations": {
                            Eq(Vs["V1"],  Vs["V2"]),
                            Eq(Is["I1"], -Is["I2"]),
                        },
                        "conditions": {

                        }
                    },
                    
                    "Laplace": {
                        "equations": {
                            Eq(Vs["V1"],  Vs["V2"]),
                            Eq(Is["I1"], -Is["I2"]),
                        },
                        "conditions": {

                        }
                    },
                    
                    "AC+DC" : {
                        "equations": {
                            Eq(Vs["V1"],  Vs["V2"]),
                            Eq(Is["I1"], -Is["I2"]),
                        },
                        "conditions": {

                        }
                    }
                    
                }
        }
        

    def __call__(self, Vs, Is):
        return self.allModes(Vs, Is)

# --------------------------------------------------------------------------------------------------------------------------
