from src.geometry import Ge
from src.source import So
from src.scorer import Sc



def getFilePath(elemName: str, basename:str="autotopas") -> str:
    if elemName == "World":
        return Ge.getFilePath(elemName, basename)
    
    if elemName in Ge["_modified"]:
        return Ge.getFilePath(elemName, basename)
    
    if elemName in So["_modified"]:
        return So.getFilePath(elemName, basename)
    
    if elemName in Sc["_modified"]:
        return Sc.getFilePath(elemName, basename)

    raise ValueError(f"Element '{elemName}' not found in any modified lists.")