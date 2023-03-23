import pickle
import os

def saveModel(name, type, compiled, model, simulatorState):
    if not os.path.exists("__models__"):
        os.makedirs("__models__")
    with open(os.path.join("__models__", f"{name}_{type}.pickle"), "wb") as filehandler:
        pickle.dump((compiled, simulatorState), filehandler)
    
def loadModel(name, type):
    with open(os.path.join("__models__", f"{name}_{type}.pickle"), "rb") as filehandler:
        compiled, model, simulatorState = pickle.load(filehandler)
    return (compiled, simulatorState)