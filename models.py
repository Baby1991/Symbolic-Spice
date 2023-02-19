from component import *

#--------------------------------------------------------------------------------------------------------------------------

class Potential(Component):
    """
    Default Values: \\
    Vdc = 0V \\
    V   = 0V
    """

    default_values = {
        "Vdc" : 0,
        "V"   : 0,
    }

    def potential(self, Vs, Is):
        return [(
                    [
                        Eq(Vs["V"], self.values["Vdc"]),
                    ], 
                    [
                        Eq(Vs["V"], self.values["V"]),
                    ],
                    [

                    ],
                        (self.name, "")
                    )]

    def allModes(self, Vs, Is):
        return self.potential(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class VoltageSource(Component):
    """
    Default Values: \\
    Vdc = 0V \\
    V   = 0V
    """
    
    default_values = {
        "Vdc" : 0,
        "V"   : 0,
    }

    def source(self, Vs, Is):

        return [(
                    [
                        Eq(Vs["V+"] - Vs["V-"], self.values["Vdc"]),
                        *Component.ZeroCurrentSum(Is),
                    ], 
                    [
                        Eq(Vs["V+"] - Vs["V-"], self.values["V"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    [

                    ],
                        (self.name, "")
                    )]

    def allModes(self, Vs, Is):
        return self.source(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class CurrentSource(Component):
    """
    Default Values: \\
    Idc = 0A \\
    I   = 0A
    """

    default_values = {
        "Idc" : 0,
        "I"   : 0,
    }

    def source(self, Vs, Is):

        return [(
                 [
                    Eq(Is["V+"], -self.values["Idc"]),
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    Eq(Is["V-"], -self.values["I"]),
                    *Component.ZeroCurrentSum(Is),
                 ],
                 [

                 ],
                    (self.name, "")
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

                 ], 
                 [
                    
                 ],
                    (self.name, "")
                 )]

    def allModes(self, Vs, Is):
        return self.resistor(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Capacitor(Component):   #unfinished
    """
    Default Values: \\
    C = 1uF\\
    V1_0 = 0V\\
    V2_0 = 0V
    """

    default_values = {
        "C" : 1e-6,
        "V1_0" : 0,
        "V2_0" : 0,
    }

    def capacitor(self, Vs, Is):

        return [(
                 [
                    #Eq(Vs["V1"] - Vs["V2"], self.values["V0"]),
                    *Component.OpenConnection(Vs, Is),
                 ],
                 [
                    Eq(Is["V1"], self.values["C"] * (s * (Vs["V1"] - Vs["V2"]) - (self.values["V1_0"] - self.values["V2_0"]))), 
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    
                 ],
                    (self.name, "")
                 )]

    def allModes(self, Vs, Is):
        return self.capacitor(Vs, Is)

#--------------------------------------------------------------------------------------------------------------------------

class Inductor(Component):   #unfinished
    """
    Default Values: \\
    L = 1mH\\
    I_V1_0 = 0A\\
    I_V2_0 = 0A
    """

    default_values = {
        "L" : 1e-3,
        "I_V1_0" : 0,
        "I_V2_0" : 0,
    }

    def inductor(self, Vs, Is):

        return [(
                 [
                    *Component.ShortCircuit(Vs, Is),
                 ],
                 [
                    Eq(Vs["V1"] - Vs["V2"], s * Is["V1"] - self.values["I_V1_0"])
                    *Component.ZeroCurrentSum(Is),
                 ], 
                 [
                    
                 ],
                    (self.name, "")
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
                    Vs["Vp"] - Vs["Vn"] <= self.values["Vd"],
                 ],
                    (self.name, "Cut")
                 )]

    def Dir(self, Vs, Is):

        return [(
                 [
                    Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"]),
                    *Component.ZeroCurrentSum(Is)
                 ], 
                 [
                    Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"] / s),
                    *Component.ZeroCurrentSum(Is)
                 ],
                 [
                    Is["Vp"] > 0,
                 ],
                    (self.name, "Fwd")
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
                    Vs["Vb"] - Vs["Ve"] <= self.values["Vdf"], 
                    Vs["Vb"] - Vs["Vc"] <= self.values["Vdr"],
                 ],
                    (self.name, "Cut")
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
                    Is["Vb"] > 0,
                    Vs["Vb"] - Vs["Vc"] <= self.values["Vdr"],
                 ],
                    (self.name, "Fwd")
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
                    Is["Vb"] > 0,
                    Vs["Vb"] - Vs["Ve"] <= self.values["Vdf"],
                 ],
                    (self.name, "Inv")
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
                    Is["Vb"] > 0,
                    
                    Is["Vc"] < self.values["Bf"] * Is["Vb"],
                    Is["Ve"] < self.values["Br"] * Is["Vb"],
                 ],
                    (self.name, "Sat")
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
                    Vs["Ve"] - Vs["Vb"] <= self.values["Vdf"],
                    Vs["Vc"] - Vs["Vb"] <= self.values["Vdr"],
                 ],
                    (self.name, "Cut")
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
                    Is["Vb"] < 0,
                    Vs["Vc"] - Vs["Vb"] <= self.values["Vdr"],
                 ],
                    (self.name, "Fwd")
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
                    Is["Vb"] < 0,
                    Vs["Ve"] - Vs["Vb"] <= self.values["Vdf"],
                 ],
                    (self.name, "Inv")
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
                    Is["Vb"] < 0,
                
                    Is["Vc"] > self.values["Bf"] * Is["Vb"],
                    Is["Ve"] > self.values["Br"] * Is["Vb"],
                 ],
                    (self.name, "Sat")
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
                    #*Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Is["V+"], 0),
                    Eq(Is["V-"], 0),
                    Eq(Is["Vcc"], 0),
                    Eq(Is["Vee"], 0),
                    Eq(Vs["Vop"] / self.values["Av"], Vs["V+"] - Vs["V-"]),
                 ],
                 [
                    
                 ],
                 [
                    Vs["Vop"] <= Vs["Vcc"],
                    Vs["Vop"] >= Vs["Vee"], 
                 ],
                    (self.name, "Amp")
                 )]

    def SatMax(self, Vs, Is):
        return [(
                 [
                    #*Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Is["V+"], 0),
                    Eq(Is["V-"], 0),
                    Eq(Is["Vcc"], 0),
                    Eq(Is["Vee"], 0),
                    Eq(Vs["Vop"], Vs["Vcc"])
                 ],
                 [
                    #*Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Is["V+"], 0),
                    Eq(Is["V-"], 0),
                    Eq(Is["Vcc"], 0),
                    Eq(Is["Vee"], 0),
                    Eq(Vs["Vop"], Vs["Vcc"] / s)
                 ],
                 [
                    Vs["V+"] - Vs["V-"] > Vs["Vcc"] / self.values["Av"]
                 ],
                    (self.name, "SatMax")
                 )]

    def SatMin(self, Vs, Is):
        return [(
                 [
                    #*Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Is["V+"], 0),
                    Eq(Is["V-"], 0),
                    Eq(Is["Vcc"], 0),
                    Eq(Is["Vee"], 0),
                    Eq(Vs["Vop"], Vs["Vee"])
                 ],
                 [
                    #*Component.ZeroCurrents({Is["V+"], Is["V-"], Is["Vcc"], Is["Vee"]}),
                    Eq(Is["V+"], 0),
                    Eq(Is["V-"], 0),
                    Eq(Is["Vcc"], 0),
                    Eq(Is["Vee"], 0),
                    Eq(Vs["Vop"], Vs["Vee"] / s)
                 ],
                 [
                    Vs["V+"] - Vs["V-"] < Vs["Vee"] / self.values["Av"]
                 ],
                    (self.name, "SatMin")
                 )]
    
    def allModes(self, Vs, Is):
        return  self.Dir(Vs, Is) + self.SatMax(Vs, Is) + self.SatMin(Vs, Is)