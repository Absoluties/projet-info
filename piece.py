
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from partie import Partie


class Piece(ABC):
    """Auteur : Valentin"""
    def __init__(self, x: int, y: int, couleur: int, partie: "Partie"):
        self.position = (x, y)
        self.couleur = couleur  # 0 = Blanc, 1 = Noir
        self.partie = partie
        self.coups_possibles = []
        self.representation = ""
        self.type = ""

    def test_menace_pion_cavalier(self, position: tuple[int, int], type_piece: str, attaquants:list['Piece']):
        """Vérifie si la case donnée contient un ennemi du type spécifié."""
        x, y = position
        if 0 <= x < 8 and 0 <= y < 8:
            piece: Piece | None = self.partie.plateau[x][y]
            if not piece is None and piece.type == type_piece:
                if piece.couleur != self.couleur:
                    attaquants.append(piece)

    def test_menace_dame_fou_tour_roi(
        self,
        direction: tuple[int, int],
        types_pieces: tuple[str, ...],
        max_distance: int,
        attaquants:list['Piece']
    ) -> bool:
        """Parcourt la direction donnée et retourne True si une pièce ennemie des types indiqués est rencontrée."""
        x, y = self.position
        distance = 1
        while (
            distance <= max_distance
            and 0 <= (x := x + direction[0]) < 8
            and 0 <= (y := y + direction[1]) < 8
        ):
            distance += 1
            piece: Piece | None = self.partie.plateau[x][y]
            if not piece is None:
                if piece.type in types_pieces and piece.couleur != self.couleur:
                    attaquants.append(piece) 
                return

    def attaquee(self) -> list['Piece']:
        """Retourne les deux premières pièces du plateau qui attaquent la pièce actuelle. Dans les faits, cette fonction ne sert qu'au roi."""
        attaquants:list[Piece] = []

        positions_menaces_cavalier = [
            (self.position[0] + i, self.position[1] + j)
            for i, j in (
                (-1, 2),
                (1, 2),
                (-1, -2),
                (1, -2),
                (2, -1),
                (2, 1),
                (-2, -1),
                (-2, 1),
            )
        ]
        # (-1)**couleur vaut 1 (blancs) ou -1 (noirs) : sens depuis lequel un pion ennemi peut attaquer
        positions_menaces_pion = [
            (self.position[0] + (-1) ** self.couleur, self.position[1] + i)
            for i in (1, -1)
        ]

        directions_tour = ((-1, 0), (0, -1), (0, 1), (1, 0))
        directions_fou = ((-1, -1), (-1, 1), (1, -1), (1, 1))

        for position in positions_menaces_cavalier:
            self.test_menace_pion_cavalier(position, "C", attaquants)
            if len(attaquants) == 2:
                return attaquants
        for position in positions_menaces_pion:
            self.test_menace_pion_cavalier(position, "P", attaquants)
            if len(attaquants) == 2:
                return attaquants

        for direction in directions_tour:
            self.test_menace_dame_fou_tour_roi(direction, ("T", "D"), 7, attaquants)
            if len(attaquants) == 2:
                return attaquants
            self.test_menace_dame_fou_tour_roi(direction, tuple("R"), 1, attaquants)
            if len(attaquants) == 2:
                return attaquants

        for direction in directions_fou:
            self.test_menace_dame_fou_tour_roi(direction, ("F", "D"), 7, attaquants)
            if len(attaquants) == 2:
                return attaquants
            self.test_menace_dame_fou_tour_roi(direction, tuple("R"), 1, attaquants)
            if len(attaquants) == 2:
                return attaquants

        return attaquants

    def filtrer_coups_forces_clouage(self, coups: list) -> list:
        """Filtre les coups qui laisseraient le roi allié en échec (clouage ou mise en échec directe).

        Simule chaque coup temporairement sur le plateau sans passer par jouer_coup.
        """
        x1, y1 = self.position
        x_roi, y_roi = self.partie.rois[self.couleur].position

        if len(self.partie.echecs) == 2 and self.type != 'R': # Seul le roi peut bouger en cas de double échec
            return []

        if len(self.partie.echecs) == 1 and self.type != 'R':
            coups = [coup for coup in coups if coup in self.partie.cases_blocage]

        # Si le roi n'est pas en échec, et qu'on est pas aligné au roi, la pièce n'a pas de coups forcés
        if not self.partie.echecs and abs(x_roi - x1) != abs(y_roi - y1) and (x_roi != x1) and (y_roi != y1):
            return coups

        coups_filtres = []
        for x2, y2 in coups:
            piece_deplacee: Piece | None = self.partie.plateau[x1][y1]
            piece_capturee: Piece | None = self.partie.plateau[x2][y2]

            self.partie.plateau[x1][y1] = None
            self.partie.plateau[x2][y2] = piece_deplacee

            ancienne_position = self.position
            self.position = (x2, y2)

            roi: Piece = self.partie.rois[self.couleur]

            if not roi.attaquee():
                coups_filtres.append((x2, y2))

            self.partie.plateau[x1][y1] = piece_deplacee
            self.partie.plateau[x2][y2] = piece_capturee

            self.position = ancienne_position
        return coups_filtres

    @abstractmethod
    def cases_atteignables(self) -> list[tuple[int, int]]:
        """Retourne la liste des cases légalement atteignables par cette pièce."""
        pass
