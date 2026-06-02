from partie import Partie
from piece import Piece
from abc import abstractmethod, ABCMeta

class IA(ABCMeta):
    def __init__(self, niveau:int, partie:Partie):
        self.partie = partie
        match niveau:
            case 0:
                ...
            case 1:
                ...
            case 2:
                ...
            case 3:
                ...
            case _:
                RuntimeError()
    
    def minmax():
        ...
    
    @abstractmethod
    def choisir_coup() -> tuple[tuple[int,int], tuple[int,int]]:
        ...
    
    
