from component import *

#--------------------------------------------------------------------------------------------------------------------------

class VoltageSource(Component):

    def __init__(self, name, nodes, V = 1):
        super().__init__(name, nodes)
        self.V = V

    def Dir(self):
        return [(
                    [
                    Eq(self.Vs[0] - self.Vs[1], self.V),
                    Eq(self.Is[0], -self.Is[1]),
                    ], 
                    [
                    ],
                    ""
                    )]

#--------------------------------------------------------------------------------------------------------------------------

class CurrentSource(Component):
   
    def __init__(self, name, nodes, I = 1e-3):
        super().__init__(name, nodes)
        self.I = I

    def Dir(self):
        return [(
                 [
                    Eq(self.Is[0], -self.I),
                    Eq(self.Is[1], self.I),
                 ], 
                 [
                 ],
                    ""
                 )]

#--------------------------------------------------------------------------------------------------------------------------

class Resistor(Component):

    def __init__(self, name, nodes, R = 1e3):
        super().__init__(name, nodes)
        self.R = R

    def Dir(self):
        return [(
                 [
                    Eq(self.Is[0], (self.Vs[0] - self.Vs[1]) / self.R),
                    Eq(self.Is[0], -self.Is[1]),
                 ], 
                 [
                 ],
                    ""
                    #f"{self.name}_{self.R}"
                 )]

#--------------------------------------------------------------------------------------------------------------------------

class Diode(Component):
    def __init__(self, name, nodes, Vt = 0.6):
        super().__init__(name, nodes)
        self.Vt = Vt

    def Cut(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),
                 ], 
                 [
                    self.Vs[0] - self.Vs[1] < self.Vt,
                 ],
                    f"{self.name}_Cut"
                 )]

    def Dir(self):
        return [(
                 [
                    Eq(self.Vs[0] - self.Vs[1], self.Vt),
                    Eq(self.Is[0], - self.Is[1]),
                 ], 
                 [
                    self.Is[0] >= 0,
                 ],
                    f"{self.name}_Fwd"
                 )]

    def allModes(self):
        return  self.Cut() + self.Dir()

#--------------------------------------------------------------------------------------------------------------------------

class NPN(Component):

    def __init__(self, name, nodes, Bf = 100, Br = 0.1, Vtf = 0.7, Vtr = 0.5):
        super().__init__(name, nodes)
        self.Bf = Bf
        self.Br = Br
        self.Vtf = Vtf
        self.Vtr = Vtr

    def Cut(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),
                    Eq(self.Is[2], 0),
                 ], 
                 [
                    self.Vs[1] - self.Vs[2] < self.Vtf,
                    self.Vs[1] - self.Vs[0] < self.Vtr,
                 ],
                    f"{self.name}_Cut"
                 )]

    def Dir(self):
        return [(
                 [
                    Eq(self.Is[0], self.Bf * self.Is[1]),
                    Eq(self.Is[2], -(self.Bf + 1) * self.Is[1]),
                    Eq(self.Vs[1] - self.Vs[2], self.Vtf),
                 ], 
                 [
                    self.Is[1] >= 0,
                    self.Vs[1] - self.Vs[0] < self.Vtr,
                 ],
                    f"{self.name}_Fwd"
                 )]

    def Inv(self):
        return [(
                 [
                    Eq(self.Is[2], self.Br * self.Is[1]),
                    Eq(self.Is[0], -(self.Br + 1) * self.Is[1]),
                    Eq(self.Vs[1] - self.Vs[0], self.Vtr),
                 ],
                 [
                    self.Is[1] >= 0,
                    self.Vs[1] - self.Vs[2] < self.Vtf,
                 ],
                    f"{self.name}_Inv"
                 )]

    def Sat(self):
        return [(
                 [
                    Eq(self.Is[0] + self.Is[1] + self.Is[2], 0),
                    Eq(self.Vs[1] - self.Vs[2], self.Vtf),
                    Eq(self.Vs[1] - self.Vs[0], self.Vtr),
                 ], 
                 [
                    self.Is[1] >= 0,
                    
                    self.Is[0] <= self.Bf * self.Is[1],
                    self.Is[2] <= self.Br * self.Is[1],
                 ],
                    f"{self.name}_Sat"
                 )]

    def allModes(self):
        return  self.Cut() + self.Dir() + self.Inv() + self.Sat()

