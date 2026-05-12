from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Fou(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♝" if couleur else "♗"  # 0: Blanc ; 1: Noir
        self.type = 'F'

    def cases_atteignables(self, plateau: list, historique=None):
        L = []
        i, j = self.position
        k = 1
        while (
            i + k < 8
            and j + k < 8
            and (plateau[i + k][j + k] == None or plateau[i + k][j + k].couleur != self.couleur)
        ):  # en bas à droite
            L.append((i + k, j + k))
            k += 1
            if plateau[i + k][j + k] != None:
                break
        k = 1
        while (
            i - k > 0
            and j + k < 8
            and (plateau[i - k][j + k] == None or plateau[i - k][j + k].couleur != self.couleur)
        ):  # en haut à droite
            L.append((i - k, j + k))
            k += 1
            if plateau[i - k][j + k] != None:
                break
        k = 1
        while (
            i - k > 0
            and j - k > 0
            and (plateau[i - k][j - k] == None or plateau[i - k][j - k].couleur != self.couleur)
        ):  # en haut à gauche
            L.append((i - k, j - k))
            k += 1
            if plateau[i - k][j - k] != None:
                break
        k = 1
        while (
            i + k < 8
            and j - k > 0
            and (plateau[i + k][j - k] == None or plateau[i - k][j + k].couleur != self.couleur)
        ):  # en bas à gauche
            L.append((i + k, j - k))
            k += 1
            if plateau[i + k][j - k] != None:
                break
        return self.filtrer_coups_forces_clouage(L, plateau)
