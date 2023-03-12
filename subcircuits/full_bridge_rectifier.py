from subcircuits.subcircuits import *

full_bridge_rectifier = Circuit()
Vd = full_bridge_rectifier.generic("Vd", 0.6)
full_bridge_rectifier.element(
                                Diode("D1", {"Vp" : "Vin1", "Vn" : "Vout+"}, Vd=Vd),
                                Diode("D2", {"Vp" : "Vout-", "Vn" : "Vin2"}, Vd=Vd),
                                Diode("D3", {"Vp" : "Vin2", "Vn" : "Vout+"}, Vd=Vd),
                                Diode("D4", {"Vp" : "Vout-", "Vn" : "Vin1"}, Vd=Vd),
)