#--------------------------------------------------------------------------------------------------------------------------

class PNP(Component):

    def __init__(self, name, nodes, Bf = 100, Br = 0.1, Vtf = 0.7, Vtr = 0.5):
        super().__init__(name, nodes)
        self.Bf = Bf
        self.Br = Br
        self.Vtf = Vtf
        self.Vtr = Vtr

    def Cut(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),
                    Eq(self.Is[2], 0),
                 ], 
                 [
                    self.Vs[0] - self.Vs[1] < self.Vtf,
                    self.Vs[2] - self.Vs[1] < self.Vtr,
                 ],
                    f"{self.name}_Cut"
                 )]

    def Dir(self):
        return [(
                 [
                    Eq(self.Is[0], -(self.Bf + 1) * self.Is[1]),
                    Eq(self.Is[2], self.Bf * self.Is[1]),
                    Eq(self.Vs[0] - self.Vs[1], self.Vtf),
                 ], 
                 [
                    self.Is[1] <= 0,
                    self.Vs[2] - self.Vs[1] < self.Vtr,
                 ],
                    f"{self.name}_Fwd"
                 )]

    def Inv(self):
        return [(
                 [
                    Eq(self.Is[2], -(self.Br + 1) * self.Is[1]),
                    Eq(self.Is[0], self.Br * self.Is[1]),
                    Eq(self.Vs[2] - self.Vs[1], self.Vtr),
                 ],
                 [
                    self.Is[1] <= 0,
                    self.Vs[0] - self.Vs[1] < self.Vtf,
                 ],
                    f"{self.name}_Inv"
                 )]

    def Sat(self):
        return [(
                 [
                    Eq(self.Is[0] + self.Is[1] + self.Is[2], 0),
                    Eq(self.Vs[0] - self.Vs[1], self.Vtf),
                    Eq(self.Vs[2] - self.Vs[1], self.Vtr),
                 ], 
                 [
                    self.Is[1] <= 0,
                
                    self.Is[2] >= self.Bf * self.Is[1],
                    self.Is[0] >= self.Br * self.Is[1],
                 ],
                    f"{self.name}_Sat"
                 )]

    def allModes(self):
        return  self.Cut() + self.Dir() + self.Inv() + self.Sat()

#--------------------------------------------------------------------------------------------------------------------------

class OpAmp(Component):
    
    def __init__(self, name, nodes, Av = oo):
        super().__init__(name, nodes)
        self.Av = Av

    def Dir(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),

                    Eq(self.Vs[2] / self.Av, self.Vs[0] - self.Vs[1]),
                    
                    Eq(self.Is[3], 0),
                    Eq(self.Is[4], 0),
                 ], 
                 [
                    self.Vs[2] <= self.Vs[3],
                    self.Vs[2] >= self.Vs[4], 
                 ],
                    f"{self.name}_Amp"
                 )]

    def SatMax(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),

                    Eq(self.Vs[2], self.Vs[3]),
                    
                    Eq(self.Is[3], 0),
                    Eq(self.Is[4], 0),
                 ], 
                 [
                    self.Vs[0] - self.Vs[1] > self.Vs[3] / self.Av
                 ],
                    f"{self.name}_SatMax"
                 )]

    def SatMin(self):
        return [(
                 [
                    Eq(self.Is[0], 0),
                    Eq(self.Is[1], 0),

                    Eq(self.Vs[2], self.Vs[4]),
                    
                    Eq(self.Is[3], 0),
                    Eq(self.Is[4], 0),
                 ], 
                 [
                    self.Vs[0] - self.Vs[1] < self.Vs[4] / self.Av
                 ],
                    f"{self.name}_SatMin"
                 )]
    
    def allModes(self):
        return  self.Dir() + self.SatMax() + self.SatMin()