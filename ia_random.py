from ia import IA
from random import choice, choices
from piece import Piece

class IARandom(IA):
    def choisir_coup(self):
        pieces_candidates:list[Piece] = []
        poids:list[float] = []
        cases_candidates:list[tuple[tuple[int,int]]] = []
        for ligne in self.partie.plateau:
            for piece in ligne:
                if piece is not None:
                    pieces_candidates.append(piece)
                    cases_candidates.append(tuple(piece.cases_atteignables()))
                    poids.append(len(cases_candidates))
        # On est sûr de choisir au moins un coupn, sinon la partie serait arrêtée
        indice_piece = choices(range(len(pieces_candidates)), poids)[0]
        piece_choisie = pieces_candidates[indice_piece]
        case_choisie = choice(cases_candidates[indice_piece])
        return piece_choisie.position, case_choisie