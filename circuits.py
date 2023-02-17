from circuit import Circuit

Gnd = 0

class Circuits():

    circuits = {}
    main = None

    def setMain(name):
        main = Circuits.circuits[name]
        return main

    def newCircuit(name):
        if name in Circuits.circuits.keys():
            raise Exception("Circuit Alreadt Exists")
        circuit = Circuit()
        if Circuits.circuits == {}:
            Circuits.main = circuit
        Circuits.circuits.update({name : circuit})
        return circuit
    
    def compile():
        return Circuits.main()