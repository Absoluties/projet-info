from piece import Piece

class Fou(Piece):
    def __init__(self, x, y, couleur):
        super().__init__(x, y, couleur)
        self.representation = '♝' if couleur else '♗' # 0: Blanc ; 1: Noir

    def cases_atteignables(plateau:list):
        return None