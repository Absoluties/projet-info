from abc import ABC, abstractmethod
from partie import Partie
from roi import Roi

class Piece(ABC):
    def __init__(self, x:int, y:int, couleur:int, partie:Partie):
        self.position = (x, y)
        self.couleur = couleur
        self.partie = partie
        self.coups_possibles = []
        self.representation = " "

    """def get_position(self):
        return self.position
    
    #Méthode à revoir, je l'ai écrit ainsi comme je savais pas trop comment elle serait utilisée
    def set_position(self, x, y):
        if 0 <= x < 8 and 0 <= y < 8 :
            return self.position
        else :
            return (0, 0)"""

    def filter_coups_forces_clouage(self,coups:list,plateau:list) -> list:
        coups_filtres = []
        for coup in coups:
            plateau_copie = plateau.copy()
            plateau_copie[self.position[0]][self.position[1]], plateau_copie[self.coup[0]][self.coup[1]] = None, plateau_copie[self.position[0]][self.position[1]]
            roi:Roi = None
            if self.couleur: # Noir
                roi = plateau_copie[self.partie.position_roi_noir]
            else:
                roi = plateau_copie[self.partie.position_roi_blanc]
            if not roi.echec(plateau_copie):
                coups_filtres.append(coup)
        return coups_filtres

    @abstractmethod
    def cases_atteignables(self, plateau:list) -> list:
        """Détermine les cases qu'une pièce peut atteindre
        pour ensuite ne permettre de jouer que les coups légaux.

        Renvoie une liste de couples correspondants aux coordonnées des cases atteignables"""
        pass
