# Auteur : Valentin
import copy
from random import choice
from dame import Dame
from tour import Tour
from fou import Fou
from cavalier import Cavalier
from abc import abstractmethod, ABC
from typing import TYPE_CHECKING
from ia import IA

if TYPE_CHECKING:
    from partie import Partie


class IA_fort(IA):
    """IA utilisant l'algorithme minimax avec élagage alpha-bêta."""

    def __init__(self, niveau: int, partie: "Partie"):
        super().__init__(niveau, partie)

    PIECES_PROMOTION = [Dame, Tour, Fou, Cavalier]

    def _get_tous_coups_legaux(self, partie_etat: "Partie", couleur: int) -> list[tuple]:
        """Retourne tous les coups légaux de la couleur donnée. Chaque promotion génère 4 coups distincts."""
        coups = []
        ligne_promo = 7 if couleur == 0 else 0
        for i in range(8):
            for j in range(8):
                piece = partie_etat.plateau[i][j]
                if piece is not None and piece.couleur == couleur:
                    for dest in piece.cases_atteignables():
                        if piece.type == "P" and dest[0] == ligne_promo:
                            for classe in self.PIECES_PROMOTION:
                                coups.append((piece.position, dest, classe))
                        else:
                            coups.append((piece.position, dest))
        return coups

    def _evaluer(self, partie_etat: "Partie", couleur_ia: int) -> int:
        """Évalue la position : somme des valeurs matérielles avec bonus positionnels (centralisation, développement)."""
        valeurs = {"P": 10, "C": 30, "F": 30, "T": 50, "D": 90, "R": 1000000000}

        # Distance de Chebyshev au centre (cases e4/d4/e5/d5) : vaut 3 au centre, 0 au coin
        def bonus_centre(i, j):
            return max(0, 3 - max(abs(i - 3.5), abs(j - 3.5)))

        # Cases de départ des pièces mineures (cavaliers, fous) par couleur
        cases_depart = [
            {(0, 1), (0, 2), (0, 5), (0, 6)},  # blancs
            {(7, 1), (7, 2), (7, 5), (7, 6)},  # noirs
        ]

        score = 0
        for i in range(8):
            for j in range(8):
                piece = partie_etat.plateau[i][j]
                if piece is None:
                    continue
                valeur_piece = valeurs.get(piece.type, 0)

                positional = 0
                if piece.type != "R":
                    positional += bonus_centre(i, j)

                # Malus si cavalier/fou encore sur sa case de départ après les 3 premiers tours
                if partie_etat.tour > 3 and piece.type in ("C", "F") and (i, j) in cases_depart[piece.couleur]:
                    positional -= 2

                if piece.couleur == couleur_ia:
                    score += valeur_piece + positional
                else:
                    score -= valeur_piece + positional
        return score

    def _jouer_coup_ia(self, partie_etat: "Partie", coup: tuple) -> tuple:
        """Joue un coup sur partie_etat et retourne un tuple d'état permettant son annulation."""
        depart, arrivee = coup[0], coup[1]
        classe_promotion = coup[2] if len(coup) == 3 else None
        piece_depart = partie_etat.plateau[depart[0]][depart[1]]

        # 1. Sauvegarde des droits de roque
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

        # 3. Application du coup (incrémente le tour, remplit l'historique…)
        partie_etat.jouer_coup((depart, arrivee))

        # 4. Promotion : substitution du pion par la pièce choisie
        if classe_promotion is not None:
            piece_promue = classe_promotion(arrivee[0], arrivee[1], piece_depart.couleur, partie_etat)
            partie_etat.plateau[arrivee[0]][arrivee[1]] = piece_promue

        return (piece_depart, depart, arrivee, piece_capturee, pos_capture, anciens_roques, est_r)

    def _annuler_coup_ia(self, partie_etat: "Partie", etat_sauvegarde: tuple) -> None:
        """Restaure partie_etat à son état avant le coup correspondant à etat_sauvegarde."""
        piece_depart, depart, arrivee, piece_capturee, pos_capture, anciens_roques, est_r = (
            etat_sauvegarde
        )

        # 1. Décrémentation du compteur de tours et retrait des entrées d'historique
        partie_etat.tour -= 1
        if partie_etat.historique:
            partie_etat.historique.pop()
        if partie_etat.historique_str:
            partie_etat.historique_str.pop()

        # 2. Restauration des droits de roque
        partie_etat.roques_possibles = anciens_roques

        # 3. Retour de la pièce déplacée à sa case d'origine
        partie_etat.plateau[depart[0]][depart[1]] = piece_depart
        if piece_depart:
            piece_depart.position = depart

        # 4. Nettoyage de la case d'arrivée
        partie_etat.plateau[arrivee[0]][arrivee[1]] = None

        # 5. Restauration de la pièce capturée
        if piece_capturee is not None:
            partie_etat.plateau[pos_capture[0]][pos_capture[1]] = piece_capturee
            piece_capturee.position = pos_capture

        # 6. Repositionnement de la tour si le coup était un roque
        if est_r:
            # y1 : colonne d'origine de la tour (0 ou 7) ; y2 : colonne intermédiaire occupée après le roque
            y1 = 7 * (1 + (arrivee[1] - depart[1]) // 2) // 2
            y2 = depart[1] + (arrivee[1] - depart[1]) // 2
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
        """Algorithme minimax avec élagage alpha-bêta. Retourne le score estimé de la position."""
        couleur_actuelle = couleur_ia if est_max else (1 - couleur_ia)
        coups_legaux = self._get_tous_coups_legaux(partie_etat, couleur_actuelle)

        if profondeur == 0 or not coups_legaux:
            if not coups_legaux:
                roi = partie_etat.rois[couleur_actuelle]
                if partie_etat.echecs:
                    # Favoriser les mats plus rapides via la profondeur résiduelle
                    return -10000 - profondeur if est_max else 10000 + profondeur
                else:
                    return 0  # Pat
            return self._evaluer(partie_etat, couleur_ia)

        if est_max:  # Tour de l'IA
            val_max = float("-inf")
            for coup in coups_legaux:
                etat = self._jouer_coup_ia(partie_etat, coup)
                score = self._minimax(partie_etat, profondeur - 1, alpha, beta, False, couleur_ia)
                self._annuler_coup_ia(partie_etat, etat)

                val_max = max(val_max, score)
                alpha = max(alpha, val_max)
                if beta <= alpha:  # Coupure bêta
                    break
            return val_max
        else:  # Tour de l'adversaire
            val_min = float("inf")
            for coup in coups_legaux:
                etat = self._jouer_coup_ia(partie_etat, coup)
                score = self._minimax(partie_etat, profondeur - 1, alpha, beta, True, couleur_ia)
                self._annuler_coup_ia(partie_etat, etat)

                val_min = min(val_min, score)
                beta = min(beta, val_min)
                if beta <= alpha:  # Coupure alpha
                    break
            return val_min

    def choisir_coup(self) -> tuple[tuple[int, int], tuple[int, int]]:
        """Retourne le meilleur coup trouvé par minimax pour la couleur du joueur actuel.

        En cas d'égalité de score entre plusieurs coups, l'un d'eux est choisi aléatoirement.
        """
        couleur_ia = self.partie.tour % 2

        partie_virtuelle = copy.deepcopy(self.partie)
        coups_legaux = self._get_tous_coups_legaux(partie_virtuelle, couleur_ia)

        if not coups_legaux:
            return None

        meilleurs_coups = []
        meilleur_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        for coup in coups_legaux:
            etat = self._jouer_coup_ia(partie_virtuelle, coup)
            score = self._minimax(partie_virtuelle, self.niveau - 1, alpha, beta, False, couleur_ia)
            self._annuler_coup_ia(partie_virtuelle, etat)

            if score > meilleur_score:
                meilleur_score = score
                meilleurs_coups = [coup]
            elif score == meilleur_score:
                meilleurs_coups.append(coup)
            alpha = max(alpha, meilleur_score)

        # On tronque à 2 éléments pour éliminer la classe de promotion éventuelle
        return choice(meilleurs_coups)[:2]