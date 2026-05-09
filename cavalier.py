from piece import Piece


class Cavalier(Piece):
    def __init__(self, x, y, couleur):
        super().__init__(x, y, couleur)
        self.representation = "♞" if couleur else "♘"  # 0: Blanc ; 1: Noir

    def cases_atteignables(self, plateau: list):
        L = []
        i, j = self.position
        cases_candidates = [
            (i - 2, j - 1),
            (i - 2, j + 1),
            (i - 1, j - 2),
            (i - 1, j + 2),
            (i + 1, j - 2),
            (i + 1, j + 2),
            (i + 2, j - 1),
            (i + 2, j + 1),
        ]
        for case in cases_candidates:
            if (
                (
                    plateau[case[0]][case[1]] != None
                    or plateau[case[0]][case[1]].couleur != self.couleur
                )
                and 0 <= case[0] <= 8
                and 0 <= case[1] <= 8
            ):
                L.append(case)
        return None
