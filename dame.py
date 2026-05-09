from piece import Piece


class Dame(Piece):
    def __init__(self, x, y, couleur):
        super().__init__(x, y, couleur)
        self.representation = "♛" if couleur else "♕"  # 0: Blanc ; 1: Noir

    def cases_atteignables(self, plateau: list):
        """Détermine les cases où la dame peut aller"""
        L = []  # liste des cases atteignables : à remplir
        i, j = self.position
        # On regarde d'abord les lignes et les colonnes
        # On regarde à i fixé
        k = 1
        while j + k < 8 and (
            plateau[i][j + k] == None or plateau[i][j + k].couleur != self.couleur
        ):  # on regarde à droite
            L.append((i, j + k))
            k += 1
            if plateau[i][j + k] != None:
                break
        k = 1
        while j - k > 0 and (
            plateau[i][j - k] == None or plateau[i][j - k].couleur != self.couleur
        ):  # on regarde à gauche
            L.append((i, j - k))
            k += 1
            if plateau[i][j - k] != None:
                break
        # On regarde maintenant à j fixé
        k = 1
        while i + k < 8 and (
            plateau[i + k][j] == None or plateau[i + k][j].couleur != self.couleur
        ):  # on regarde au dessus
            L.append((i + k, j))
            k += 1
            if plateau[i + k][j] != None:
                break
        k = 1
        while i - k > 0 and (
            plateau[i - k][j] == None or plateau[i - k][j].couleur != self.couleur
        ):  # on regarde en dessous
            L.append((i - k, j))
            k += 1
            if plateau[i - k][j] != None:
                break
        # On regarde maintenant les diagonales
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
        return L
