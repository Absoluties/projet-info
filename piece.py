from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from partie import Partie

class Piece(ABC):
    def __init__(self, x:int, y:int, couleur:int, partie:'Partie'):
        self.position = (x, y)
        self.couleur = couleur
        self.partie = partie
        self.coups_possibles = []
        self.representation = ""
        self.type = None

    def test_menace_pion_cavalier(self, position:tuple[int,int], type_piece:type):
        x,y = position
        if 0 <= x < 8 and 0 <= y < 8:
            piece:Piece = self.partie.plateau[x][y]
            if not piece is None and piece.type == type_piece:
                if piece.couleur != self.couleur:
                    return True
        return False

    def test_menace_dame_fou_tour_roi(self, direction:tuple[int,int], types_pieces:type, max_distance:int=7):
        x,y = self.position
        distance = 1
        while distance <= max_distance and 0 <= (x:=x+direction[0]) < 8 and 0 <= (y:=y+direction[1]) < 8:
            distance += 1
            piece:Piece = self.partie.plateau[x][y]
            if not piece is None:
                if piece.type in types_pieces:
                    return piece.couleur != self.couleur
                return False
        return False

    def attaquee(self) -> bool:
        positions_menaces_cavalier = [(self.position[0]+i,self.position[1]+j) for i,j in ((-1,2), (1,2), (-1,-2), (1,-2), (2,-1), (2,1), (-2,-1), (-2,1))]
        positions_menaces_pion = [(self.position[0] + (-1) ** self.couleur,self.position[1] + i) for i in (1,-1)]

        for position in positions_menaces_cavalier:
            if self.test_menace_pion_cavalier(position, 'C', self.partie.plateau):
                return True
        for position in positions_menaces_pion:
            if self.test_menace_pion_cavalier(position, 'P', self.partie.plateau):
                return True
        
        directions_tour = ((-1,0),(0,-1),(0,1),(1,0))
        directions_fou = ((-1,-1),(-1,1),(1,-1),(1,1))
        
        for direction in directions_tour:
            if self.test_menace_dame_fou_tour_roi(direction, ('T', 'D'), self.partie.plateau):
                return True
            if self.test_menace_dame_fou_tour_roi(direction, ('R'), self.partie.plateau, 1):
                return True
        
        for direction in directions_fou:
            if self.test_menace_dame_fou_tour_roi(direction, ('F', 'D'), self.partie.plateau):
                return True
            if self.test_menace_dame_fou_tour_roi(direction, ('R'), self.partie.plateau, 1):
                return True
                    
        return False

    def filtrer_coups_forces_clouage(self, coups:list) -> list:
        '''
        Ici on vérifie si les coups générés précedemment génèrent des échecs, auquel cas il faut les ignorer.
        Ainsi on simule les coups et on utilise la méthode attaquee() des rois.
        '''
        coups_filtres = []
        x1, y1 = self.position

        for x2, y2 in coups:
            piece_deplacee:Piece = self.partie.plateau[x1][y1]
            piece_capturee:Piece = self.partie.plateau[x2][y2]

            self.partie.plateau[x1][y1] = None
            self.partie.plateau[x2][y2] = piece_deplacee

            ancienne_position = self.position
            self.position = (x2, y2)

            roi:Piece = self.partie.rois[self.couleur]

            if not roi.attaquee(self.partie.plateau):
                coups_filtres.append((x2, y2))

            self.partie.plateau[x1][y1] = piece_deplacee
            self.partie.plateau[x2][y2] = piece_capturee

            self.position = ancienne_position
        return coups_filtres

    @abstractmethod
    def cases_atteignables(self) -> list:
        """Détermine les cases qu'une pièce peut atteindre
        pour ensuite ne permettre de jouer que les coups légaux.

        Renvoie une liste de couples correspondants aux coordonnées des cases atteignables"""
        pass
