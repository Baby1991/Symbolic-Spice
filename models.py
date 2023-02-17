from component import *

#--------------------------------------------------------------------------------------------------------------------------

class VoltageSource(Component):
    """
    Default Values: \\
    Vdc = 0V \\
    Vac = 0V
    """

    def getValues(self):
        Vdc = self.values.get("Vdc", 0)
        Vac = self.values.get("Vac", 0)
        return (Vdc, Vac)

    def source(self, Vs, Is):

        Vdc, Vac = self.getValues()

        return [(
                    [
                        Eq(Vs["V+"] - Vs["V-"], Vdc),
                        *Component.ZeroCurrentSum(Is),
                    ], 
                    [
                        Eq(Vs["V+"] - Vs["V-"], Vac),
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

    def getValues(self):
        Idc = self.values.get("Idc", 0)
        Iac = self.values.get("Iac", 0)
        return (Idc, Iac)

    def source(self, Vs, Is):

        Idc, Iac = self.getValues()

        return [(
                 [
                    Eq(Is["V+"], -Idc),
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    Eq(Is["V-"], -Iac),
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

    def getValues(self):
        R = self.values.get("R", 1e3)
        return (R)

    def resistor(self, Vs, Is):

        R = self.getValues()

        return [(
                 [
                    Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) / R),
                    *Component.ZeroCurrentSum(Is),
                 ],
                 [
                    Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) / R),
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

    def getValues(self):
        C = self.values.get("C", 1e-6)
        return (C)

    def capacitor(self, Vs, Is):

        C = self.getValues()

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

    def getValues(self):
        L = self.values.get("L", 1e-3)
        return (L)

    def inductor(self, Vs, Is):

        L = self.getValues()

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

    def getValues(self):
        Vd = self.values.get("Vd", 0.6)
        return (Vd)

    def Cut(self, Vs, Is):

        Vd = self.getValues()

        return [(
                 [
                    *Component.OpenConnection(Vs, Is)
                 ], 
                 [
                    
                 ],
                 [
                    Vs["Vp"] - Vs["Vn"] < Vd,
                 ],
                    {self.name : "Cut"}
                 )]

    def Dir(self, Vs, Is):

        Vd = self.getValues()

        return [(
                 [
                    Eq(Vs["Vp"] - Vs["Vn"], Vd),
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

    def getValues(self):
        Vdf = self.values.get("Vdf", 0.7)
        Vdr = self.values.get("Vdr", 0.5)
        Bf  = self.values.get("Bf", 100)
        Br  = self.values.get("Br", 0.1)
        return (Vdf, Vdr, Bf, Br)

    def Cut(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [

                 ],
                 [
                    Vs["Vb"] - Vs["Ve"] < Vdf, 
                    Vs["Vb"] - Vs["Vc"] < Vdr,
                 ],
                    {self.name : "Cut"}
                 )]

    def Dir(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    Eq(Is["Vc"], Bf * Is["Vb"]),
                    Eq(Is["Ve"], -(Bf + 1) * Is["Vb"]),
                    Eq(Vs["Vb"] - Vs["Ve"], Vdf),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    Vs["Vb"] - Vs["Vc"] < Vdr,
                 ],
                    {self.name : "Fwd"}
                 )]

    def Inv(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    Eq(Is["Ve"], Br * Is["Vb"]),
                    Eq(Is["Vc"], -(Br + 1) * Is["Vb"]),
                    Eq(Vs["Vb"] - Vs["Vc"], Vdr),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    Vs["Vb"] - Vs["Ve"] < Vdf,
                 ],
                    {self.name : "Inv"}
                 )]

    def Sat(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    *Component.ZeroCurrentSum(Is),
                    Eq(Vs["Vb"] - Vs["Ve"], Vdf),
                    Eq(Vs["Vb"] - Vs["Vc"], Vdr),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] >= 0,
                    
                    Is["Vc"] <= Bf * Is["Vb"],
                    Is["Ve"] <= Br * Is["Vb"],
                 ],
                    {self.name : "Sat"}
                 )]

    def allModes(self, Vs, Is):
        return  self.Cut(Vs, Is) + self.Dir(Vs, Is) + self.Inv(Vs, Is) + self.Sat(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class PNP(Component):
    """
    Default Values: \\
    Vdf = 0.7V \\
    Vdr = 0.5V \\
    Bf = 100 \\
    Br = 0.1
    """

    def getValues(self):
        Vdf = self.values.get("Vdf", 0.7)
        Vdr = self.values.get("Vdr", 0.5)
        Bf  = self.values.get("Bf", 100)
        Br  = self.values.get("Br", 0.1)
        return (Vdf, Vdr, Bf, Br)

    def Cut(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [

                 ],
                 [
                    Vs["Ve"] - Vs["Vb"] < Vdf,
                    Vs["Vc"] - Vs["Vb"] < Vdr,
                 ],
                    {self.name : "Cut"}
                 )]
        
    def Dir(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    Eq(Is["Ve"], -(Bf + 1) * Is["Vb"]),
                    Eq(Is["Vc"], Bf * Is["Vb"]),
                    Eq(Vs["Ve"] - Vs["Vb"], Vdf),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                    Vs["Vc"] - Vs["Vb"] < Vdr,
                 ],
                    {self.name : "Fwd"}
                 )]

    def Inv(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    Eq(Is["Vc"], -(Br + 1) * Is["Vb"]),
                    Eq(Is["Ve"], Br * Is["Vb"]),
                    Eq(Vs["Vc"] - Vs["Vb"], Vdr),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                    Vs["Ve"] - Vs["Vb"] < Vdf,
                 ],
                    {self.name : "Inv"}
                 )]

    def Sat(self, Vs, Is):

        Vdf, Vdr, Bf, Br = self.getValues()

        return [(
                 [
                    *Component.ZeroCurrentSum(Is),
                    Eq(Vs["Ve"] - Vs["Vb"], Vdf),
                    Eq(Vs["Vc"] - Vs["Vb"], Vdr),
                 ],
                 [

                 ],
                 [
                    Is["Vb"] <= 0,
                
                    Is["Vc"] >= Bf * Is["Vb"],
                    Is["Ve"] >= Br * Is["Vb"],
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

    def getValues(self):
        Av = self.values.get("Av", oo)
        return (Av)

    def Dir(self, Vs, Is):

        Av = self.getValues()

        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"] / Av, Vs["V+"] - Vs["V-"]),
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

        Av = self.getValues()

        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"], Vs["Vcc"])
                 ],
                 [

                 ],
                 [
                    Vs["V+"] - Vs["V-"] > Vs["Vcc"] / Av
                 ],
                    {self.name : "SatMax"}
                 )]

    def SatMin(self, Vs, Is):

        Av = self.getValues()

        return [(
                 [
                    *Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Vs["Vop"], Vs["Vee"])
                 ],
                 [

                 ],
                 [
                    Vs["V+"] - Vs["V-"] < Vs["Vee"] / Av
                 ],
                    {self.name : "SatMin"}
                 )]
    
    def allModes(self, Vs, Is):
        return  self.Dir(Vs, Is) + self.SatMax(Vs, Is) + self.SatMin(Vs, Is)