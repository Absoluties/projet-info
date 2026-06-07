from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Pion(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♟" if couleur else "♙"  # 0: Blanc ; 1: Noir
        self.type = 'P'

    def cases_atteignables(self) -> list[tuple[int,int]]:
        """Retourne les cases atteignables : avance simple/double, captures diagonales et prise en passant."""
        L = []
        i, j = self.position
        direction = 1 if self.couleur == 0 else -1
        ligne_depart = 1 if self.couleur == 0 else 6
        # Avance simple
        if 0 <= i + direction < 8:
            if self.partie.plateau[i + direction][j] is None:
                L.append((i + direction, j))
                # Avance double depuis la rangée de départ
                if i == ligne_depart and self.partie.plateau[i + 2 * direction][j] is None:
                    L.append((i + 2 * direction, j))
        # Captures diagonales
        for dj in (-1, 1):
            x = i + direction
            y = j + dj
            if 0 <= x < 8 and 0 <= y < 8:
                piece_sur_case:Piece|None = self.partie.plateau[x][y]
                if piece_sur_case is not None and piece_sur_case.couleur != self.couleur:
                    L.append((x, y))
        # Prise en passant : le dernier coup adverse était un saut double d'un pion adjacent
        if self.partie.historique:
            depart, arrivee = self.partie.historique[-1]
            x1, y1 = depart
            x2, y2 = arrivee
            piece_sur_case:Piece|None = self.partie.plateau[x2][y2]
            if (piece_sur_case is not None and piece_sur_case.type == 'P' and piece_sur_case.couleur != self.couleur and abs(x2 - x1) == 2 and x2 == i and abs(y2 - j) == 1):
                L.append((i + direction, y2))

        return self.filtrer_coups_forces_clouage(L)