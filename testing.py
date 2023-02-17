from circuits import *
from solver import *

from models import NPN, PNP, Diode, Resistor, VoltageSource, CurrentSource, OpAmp
import sympy as sp

Vcc = 5

var = sp.Symbol("Vin", real=True)

circuit = Circuits.newCircuit("main")
subcircuit = Circuits.newCircuit("sub")

Vin = subcircuit.port("Vin")
Vout = subcircuit.port("Vout")
V1, V2 = subcircuit.nodes("V1", "V2")

subcircuit.elements(
                    Resistor("R1", {"V1" : Vcc, "V2" : V1}, R=1e-6),
                    NPN("Q1", {"Vc" : V1, "Vb" : Vin, "Ve" : Vout}),
                    PNP("Q2", {"Ve" : Vout, "Vb" : Vin, "Vc" : V2}),
                    Resistor("R2", {"V1" : V2, "V2" : -Vcc}, R=1e-6),
)

V1, V2, V3 = circuit.nodes("V1", "V2", "V3")

circuit.elements(
                        VoltageSource("Vg", {"V+" : V1, "V-" : Gnd}, Vdc = var),
                        Resistor("Rg", {"V1" : V1, "V2" : V2}, R = 50),
                        Resistor("Rout", {"V1" : V3, "V2" : Gnd}, R = 50),
                      )

circuit.subcircuit(subcircuit, "amp", {"Vin" : V2, "Vout" : V3})

compiled = Circuits.compile()

print("Nodes: ", compiled["nodes"])
print("Voltages: ", compiled["voltages"])
print("Currents: ", compiled["currents"])

Vout = compiled["voltages"]["Rout"]["V1"]

measurments =   [   
                    (lambda sol : Vout.subs(sol), "Vout"),
                ]


fig, ax = plt.subplots(figsize=[11, 7])
model = Solver.solveDC(compiled, debugLog = False)
#Solver.printModel(model, var)
plotMeasurments(model, -10, 10, 0.1, measurments, var)
plt.legend(loc="best");
plt.grid(True);
plt.show()