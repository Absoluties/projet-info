from piece import Piece


class Pion(Piece):
    def __init__(self, x, y, couleur: int):
        super().__init__(x, y, couleur)
        self.representation = "♟" if couleur else "♙"  # 0: Blanc ; 1: Noir

    def cases_atteignables(self, plateau: list):
        L = []
        i, j = self.position
        if self.couleur == 0:  # pion blanc
            if i + 1 <= 8 and (
                plateau[i + 1][j] == None or plateau[i + 1][j].couleur != self.couleur
            ):
                L.append((i + 1, j))  # on ajoute la case devant
            if i == 1 and (plateau[i + 2][j] == None or plateau[i + 2][j].couleur != self.couleur):
                L.append(
                    (i + 2, j)
                )  # Si le pion est sur sa case initiale il peut aussi avancer de 2 cases
        else:  # pion noir
            if i - 1 >= 0 and (
                plateau[i - 1][j] == None or plateau[i - 1][j].couleur != self.couleur
            ):
                L.append((i - 1, j))  # on ajoute la case devant
            if i == 6 and (plateau[2 - 1][j] == None or plateau[i - 2][j].couleur != self.couleur):
                L.append(
                    (i - 2, j)
                )  # Si le pion est sur sa case initiale il peut aussi avancer de 2 cases
        return None
