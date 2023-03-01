from sympy import Eq

class Node:
    
    def __init__(self, symbol):
        self.symbol = symbol
        self.currents = set()

    def addCurrent(self, symbol):
        self.currents.add(symbol)

    def __call__(self):
        return self.symbol

    def equations(self):
        eq = 0
        for current in self.currents:
            eq += current
        return Eq(eq, 0)