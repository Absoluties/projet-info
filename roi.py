from piece import Piece


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

    def echec(plateau: list) -> bool: ...

    # TODO rédiger la méthode echec qui regarde si le roi est en échec -> Voir si echec doit être écrit ici ce n'est peut être pas le plus judicieux

    # TODO rédiger une méthode echec_et_mat qui regarde si le roi est en echec et mat (i.e. roi.echec() = True et cases_atteignables = [])
