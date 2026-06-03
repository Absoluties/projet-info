# écrit par Valentin
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
    """Version évoluée de l'IA utilisant l'algorithme minimax
    avec élagage alpha-beta (ignorer certains coups a priori peu intéressants)"""

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
                    for case_destination in piece.cases_atteignables():
                        coups.append((piece.position, case_destination))
        return coups

    def _evaluer(self, partie_etat: "Partie", couleur_ia: int) -> int:
        """Fonction d'évaluation du gain associé à un coup.
        Ce gain correspond simplement aux pièces encore
        présentes sur l'échiquier pondéré par leurs valeurs.
        La pondération est négative pour le joueur."""
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
        """Algorithme récursif minimax calculant le coup plus avantageux"""
        # determiner qui doit jouer (dans la partie virtuelle sur laquelle l'algorithme calcule)
        couleur_actuelle = couleur_ia if est_max else (1 - couleur_ia)
        coups_legaux = self._get_tous_coups_legaux(partie_etat, couleur_actuelle)

        # Condition d'arrêt : profondeur max atteinte ou situation de Mat
        if profondeur == 0 or not coups_legaux:
            if not coups_legaux:
                roi = partie_etat.rois[couleur_actuelle]
                if roi.attaquee():
                    # Échec et mat représenté par ungain extremement élevé (en valeur absolue)
                    return -10000 - profondeur if est_max else 10000 + profondeur
                else:
                    # Pat
                    return 0
            return self._evaluer(partie_etat, couleur_ia)

        if est_max:  # si l'IA joue (tour virtuel)
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
                    break  # Élagage c-à-d on néglige les coups a priori inintéressants pour l'IA
            return val_max
        else:  # Si le joueur joue (tour virtuel, en considérant qu'il joue avec la même méthode que l'IA)
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
                    break  # Élagage des coups côté joueur
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

        for (
            coup
        ) in coups_legaux:  # application de minimax et tri des coups en fonction de leurs scores
            partie_virtuelle = copy.deepcopy(self.partie)
            partie_virtuelle.jouer_coup(coup)
            score = self._minimax(partie_virtuelle, self.niveau - 1, alpha, beta, False, couleur_ia)

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)

        return meilleur_coup
