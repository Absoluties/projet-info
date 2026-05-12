from piece import Piece
from fou import Fou
from tour import Tour
from dame import Dame
from cavalier import Cavalier
from pion import Pion


class Roi(Piece):
    def __init__(self, x, y, couleur):
        super().__init__(x, y, couleur)
        self.representation = "♚" if couleur else "♔"  # 0: Blanc ; 1: Noir

    def cases_atteignables(self, plateau: list) -> list:
        L = []
        i, j = self.position
        for k in range(i - 1, i + 2):
            for l in range(j - 1, j + 2):
                if (k, l) != (i, j) and (
                    plateau[k][l] == None or plateau[k][l].couleur != self.couleur
                ):
                    L.append((k, l))
        return L

    def test_menace_pion_cavalier(self, position:tuple[int,int], type_piece:type, plateau:list):
        x,y = position
        if 0 <= x < 8 and 0 <= y < 8:
            if type(piece:=plateau[x][y]) is type_piece:
                if piece.couleur != self.couleur:
                    return True
        return False

    def test_menace_dame_fou_tour_roi(self, direction:tuple[int,int], types_pieces:type, plateau:list):
        x,y = self.position
        while 0 <= (x:=x+direction[0]) < 8 and 0 <= (y:=y+direction[1]) < 8:
            piece = plateau[x][y]
            if not piece is None:
                if type(piece) in types_pieces:
                    print(x,y)
                    return piece.couleur != self.couleur
                return False
        return False


    def echec(self, plateau: list) -> bool:
        positions_menaces_cavalier = [(self.position[0]+i,self.position[1]+j) for i,j in ((-1,2), (1,2), (-1,-2), (1,-2), (2,-1), (2,1), (-2,-1), (-2,1))]
        positions_menaces_pion = [(self.position[0]+i,self.position[1] + (-1) ** self.couleur) for i in (1,-1)]

        for position in positions_menaces_cavalier:
            if self.test_menace_pion_cavalier(position, Cavalier, plateau):
                return True
        for position in positions_menaces_pion:
            if self.test_menace_pion_cavalier(position, Pion, plateau):
                return True
        
        directions_tour = ((-1,0),(0,-1),(0,1),(1,0))
        directions_fou = ((-1,-1),(-1,1),(1,-1),(1,1))
        
        for direction in directions_tour:
            if self.test_menace_dame_fou_tour_roi(direction, (Tour, Dame, Roi), plateau):
                return True
        
        for direction in directions_fou:
            if self.test_menace_dame_fou_tour_roi(direction, (Fou, Dame, Roi), plateau):
                return True
        
        return False
        
            
            
        

        


    # TODO rédiger la méthode echec qui regarde si le roi est en échec -> Voir si echec doit être écrit ici ce n'est peut être pas le plus judicieux

    # TODO rédiger une méthode echec_et_mat qui regarde si le roi est en echec et mat (i.e. roi.echec() = True et cases_atteignables = [])
