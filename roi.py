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
        if self.position == (7 * self.couleur, 4) and not [coup for coup in self.partie.historique if coup[0] == (7 * self.couleur, 4)]: # Le roi n'a pas bougé
            if not self.attaquee():
                x, y = self.position
                for direction in (-1,1):
                    tour:Piece = self.partie.plateau[x][(7 + direction * 7) // 2]
                    if not tour is None and tour.type == 'T' and tour.couleur == self.couleur and not [coup for coup in self.partie.historique if coup[0] == (7 * tour.couleur, (7 + direction * 7) // 2)]: # La tour n'a pas bougé
                        
                        for i in range(1,3):
                            j = direction * i
                            print(f'Test case {(x,y+j)}')

                            if not self.partie.plateau[x][y+j] is None: # il faut des cases vides non menacées pour roquer
                                break

                            self.partie.plateau[x][y+j], self.partie.plateau[self.position[0]][self.position[1]] = self.partie.plateau[self.position[0]][self.position[1]], self.partie.plateau[x][y+j]
                            self.position = (x,y+j)

                            attaquee = self.attaquee()
                            print(f'Case attaquée : {attaquee}')

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
