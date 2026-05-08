class Piece:
    def __init__(self, x, y, clr):
        self.position = (x, y)
        self.couleur = clr
        self.coup_possible = []

    def get_position(self):
        return self.position

    def case_atteignables() -> list:
        return None
