from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Cavalier(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♞" if couleur else "♘"  # 0: Blanc ; 1: Noir
        self.type = 'C'

    def cases_atteignables(self):
        L = []
        i, j = self.position
        cases_candidates = [
            (i - 2, j - 1),
            (i - 2, j + 1),
            (i - 1, j - 2),
            (i - 1, j + 2),
            (i + 1, j - 2),
            (i + 1, j + 2),
            (i + 2, j - 1),
            (i + 2, j + 1),
        ]
        for case in cases_candidates:
            if 0 <= case[0] < 8 and 0 <= case[1] < 8 and (self.partie.plateau[case[0]][case[1]] is None or self.partie.plateau[case[0]][case[1]].couleur != self.couleur):
                L.append(case)
        return self.filtrer_coups_forces_clouage(L, self.partie.plateau)
