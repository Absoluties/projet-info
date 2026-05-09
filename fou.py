from piece import Piece


class Fou(Piece):
    def __init__(self, x, y, couleur):
        super().__init__(x, y, couleur)
        self.representation = "♝" if couleur else "♗"  # 0: Blanc ; 1: Noir

    def cases_atteignables(self, plateau: list):
        L = []
        i, j = self.position
        k = 1
        while i + k < 8 and j + k < 8 and plateau[i + k][j + k] == None:  # en bas à droite
            L.append((i + k, j + k))
            k += 1
        k = 1
        while i - k > 0 and j + k < 8 and plateau[i - k][j + k] == None:  # en haut à droite
            L.append((i - k, j + k))
            k += 1
        k = 1
        while i - k > 0 and j - k > 0 and plateau[i - k][j - k] == None:  # en haut à gauche
            L.append((i - k, j - k))
            k += 1
        k = 1
        while i + k < 8 and j - k > 0 and plateau[i + k][j - k] == None:  # en bas à gauche
            L.append((i + k, j - k))
            k += 1
        return L
