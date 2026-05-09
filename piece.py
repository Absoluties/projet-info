from abc import ABC, abstractmethod


class Piece:
    def __init__(self, x, y, couleur):
        self.position = (x, y)
        self.couleur = couleur
        self.coups_possibles = []
        self.representation = " "

    """def get_position(self):
        return self.position
    
    #Méthode à revoir, je l'ai écrit ainsi comme je savais pas trop comment elle serait utilisée
    def set_position(self, x, y):
        if 0 <= x <= 8 and 0 <= y <= 8 :
            return self.position
        else :
            return (0, 0)"""

    @abstractmethod
    def case_atteignables() -> list:
        """Détermine les cases qu'une pièce peut atteindre
        pour ensuite ne permettre de jouer que les coups légaux.

        Renvoie une liste de couples correspondants aux coordonnées des cases atteignables"""
        pass
