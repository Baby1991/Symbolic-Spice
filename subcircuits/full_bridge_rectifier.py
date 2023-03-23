from subcircuits.subcircuits import *

full_bridge_rectifier = Circuit()
Vd = full_bridge_rectifier.generic("Vd", 0.6)
full_bridge_rectifier.element(
                                Diode("D1", {"Vp" : "Vin1", "Vn" : "Vout+"}, Vd=Vd),
                                Diode("D2", {"Vp" : "Vout-", "Vn" : "Vin2"}, Vd=Vd),
                                Diode("D3", {"Vp" : "Vout-", "Vn" : "Vin1"}, Vd=Vd),
                                Diode("D4", {"Vp" : "Vin2", "Vn" : "Vout+"}, Vd=Vd),
)

semi_real_full_bridge_rectifier = Circuit()
Vd = semi_real_full_bridge_rectifier.generic("Vd", 0.6)
Is = semi_real_full_bridge_rectifier.generic("Is", 1e-9)
semi_real_full_bridge_rectifier.element(
                                SemiRealDiode("D1", {"Vp" : "Vin1", "Vn" : "Vout+"}, Vd=Vd, Is=Is),
                                SemiRealDiode("D2", {"Vp" : "Vout-", "Vn" : "Vin2"}, Vd=Vd, Is=Is),
                                SemiRealDiode("D3", {"Vp" : "Vin2", "Vn" : "Vout+"}, Vd=Vd, Is=Is),
                                SemiRealDiode("D4", {"Vp" : "Vout-", "Vn" : "Vin1"}, Vd=Vd, Is=Is),
)