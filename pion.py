from piece import Piece


class Pion(Piece):
    def __init__(self, x, y, clr, id):
        super().__init__(x, y, clr)
        self.id = id

    def cases_atteignables(self, plateau):
        pos = self.position

        return None
