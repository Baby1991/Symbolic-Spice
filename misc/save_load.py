import pickle
import os

def saveModel(name, type, model):
    if not os.path.exists("__models__"):
        os.makedirs("__models__")
    with open(os.path.join("__models__", f"{name}_{type}_model.pickle"), "wb") as filehandler:
        pickle.dump(model, filehandler)
    
def loadModel(name, type):
    with open(os.path.join("__models__", f"{name}_{type}_model.pickle"), "rb") as filehandler:
        model = pickle.load(filehandler)
    return model
        
        
def saveCompiled(name, compiled):
    if not os.path.exists("__models__"):
        os.makedirs("__models__")
    with open(os.path.join("__models__", f"{name}_compiled.pickle"), "wb") as filehandler:
        pickle.dump(compiled, filehandler)
    
def loadCompiled(name):
    with open(os.path.join("__models__", f"{name}_compiled.pickle"), "rb") as filehandler:
        compiled = pickle.load(filehandler)
    return compiled