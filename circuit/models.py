from circuit.component import *

import sympy as sp

# --------------------------------------------------------------------------------------------------------------------------
# Physical Constants

kB_e = 86.173_332_62e-6  # Boltzmann / Elementary Charge

# --------------------------------------------------------------------------------------------------------------------------


class VoltageSource(Component):
    """
    Default Values: \\
    V = 0V \\
    """

    default_values = {
        "V": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        Eq(Vs["V+"] - Vs["V-"], self.values["V"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },
            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class CurrentSource(Component):
    """
    Default Values: \\
    I = 0A \\
    """

    default_values = {
        "I": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        Eq(Is["V-"], self.values["I"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },
            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class Resistor(Component):
    """
    Default Values: \\
    R = 1k
    """

    default_values = {
        "R": 1e3
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) /
                           self.values["R"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

            }
        }

class Diode(Component):
    """
    Default Values: \\
    Vd = 0.6V\\
    """

    default_values = {
        "Vd": 0.6,
    }

    def allModes(self, Vs, Is):
        return {

            "Cut": {
                "OP": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is)
                    ],
                    "conditions": [
                        Vs["Vp"] - Vs["Vn"] < self.values["Vd"]
                    ]
                },

            },

            "Fwd": {
                "OP" : {
                    "equations": [
                        Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"]),
                        *Component.ZeroCurrentSum(Is)
                    ],
                    "conditions": [
                        Is["Vp"] >= 0
                    ]
                },

            }
        }


# --------------------------------------------------------------------------------------------------------------------------

class NPN(Component):
    """
    Default Values: \\
    Vdf = 0.6V \\
    Vdr = 0.4V \\
    Bf = 100 \\
    Br = 0.1
    """

    default_values = {
        "Vdf": 0.6,
        "Vdr": 0.4,
        "Bf": 100,
        "Br": 0.1,
    }

    def allModes(self, Vs, Is):
        return {

            "Cut": {
                "OP": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [
                        Vs["Vb"] - Vs["Ve"] <= self.values["Vdf"],
                        Vs["Vb"] - Vs["Vc"] <= self.values["Vdr"],
                    ]
                },

            },

            "Fwd": {
                "OP": {
                    "equations": [
                        Eq(Is["Vc"], self.values["Bf"] * Is["Vb"]),
                        Eq(Is["Ve"], -(self.values["Bf"] + 1) * Is["Vb"]),
                        Eq(Vs["Vb"] - Vs["Ve"], self.values["Vdf"]),
                    ],
                    "conditions": [
                        Is["Vb"] > 0,
                        Vs["Vb"] - Vs["Vc"] <= self.values["Vdr"],
                    ]
                },

            },

            "Inv": {
                "OP": {
                    "equations": [
                        Eq(Is["Ve"], self.values["Br"] * Is["Vb"]),
                        Eq(Is["Vc"], -(self.values["Br"] + 1) * Is["Vb"]),
                        Eq(Vs["Vb"] - Vs["Vc"], self.values["Vdr"]),
                    ],
                    "conditions": [
                        Is["Vb"] > 0,
                        Vs["Vb"] - Vs["Ve"] <= self.values["Vdf"],
                    ]
                },

            },

            "Sat": {
                "OP": {
                    "equations": [
                        *Component.ZeroCurrentSum(Is),
                        Eq(Vs["Vb"] - Vs["Ve"], self.values["Vdf"]),
                        Eq(Vs["Vb"] - Vs["Vc"], self.values["Vdr"]),
                    ],
                    "conditions": [
                        Is["Vb"] > 0,
                        Is["Vc"] < self.values["Bf"] * Is["Vb"],
                        Is["Ve"] < self.values["Br"] * Is["Vb"],
                    ]
                },

            },
        }

# --------------------------------------------------------------------------------------------------------------------------


class PNP(Component):
    """
    Default Values: \\
    Vdf = 0.6V \\
    Vdr = 0.4V \\
    Bf = 100 \\
    Br = 0.1
    """

    default_values = {
        "Vdf": 0.6,
        "Vdr": 0.4,
        "Bf": 100,
        "Br": 0.1,
    }

    def allModes(self, Vs, Is):
        return {

            "Cut": {
                "OP": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [
                        Vs["Ve"] - Vs["Vb"] <= self.values["Vdf"],
                        Vs["Vc"] - Vs["Vb"] <= self.values["Vdr"],
                    ]
                },
            },

            "Fwd": {
                "OP": {
                    "equations": [
                        Eq(Is["Ve"], -(self.values["Bf"] + 1) * Is["Vb"]),
                        Eq(Is["Vc"], self.values["Bf"] * Is["Vb"]),
                        Eq(Vs["Ve"] - Vs["Vb"], self.values["Vdf"]),
                    ],
                    "conditions": [
                        Is["Vb"] < 0,
                        Vs["Vc"] - Vs["Vb"] <= self.values["Vdr"],
                    ]
                },
            },

            "Inv": {
                "OP": {
                    "equations": [
                        Eq(Is["Vc"], -(self.values["Br"] + 1) * Is["Vb"]),
                        Eq(Is["Ve"], self.values["Br"] * Is["Vb"]),
                        Eq(Vs["Vc"] - Vs["Vb"], self.values["Vdr"]),
                    ],
                    "conditions": [
                        Is["Vb"] < 0,
                        Vs["Ve"] - Vs["Vb"] <= self.values["Vdf"],
                    ]
                },
            },

            "Sat": {
                "OP": {
                    "equations": [
                        *Component.ZeroCurrentSum(Is),
                        Eq(Vs["Ve"] - Vs["Vb"], self.values["Vdf"]),
                        Eq(Vs["Vc"] - Vs["Vb"], self.values["Vdr"]),
                    ],
                    "conditions": [
                        Is["Vb"] < 0,
                        Is["Vc"] > self.values["Bf"] * Is["Vb"],
                        Is["Ve"] > self.values["Br"] * Is["Vb"],
                    ]
                },
            },
        }

# --------------------------------------------------------------------------------------------------------------------------


class OpAmp(Component):
    """
    Default Values: \\
    Av = inf
    """

    default_values = {
        "Av": oo,
    }

    def allModes(self, Vs, Is):
        return {
            "Amp": {
                "OP": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"] / self.values["Av"],
                           Vs["V+"] - Vs["V-"]),
                    ],
                    "conditions": [
                        Vs["Vop"] < Vs["Vcc"],
                        Vs["Vop"] > Vs["Vee"],
                    ]
                },
            },

            "SatMax": {
                "OP": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], Vs["Vcc"])
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] >= Vs["Vcc"] / self.values["Av"],
                    ]
                },
            },

            "SatMin": {
                "OP": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], Vs["Vee"])
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] <= Vs["Vee"] / self.values["Av"],
                    ]
                },
            },

        }
        
        
# --------------------------------------------------------------------------------------------------------------------------


class Relay(Component):
    """
    Default Values: \\
    Vs = 0V\\
    """

    default_values = {
        "Vs": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "Open": {
                "OP": {
                    "equations": [
                        Eq(Is["V1"], 0),
                        Eq(Is["V2"], 0),
                        
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] < self.values["Vs"],
                    ]
                },

            },

            "Closed": {
                "OP" : {
                    "equations": [
                        Eq(Vs["V1"], Vs["V2"]),
                        Eq(Is["V1"] + Is["V2"], 0),
                        
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] >= self.values["Vs"]
                    ]
                },

            }
        }
