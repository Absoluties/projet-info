# écrit par Valentin
from typing import TYPE_CHECKING
from piece import Piece
from abc import abstractmethod, ABC

if TYPE_CHECKING:
    from partie import Partie


class IA(ABC):
    """Classe abstraite définissant l'interface commune à toutes les IA."""

    def __init__(self, niveau: int, partie: "Partie"):
        self.partie = partie
        self.niveau = niveau

    @abstractmethod
    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Retourne le coup choisi sous la forme (position_départ, position_arrivée)."""
        ...
