from piece import Piece
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from partie import Partie

class Roi(Piece):
    def __init__(self, x, y, couleur, partie:'Partie'):
        super().__init__(x, y, couleur, partie)
        self.representation = "♚" if couleur else "♔"  # 0: Blanc ; 1: Noir
        self.type = 'R'

    def ajouter_cases_roque(self):
        L = []

        if True not in self.partie.roques_possibles[self.couleur]:
            return L

        if not self.attaquee():
            x, y = self.position
            for direction in (-1,1): # -1 grand | 1 petit
                if self.partie.roques_possibles[self.couleur][(1+direction)//2]:
                    for i in range(1,3):
                        j = direction * i

                        if not self.partie.plateau[x][y+j] is None: # il faut des cases vides non menacées pour roquer
                            break

                        # On doit déplacer le Roi pour de vrai pour tester son échec
                        self.partie.plateau[x][y+j], self.partie.plateau[self.position[0]][self.position[1]] = self.partie.plateau[self.position[0]][self.position[1]], self.partie.plateau[x][y+j]
                        self.position = (x,y+j)

                        attaquee = self.attaquee()

                        self.partie.plateau[x][y+j], self.partie.plateau[x][y] = self.partie.plateau[x][y], self.partie.plateau[x][y+j]
                        self.position = (x,y)

                        if attaquee:
                            break
                    else: # aucun problème rencontré
                        L.append((x, y+2*direction))
        return L

    def cases_atteignables(self) -> list:
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
                piece = self.partie.plateau[x2][y2]
                if piece is None or piece.couleur != self.couleur:
                    L.append((x2, y2))
        # Le roi ne peut pas se mettre sur une case menacée
        return self.filtrer_coups_forces_clouage(L) + self.ajouter_cases_roque()
