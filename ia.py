from partie import Partie
from piece import Piece
from abc import abstractmethod, ABCMeta

class IA(ABCMeta):
    def __init__(self, niveau:int, partie:Partie):
        self.partie = partie
        self.niveau = niveau
    
    @abstractmethod
    def choisir_coup(self) -> tuple[tuple[int,int], tuple[int,int]]:
        ...
    
    
