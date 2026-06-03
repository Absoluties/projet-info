import copy
import sys
import os
from piece import Piece
from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING
from ia import IA

if TYPE_CHECKING:
    from partie import Partie


class IA_fort(IA):
    def __init__(self, niveau: int, partie: "Partie"):
        super().__init__(niveau, partie)

    def _get_tous_coups_legaux(
        self, partie_etat: "Partie", couleur: int
    ) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        """Parcourt le plateau et récupère tous les coups légaux possibles pour une couleur donnée"""
        coups = []
        for i in range(8):
            for j in range(8):
                piece = partie_etat.plateau[i][j]
                if piece is not None and piece.couleur == couleur:
                    # cases_atteignables() élimine déjà le clouage et les échecs automatiques
                    for case_destination in piece.cases_atteignables():
                        coups.append((piece.position, case_destination))
        return coups

    def _evaluer(self, partie_etat: "Partie", couleur_ia: int) -> int:
        """Fonction d'évaluation matérielle basée sur les types de pièces du projet"""
        valeurs = {"P": 10, "C": 30, "F": 30, "T": 50, "D": 90, "R": 900}
        score = 0
        for i in range(8):
            for j in range(8):
                piece = partie_etat.plateau[i][j]
                if piece is not None:
                    valeur_piece = valeurs.get(piece.type, 0)
                    if piece.couleur == couleur_ia:
                        score += valeur_piece
                    else:
                        score -= valeur_piece
        return score

    def _minimax(
        self,
        partie_etat: "Partie",
        profondeur: int,
        alpha: float,
        beta: float,
        est_max: bool,
        couleur_ia: int,
    ) -> int:
        # determiner qui doit vitruellement jouer
        couleur_actuelle = couleur_ia if est_max else (1 - couleur_ia)
        coups_legaux = self._get_tous_coups_legaux(partie_etat, couleur_actuelle)

        # Condition d'arrêt : profondeur max atteinte ou situation de Mat
        if profondeur == 0 or not coups_legaux:
            if not coups_legaux:
                roi = partie_etat.rois[couleur_actuelle]
                if roi.attaquee():
                    # Échec et mat : gain extremement faible/élevé selon si c'est virtuellement le tour de l'IA ou du joueur
                    return -10000 - profondeur if est_max else 10000 + profondeur
                else:
                    # Pat (Match nul)
                    return 0
            return self._evaluer(partie_etat, couleur_ia)

        if est_max:
            val_max = float("-inf")
            for coup in coups_legaux:
                partie_virtuelle = copy.deepcopy(partie_etat)
                partie_virtuelle.jouer_coup(coup)

                score = self._minimax(
                    partie_virtuelle, profondeur - 1, alpha, beta, False, couleur_ia
                )
                val_max = max(val_max, score)
                alpha = max(alpha, val_max)
                if beta <= alpha:
                    break  # Élagage Bêta
            return val_max
        else:
            val_min = float("inf")
            for coup in coups_legaux:
                partie_virtuelle = copy.deepcopy(partie_etat)
                partie_virtuelle.jouer_coup(coup)

                score = self._minimax(
                    partie_virtuelle, profondeur - 1, alpha, beta, True, couleur_ia
                )
                val_min = min(val_min, score)
                beta = min(beta, val_min)
                if beta <= alpha:
                    break  # Élagage Alpha
            return val_min

    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Polymorphisme, métode adaptée à minimax"""
        couleur_ia = self.partie.tour % 2
        coups_legaux = self._get_tous_coups_legaux(self.partie, couleur_ia)

        if not coups_legaux:
            return None

        meilleur_coup = None
        meilleur_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for coup in coups_legaux:
            partie_virtuelle = copy.deepcopy(self.partie)
            partie_virtuelle.jouer_coup(coup)
            # Le coup joué par l'IA amène au tour de l'adversaire (est_max = False)
            # self.niveau détermine la profondeur max (ex: 3 pour calculer 3 coups à l'avance)
            score = self._minimax(partie_virtuelle, self.niveau - 1, alpha, beta, False, couleur_ia)

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)

        return meilleur_coup
