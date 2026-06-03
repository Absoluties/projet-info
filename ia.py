from typing import TYPE_CHECKING
from piece import Piece
from abc import abstractmethod, ABC

if TYPE_CHECKING:
    from partie import Partie


class IA(ABC):
    def __init__(self, niveau: int, partie: "Partie"):
        self.partie = partie
        self.niveau = niveau

    @abstractmethod
    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]: ...
