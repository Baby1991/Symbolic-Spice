from component import *

from inverseLaplace import Laplace

# --------------------------------------------------------------------------------------------------------------------------
# Physical Constants

kB_e = 86.173_332_62e-6  # Boltzmann / Elementary Charge

delta = 1e-6

# --------------------------------------------------------------------------------------------------------------------------


class VoltageSource(Component):
    """
    Default Values: \\
    Vdc = 0V \\
    Vac = 0V \\
    V_t = 0V \\
    """

    default_values = {
        "Vdc": 0,
        "Vac": 0,
        "V_t": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        Eq(Vs["V+"] - Vs["V-"], self.values["Vdc"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "Laplace": {
                    "equations": [
                        Eq(
                            #Vs["V+"] - Vs["V-"], self.values["V_s"] * exp(s * self.values.get("t_0", 0))
                            Vs["V+"] - Vs["V-"],  Laplace(self.values["V_t"], self.values.get("t_0", 0))
                        ),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Vs["V+"] - Vs["V-"],
                           self.values["Vdc"] + self.values["Vac"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V+"] - Vs["V-"], self.values["Vac"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                }

            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class CurrentSource(Component):
    """
    Default Values: \\
    Idc = 0A \\
    Iac = 0A \\
    I_t = 0A \\
    """

    default_values = {
        "Idc": 0,
        "Iac": 0,
        "I_t": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        Eq(Is["V-"], self.values["Idc"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "Laplace": {
                    "equations": [
                        Eq(
                            #Is["V-"], self.values["I_s"] * exp(s * self.values.get("t_0", 0))
                           # + self.values.get("I_V+_0", 0) / s
                           Is["V-"],  Laplace(self.values["I_t"], self.values.get("t_0", 0))
                        ),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Is["V-"], self.values["Idc"] + self.values["Iac"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "SmallSignal": {
                    "equations": [
                        Eq(Is["V-"], self.values["Iac"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                }

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

                "Laplace": {
                    "equations": [
                        Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) /
                           self.values["R"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) /
                           self.values["R"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "SmallSignal": {
                    "equations": [
                        Eq(Is["V1"], (Vs["V1"] - Vs["V2"]) /
                           self.values["R"]),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                }

            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class Capacitor(Component):  # unfinished
    """
    Default Values: \\
    C = 1uF\\
    V0 = 0V\\
    """

    default_values = {
        "C": 1e-6,
        "V0": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [

                    ]
                },

                "Laplace": {
                    "equations": [
                        Eq(Is["V1"], self.values["C"] * (s * (Vs["V1"] - Vs["V2"])
                                                         -
                                                             (self.values.get(
                                                                 "V1_0",  self.values["V0"]) - self.values.get("V2_0", 0))
                                                         )),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Vs["V1"] - Vs["V2"], self.values.get("V1_0",
                           self.values["V0"]) - self.values.get("V2_0", 0)),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "SmallSignal": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [

                    ]
                }

            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class Inductor(Component):  # unfinished
    """
    Default Values: \\
    L = 1mH\\
    I0 = 0A\\
    """

    default_values = {
        "L": 1e-3,
        "I0": 0,
    }

    def allModes(self, Vs, Is):
        return {

            "": {
                "OP": {
                    "equations": [
                        *Component.ShortCircuit(Vs, Is),

                        # Eq(Is["V1"], self.values["I0"]),
                        # *Component.ZeroCurrentSum(Is),
                        # Eq(Vs["V1"], Vs["V2"]),
                    ],
                    "conditions": [

                    ]
                },

                "Laplace": {
                    "equations": [
                        Eq(Vs["V1"] - Vs["V2"], s *
                           Is["V1"] - self.values.get("I_V1_0",  self.values["I0"])),
                        * Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Is["V1"], self.values.get(
                            "I_V1_0",  self.values["I0"])),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [

                    ]
                },

                "SmallSignal": {
                    "equations": [
                        *Component.ShortCircuit(Vs, Is),
                    ],
                    "conditions": [

                    ]
                }

            }
        }

# --------------------------------------------------------------------------------------------------------------------------


class Diode(Component):
    """
    Default Values: \\
    Vd = 0.6V\\
    T  = 300K\\
    """

    default_values = {
        "Vd": 0.6,
        "T": 300,
    }

    def allModes(self, Vs, Is):
        return {

            "Cut": {
                "OP": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is)
                    ],
                    "conditions": [
                        Vs["Vp"] - Vs["Vn"] <= self.values["Vd"]
                    ]
                },

                "Laplace": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is)
                    ],
                    "conditions": [
                        Vs["Vp"] - Vs["Vn"] < self.values["Vd"]
                    ]
                },

                "AC+DC": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is)
                    ],
                    "conditions": [
                        Vs["Vp"] - Vs["Vn"] <= self.values["Vd"]
                    ]
                },

                "SmallSignal": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is)
                    ],
                    "conditions": [
                        #(Vs["Vp"] - Vs["Vn"]) + (self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) < self.values["Vd"],
                        #(self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) < self.values["Vd"],
                        
                        (self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) < self.values["Vd"],
                        
                        #(Vs["Vp"] - Vs["Vn"]) <= -self.values["Vd"]
                    ]
                }

            },

            "Fwd": {
                "OP": {
                    "equations": [
                        Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"]),
                        *Component.ZeroCurrentSum(Is)
                    ],
                    "conditions": [
                        Is["Vp"] > 0
                    ]
                },

                "Laplace": {
                    "equations": [
                        Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"] / s),
                        *Component.ZeroCurrentSum(Is)
                    ],
                    "conditions": [
                        Is["Vp"] >= 0
                        #Is["Vp"] > -delta
                    ]
                },

                "AC+DC": {
                    "equations": [
                        Eq(Vs["Vp"] - Vs["Vn"], self.values["Vd"]),
                        *Component.ZeroCurrentSum(Is)
                    ],
                    "conditions": [
                        Is["Vp"] > 0
                    ]
                },

                "SmallSignal": {
                    "equations": [
                        Eq(Is["Vp"], (Vs["Vp"] - Vs["Vn"]) * self.values.get("I_Vp_0", 0) / 
                           (kB_e * self.values["T"])),
                        *Component.ZeroCurrentSum(Is),
                    ],
                    "conditions": [
                        #Is["Vp"] + self.values.get("I_Vp_0", 0) > 0,
                        
                        #(self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) >= self.values["Vd"],

                        [
                            (self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) >= self.values["Vd"],
                            (Vs["Vp"] - Vs["Vn"]) > -self.values["Vd"],
                        ],
                        #[
                        #    (self.values.get("Vp_0", 0) - self.values.get("Vn_0", 0)) >= self.values["Vd"],
                        #    (Vs["Vp"] - Vs["Vn"]) <= -self.values["Vd"],
                        #],
                        
                    ]
                }

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



                "AC+DC": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [
                        Vs["Vb"] - Vs["Ve"] <= self.values["Vdf"],
                        Vs["Vb"] - Vs["Vc"] <= self.values["Vdr"],
                    ]
                },

                "SmallSignal": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [
                        self.values.get("Vb_0", 0) - self.values.get("Ve_0", 0) < self.values["Vdf"],
                        self.values.get("Vb_0", 0) - self.values.get("Vc_0", 0) < self.values["Vdr"],
                    ]
                }

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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [
                        self.values.get("Vb_0", 0) - self.values.get("Ve_0", 0) >= self.values["Vdf"],
                        self.values.get("Vb_0", 0) - self.values.get("Vc_0", 0) < self.values["Vdr"],
                    ]
                }
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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [
                        self.values.get("Vb_0", 0) - self.values.get("Ve_0", 0) < self.values["Vdf"],
                        self.values.get("Vb_0", 0) - self.values.get("Vc_0", 0) >= self.values["Vdr"],
                    ]
                }
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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [
                        self.values.get("Vb_0", 0) - self.values.get("Ve_0", 0) >= self.values["Vdf"],
                        self.values.get("Vb_0", 0) - self.values.get("Vc_0", 0) >= self.values["Vdr"],
                    ]
                }
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



                "AC+DC": {
                    "equations": [
                        *Component.OpenConnection(Vs, Is),
                    ],
                    "conditions": [
                        Vs["Ve"] - Vs["Vb"] <= self.values["Vdf"],
                        Vs["Vc"] - Vs["Vb"] <= self.values["Vdr"],
                    ]
                },

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [

                    ]
                }
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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [

                    ]
                }
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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [

                    ]
                }
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



                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Vs["V"], self.values["Vac"]),
                    ],
                    "conditions": [

                    ]
                }
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

                "Laplace": {
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

                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"] / self.values["Av"],
                           Vs["V+"] - Vs["V-"]),
                    ],
                    "conditions": [
                        self.values.get("Vop_0", 0) < self.values.get("Vcc_0", 0),
                        self.values.get("Vop_0", 0) > self.values.get("Vee_0", 0),
                        
                        Vs["Vop"] < Vs["Vcc"],
                        Vs["Vop"] > Vs["Vee"],
                    ]
                }

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

                "Laplace": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], Vs["Vcc"] / s)
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] >= Vs["Vcc"] / self.values["Av"],
                    ]
                },

                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], 0)
                    ],
                    "conditions": [
                        self.values.get("Vop_0", 0) >= self.values.get("Vcc_0", 0),
                    ]
                }

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

                "Laplace": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], Vs["Vee"] / s)
                    ],
                    "conditions": [
                        Vs["V+"] - Vs["V-"] <= Vs["Vee"] / self.values["Av"],
                    ]
                },

                "AC+DC": {
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

                "SmallSignal": {
                    "equations": [
                        Eq(Is["V+"], 0),
                        Eq(Is["V-"], 0),
                        Eq(Is["Vcc"], 0),
                        Eq(Is["Vee"], 0),
                        Eq(Vs["Vop"], 0)
                    ],
                    "conditions": [
                        self.values.get("Vop_0", 0) <= self.values.get("Vee_0", 0),
                    ]
                }

            },

        }
