from component import *

#--------------------------------------------------------------------------------------------------------------------------

class Potential(Component):

    def potential(self, Vs, Is):
        return [(
                    [
                        Eq(Vs["V"], 0),
                        Eq(Is["V"], 0)
                    ], 
                    [
                        Eq(Vs["V"], 0),
                        Eq(Is["V"], 0)
                    ],
                    [

                    ],
                        {}
                    )]

    def allModes(self, Vs, Is):
        return self.potential(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class VoltageSource(Component):
    """
    Default Values: \\
    Vdc = 0V \\
    Vac = 0V
    """
    
    default_values = {
        "Vdc" : 0,
        "Vac" : 0,
    }

    def source(self, Vs, Is):

        return [(
                    [
                        Eq(Vs["V+"] - Vs["V-"], self.values["Vdc"]),
                        *Component.ZeroCurrentSum(Is),
                    ], 
                    [
                        Eq(Vs["V+"] - Vs["V-"], self.values["Vac"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    [

                    ],
                        {}
                    )]

    def allModes(self, Vs, Is):
        return self.source(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class CurrentSource(Component):
    """
    Default Values: \\
    Idc = 0A \\
    Iac = 0A
    """

    default_values = {
        "Idc" : 0,
        "Iac" : 0,
    }

    def source(self, Vs, Is):

        return [(
                 [
                    Eq(Is["V+"], -self.values["Idc"]),
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    Eq(Is["V-"], -self.values["Iac"]),
                    *Component.ZeroCurrentSum(Is),
                 ],
                 [

                 ],
                    {}
                 )]

    def allModes(self, Vs, Is):
        return self.source(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Resistor(Component):
    """
    Default Values: \\
    R = 1k
    """

    default_values = {
        "R" : 1e3
    }

    def resistor(self, Vs, Is): 

        return [(
                 [
                    Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) / self.values["R"]),
                    *Component.ZeroCurrentSum(Is),
                 ],
                 [
                    Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) / self.values["R"]),
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    
                 ],
                    {}
                 )]

    def allModes(self, Vs, Is):
        return self.resistor(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Capacitor(Component):   #unfinished
    """
    Default Values: \\
    C = 1uF
    """

    default_values = {
        "C" : 1e-6
    }

    def capacitor(self, Vs, Is):

        return [(
                 [
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [
                    *Component.ShortCircuit(Vs, Is),
                 ], 
                 [
                    
                 ],
                    {}
                 )]

    def allModes(self, Vs, Is):
        return self.capacitor(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Inductor(Component):   #unfinished
    """
    Default Values: \\
    L = 1mH
    """

    default_values = {
        "L" : 1e-3
    }

    def inductor(self, Vs, Is):

        return [(
                 [
                    *Component.ShortCircuit(Vs, Is),
                 ],
                 [
                    *Component.OpenConnection(Vs, Is),
                 ], 
                 [
                    
                 ],
                    {}
                 )]

    def allModes(self, Vs, Is):
        return self.inductor(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Diode(Component):
    """
    Default Values: \\
    Vd = 0.6V
    """

    default_values = {
        "Vd" : 0.6
    }

    def Cut(self, Vs, Is):

        return [(
                 [
                    *Component.OpenConnection(Vs, Is)
                 ], 
                 [
                    
                 ],
                 [
                    Vs["Vp"] - Vs["Vn"] < self.values["Vd"],
                 ],
                    {self.name : "Cut"}
                 )]

    def Dir(self, Vs, Is):

        return [(
                 [
                    Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"]),
                    *Component.ZeroCurrentSum(Is)
                 ], 
                 [

                 ],
                 [
                    Is["Vp"] >= 0,
                 ],
                    {self.name : "Fwd"}
                 )]

    def allModes(self, Vs, Is):
        return  self.Cut(Vs, Is) + self.Dir(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class NPN(Component):
    """
    Default Values: \\
    Vdf = 0.7V \\
    Vdr = 0.5V \\
    Bf = 100 \\
    Br = 0.1
    """

    default_values = {
        "Vdf" : 0.6,
        "Vdr" : 0.4,
        "Bf"  : 100,
        "Br"  : 0.1,
    }

    def Cut(self, Vs, Is):

        return [(
                 [
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [

                 ],
                 [
                    Vs["Vb"] - Vs["Ve"] < self.values["Vdf"], 
                    Vs["Vb"] - Vs["Vc"] < self.values["Vdr"],
                 ],
                    {self.name : "Cut"}
                 )]

    def Dir(self, Vs, Is):

        return [(
                 [
                    Eq(Is["Vc"], self.values["Bf"] * Is["Vb"]),
                    Eq(Is["Ve"], -(self.values["Bf"] + 1) * Is["Vb"]),
                    Eq(Vs["Vb"] - Vs["Ve"], self.values["Vdf"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    Vs["Vb"] - Vs["Vc"] < self.values["Vdr"],
                 ],
                    {self.name : "Fwd"}
                 )]

    def Inv(self, Vs, Is):

        return [(
                 [
                    Eq(Is["Ve"], self.values["Br"] * Is["Vb"]),
                    Eq(Is["Vc"], -(self.values["Br"] + 1) * Is["Vb"]),
                    Eq(Vs["Vb"] - Vs["Vc"], self.values["Vdr"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    Vs["Vb"] - Vs["Ve"] < self.values["Vdf"],
                 ],
                    {self.name : "Inv"}
                 )]

    def Sat(self, Vs, Is):

        return [(
                 [
                    *Component.ZeroCurrentSum(Is),
                    Eq(Vs["Vb"] - Vs["Ve"], self.values["Vdf"]),
                    Eq(Vs["Vb"] - Vs["Vc"], self.values["Vdr"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    
                    Is["Vc"] <= self.values["Bf"] * Is["Vb"],
                    Is["Ve"] <= self.values["Br"] * Is["Vb"],
                 ],
                    {self.name : "Sat"}
                 )]

    def allModes(self, Vs, Is):
        return  self.Cut(Vs, Is) + self.Dir(Vs, Is) + self.Inv(Vs, Is) + self.Sat(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class PNP(Component):
    """
    Default Values: \\
    Vdf = 0.6V \\
    Vdr = 0.4V \\
    Bf = 100 \\
    Br = 0.1
    """

    default_values = {
        "Vdf" : 0.6,
        "Vdr" : 0.4,
        "Bf"  : 100,
        "Br"  : 0.1,
    }

    def Cut(self, Vs, Is):
        return [(
                 [
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [

                 ],
                 [
                    Vs["Ve"] - Vs["Vb"] < self.values["Vdf"],
                    Vs["Vc"] - Vs["Vb"] < self.values["Vdr"],
                 ],
                    {self.name : "Cut"}
                 )]
        
    def Dir(self, Vs, Is):
        return [(
                 [
                    Eq(Is["Ve"], -(self.values["Bf"] + 1) * Is["Vb"]),
                    Eq(Is["Vc"], self.values["Bf"] * Is["Vb"]),
                    Eq(Vs["Ve"] - Vs["Vb"], self.values["Vdf"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                    Vs["Vc"] - Vs["Vb"] < self.values["Vdr"],
                 ],
                    {self.name : "Fwd"}
                 )]

    def Inv(self, Vs, Is):
        return [(
                 [
                    Eq(Is["Vc"], -(self.values["Br"] + 1) * Is["Vb"]),
                    Eq(Is["Ve"], self.values["Br"] * Is["Vb"]),
                    Eq(Vs["Vc"] - Vs["Vb"], self.values["Vdr"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                    Vs["Ve"] - Vs["Vb"] < self.values["Vdf"],
                 ],
                    {self.name : "Inv"}
                 )]

    def Sat(self, Vs, Is):
        return [(
                 [
                    *Component.ZeroCurrentSum(Is),
                    Eq(Vs["Ve"] - Vs["Vb"], self.values["Vdf"]),
                    Eq(Vs["Vc"] - Vs["Vb"], self.values["Vdr"]),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                
                    Is["Vc"] >= self.values["Bf"] * Is["Vb"],
                    Is["Ve"] >= self.values["Br"] * Is["Vb"],
                 ],
                    {self.name : "Sat"}
                 )]

    def allModes(self, Vs, Is):
        return  self.Cut(Vs, Is) + self.Dir(Vs, Is) + self.Inv(Vs, Is) + self.Sat(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class OpAmp(Component):
    """
    Default Values: \\
    Av = inf
    """

    default_values = {
        "Av" : oo,
    }

    def Dir(self, Vs, Is):
        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"] / self.values["Av"], Vs["V+"] - Vs["V-"]),
                 ],
                 [
                    
                 ],
                 [
                    Vs["Vop"] <= Vs["Vcc"],
                    Vs["Vop"] >= Vs["Vee"], 
                 ],
                    {self.name : "Amp"}
                 )]

    def SatMax(self, Vs, Is):
        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"], Vs["Vcc"])
                 ],
                 [

                 ],
                 [
                    Vs["V+"] - Vs["V-"] > Vs["Vcc"] / self.values["Av"]
                 ],
                    {self.name : "SatMax"}
                 )]

    def SatMin(self, Vs, Is):
        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"], Vs["Vee"])
                 ],
                 [

                 ],
                 [
                    Vs["V+"] - Vs["V-"] < Vs["Vee"] / self.values["Av"]
                 ],
                    {self.name : "SatMin"}
                 )]
    
    def allModes(self, Vs, Is):
        return  self.Dir(Vs, Is) + self.SatMax(Vs, Is) + self.SatMin(Vs, Is)