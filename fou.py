from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Fou(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♝" if couleur else "♗"  # 0: Blanc ; 1: Noir
        self.type = 'F'

    def cases_atteignables(self):
        L = []
        x, y = self.position
        directions = [
            (1, 1), (1, -1), (-1, 1), (-1, -1)  # fou
        ]
        for dx, dy in directions:
            k = 1
            while True:
                i = x + k * dx
                j = y + k * dy
                if not (0 <= i < 8 and 0 <= j < 8):
                    break
                piece = self.partie.plateau[i][j]
                if piece is None:
                    L.append((i, j))
                else:
                    if piece.couleur != self.couleur:
                        L.append((i, j))
                    break
                k += 1
        return self.filtrer_coups_forces_clouage(L, self.partie.plateau)
