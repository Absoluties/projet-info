from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Roi(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♚" if couleur else "♔"  # 0: Blanc ; 1: Noir
        self.type = 'R'


    def cases_atteignables(self, plateau: list) -> list:
        L = []
        x, y = self.position
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                x2 = x + dx
                y2 = y + dy
                if not (0 <= x2 < 8 and 0 <= y2 < 8):
                    continue
                piece = plateau[x2][y2]
                if piece is None or piece.couleur != self.couleur:
                    L.append((x2, y2))
        # Le roi ne peut pas se mettre sur une case menacée
        return self.filtrer_coups_forces_clouage(L, plateau)
