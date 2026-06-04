# écrit par Valentin
import copy
import sys
import os
from piece import Piece
from abc import abstractmethod, ABC
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

    def _jouer_coup_ia(self, partie_etat: "Partie", coup: tuple) -> tuple:
        """Applique le coup sur le plateau et sauvegarde l'état complet nécessaire à l'annulation"""
        depart, arrivee = coup
        piece_depart = partie_etat.plateau[depart[0]][depart[1]]

        # 1. Sauvegarde des droits aux roques (duplication des listes de booléens)
        anciens_roques = {
            0: list(partie_etat.roques_possibles[0]),
            1: list(partie_etat.roques_possibles[1]),
        }

        # 2. Sauvegarde de la pièce capturée (normale ou en passant)
        piece_capturee = partie_etat.plateau[arrivee[0]][arrivee[1]]
        pos_capture = arrivee

        if partie_etat.est_en_passant(piece_depart, depart, arrivee):
            l_ep = arrivee[0] - (-1) ** piece_depart.couleur
            piece_capturee = partie_etat.plateau[l_ep][arrivee[1]]
            pos_capture = (l_ep, arrivee[1])

        est_r = partie_etat.est_roque(piece_depart, depart, arrivee)

        # 3. Application native du coup (incrémente le tour, remplit l'historique...)
        partie_etat.jouer_coup(coup)

        # On renvoie le tuple contenant l'état initial complet
        return (piece_depart, depart, arrivee, piece_capturee, pos_capture, anciens_roques, est_r)

    def _annuler_coup_ia(self, partie_etat: "Partie", etat_sauvegarde: tuple) -> None:
        """Inverse proprement les modifications de jouer_coup sans refaire de deepcopy"""
        piece_depart, depart, arrivee, piece_capturee, pos_capture, anciens_roques, est_r = (
            etat_sauvegarde
        )

        # 1. Restauration du compteur de tours et retrait des historiques ajoutés
        partie_etat.tour -= 1
        if partie_etat.historique:
            partie_etat.historique.pop()
        if partie_etat.historique_str:
            partie_etat.historique_str.pop()

        # 2. Restauration des roques
        partie_etat.roques_possibles = anciens_roques

        # 3. Retour de la pièce de départ à sa case initiale
        partie_etat.plateau[depart[0]][depart[1]] = piece_depart
        if piece_depart:
            piece_depart.position = depart

        # 4. Nettoyage de la case d'arrivée
        partie_etat.plateau[arrivee[0]][arrivee[1]] = None

        # 5. Restauration de la pièce mangée s'il y en avait une
        if piece_capturee is not None:
            partie_etat.plateau[pos_capture[0]][pos_capture[1]] = piece_capturee
            piece_capturee.position = pos_capture

        # 6. Gestion du retour de la Tour si le coup était un Roque
        if est_r:
            y1 = 7 * (1 + (arrivee[1] - depart[1]) // 2) // 2
            y2 = depart[1] + (arrivee[1] - depart[1]) // 2
            # On ré-inverse le swap de la tour effectué dans jouer_coup
            partie_etat.plateau[depart[0]][y1], partie_etat.plateau[depart[0]][y2] = (
                partie_etat.plateau[depart[0]][y2],
                partie_etat.plateau[depart[0]][y1],
            )
            tour_piece = partie_etat.plateau[depart[0]][y1]
            if tour_piece:
                tour_piece.position = (depart[0], y1)

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
        couleur_actuelle = couleur_ia if est_max else (1 - couleur_ia)
        coups_legaux = self._get_tous_coups_legaux(partie_etat, couleur_actuelle)

        if profondeur == 0 or not coups_legaux:
            if not coups_legaux:
                roi = partie_etat.rois[couleur_actuelle]
                if roi.attaquee():
                    return -10000 - profondeur if est_max else 10000 + profondeur
                else:
                    return 0
            return self._evaluer(partie_etat, couleur_ia)

        if est_max:  # si l'IA joue (tour virtuel)
            val_max = float("-inf")
            for coup in coups_legaux:
                # --- PLUS DE DEEPCOPY ICI : ON JOUE ET ON ANNULE SUR LA MÊME INSTANCE ---
                etat = self._jouer_coup_ia(partie_etat, coup)
                score = self._minimax(partie_etat, profondeur - 1, alpha, beta, False, couleur_ia)
                self._annuler_coup_ia(partie_etat, etat)

                val_max = max(val_max, score)
                alpha = max(alpha, val_max)
                if beta <= alpha:
                    break
            return val_max
        else:  # Si le joueur joue
            val_min = float("inf")
            for coup in coups_legaux:
                etat = self._jouer_coup_ia(partie_etat, coup)
                score = self._minimax(partie_etat, profondeur - 1, alpha, beta, True, couleur_ia)
                self._annuler_coup_ia(partie_etat, etat)

                val_min = min(val_min, score)
                beta = min(beta, val_min)
                if beta <= alpha:
                    break
            return val_min

    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Polymorphisme, métode adaptée à minimax"""
        couleur_ia = self.partie.tour % 2

        partie_virtuelle = copy.deepcopy(self.partie)
        coups_legaux = self._get_tous_coups_legaux(partie_virtuelle, couleur_ia)

        if not coups_legaux:
            return None

        meilleur_coup = None
        meilleur_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for coup in coups_legaux:
            etat = self._jouer_coup_ia(partie_virtuelle, coup)
            score = self._minimax(partie_virtuelle, self.niveau - 1, alpha, beta, False, couleur_ia)
            self._annuler_coup_ia(partie_virtuelle, etat)

            if score > meilleur_score:
                meilleur_score = score
                meilleur_coup = coup
            alpha = max(alpha, meilleur_score)

        return meilleur_coup
