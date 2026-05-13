from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Pion(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♟" if couleur else "♙"  # 0: Blanc ; 1: Noir
        self.type = 'P'

    def cases_atteignables(self):
        L = []
        i, j = self.position
        direction = 1 if self.couleur == 0 else -1
        ligne_depart = 1 if self.couleur == 0 else 6
        # avance simple
        if 0 <= i + direction < 8:
            if self.partie.plateau[i + direction][j] is None:
                L.append((i + direction, j))
                # avance double
                if i == ligne_depart and self.partie.plateau[i + 2 * direction][j] is None:
                    L.append((i + 2 * direction, j))
        # captures diagonales
        for dj in (-1, 1):
            x = i + direction
            y = j + dj
            if 0 <= x < 8 and 0 <= y < 8:
                piece = self.partie.plateau[x][y]
                if piece is not None and piece.couleur != self.couleur:
                    L.append((x, y))
        # prise en passant
        if self.partie.historique:
            depart, arrivee = self.partie.historique[-1]
            x1, y1 = depart
            x2, y2 = arrivee
            piece:Piece = self.partie.plateau[x2][y2]
            if (piece is not None and piece.type == 'P' and piece.couleur != self.couleur and abs(x2 - x1) == 2 and x2 == i and abs(y2 - j) == 1): # Le pion adverse a fait un saut double et arrive à côté du pion
                L.append((i + direction, y2))

        return self.filtrer_coups_forces_clouage(L, self.partie.plateau)
