from piece import Piece

class Pion(Piece):
    def __init__(self, x, y, couleur:int):
        super().__init__(x, y, couleur)
        self.representation = '♟' if couleur else '♙' # 0: Blanc ; 1: Noir

    def cases_atteignables(plateau:list):
        return None
