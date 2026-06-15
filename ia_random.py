from ia import IA
from random import choice, choices
from piece import Piece


class IARandom(IA):
    """IA choisissant un coup aléatoire pondéré par le nombre de coups disponibles de chaque pièce.
    Auteur : Valentin"""
    
    def __init__(self, niveau: int, partie: "Partie"):
        super().__init__(niveau, partie)
    
    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Choisit un coup aléatoire pondéré par le nombre de coups disponibles de chaque pièce."""
        pieces_candidates: list[Piece] = []
        poids: list[float] = []
        cases_candidates: list[list[tuple[int, int]]] = []

        for ligne in self.partie.plateau:
            for piece in ligne:
                if piece is not None and piece.couleur == (self.partie.tour % 2):
                    if cases_atteignables_piece := piece.cases_atteignables():
                        pieces_candidates.append(piece)
                        cases_candidates.append(cases_atteignables_piece)
                        poids.append(len(cases_candidates))

        # On est sûr de choisir au moins un coup, sinon la partie serait déjà arrêtée
        indice_piece = choices(range(len(pieces_candidates)), poids)[0]
        piece_choisie = pieces_candidates[indice_piece]
        case_choisie = choice(cases_candidates[indice_piece])

        return piece_choisie.position, case_choisie
