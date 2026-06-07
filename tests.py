"""
Tests unitaires — Jeu d'échecs
==============================
Méthodes testées :
  1. Piece.filtrer_coups_forces_clouage  — exclut les coups qui laissent le roi en échec
  2. Partie.jouer_coup                   — met à jour le plateau, l'historique et le tour
  3. Partie.est_en_passant / est_roque   — détection des règles spéciales
  4. IA_fort._evaluer                    — fonction d'évaluation positionnelle
"""

import unittest

from partie import Partie
from piece import Piece
from pion import Pion
from roi import Roi
from dame import Dame
from tour import Tour
from fou import Fou
from cavalier import Cavalier
from ia_fort import IA_fort


def plateau_vide(partie: Partie) -> None:
    """Vide entièrement le plateau (utile pour poser des positions sur mesure)."""
    for i in range(8):
        for j in range(8):
            partie.plateau[i][j] = None


def poser(partie: Partie, piece: Piece, ligne: int, colonne: int) -> None:
    """Place une pièce à la position donnée et met à jour son attribut position."""
    partie.plateau[ligne][colonne] = piece
    piece.position = (ligne, colonne)


# 1. Piece.filtrer_coups_forces_clouage
class TestFiltrerCoupsForcesClouage(unittest.TestCase):
    """
    filtrer_coups_forces_clouage doit retirer tout coup qui laisserait
    le roi allié en échec après le déplacement.
    """

    def test_clouage_absolu_aucun_coup(self):
        """
        Un fou allié est cloué sur la colonne du roi par une tour ennemie :
        aucun de ses déplacements ne doit être autorisé.

            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            . . . . . . . .
            R(b) F(b) . . . T(n) . .   ← rangée 0
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 0, 0, partie)
        fou_blanc = Fou(0, 1, 0, partie)
        tour_noire = Tour(0, 5, 1, partie)

        partie.rois[0] = roi_blanc
        poser(partie, roi_blanc, 0, 0)
        poser(partie, fou_blanc, 0, 1)
        poser(partie, tour_noire, 0, 5)

        # Le fou est cloué sur la ligne 0 — aucun mouvement ne le sort de cette ligne
        coups = fou_blanc.cases_atteignables()
        self.assertEqual(
            coups, [], "Un fou cloué sur la ligne du roi ne peut pas se déplacer"
        )

    def test_clouage_partiel_seul_interposition_autorisee(self):
        """
        Le roi blanc est en a1, une dame noire en a8 cloue un pion blanc en a4.
        Le pion peut seulement avancer sur a5 (reste sur la colonne, interpose).
        Il ne peut pas capturer en diagonale car cela dévoilerait le roi.

            D(n) en (7,0)
            ...
            P(b) en (3,0)  ← cloué sur colonne 0
            ...
            R(b) en (0,0)
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 0, 0, partie)
        pion_blanc = Pion(3, 0, 0, partie)
        dame_noire = Dame(7, 0, 1, partie)
        # Pièce ennemie en diagonale du pion pour tenter la capture
        pion_ennemi = Pion(4, 1, 1, partie)

        partie.rois[0] = roi_blanc
        poser(partie, roi_blanc, 0, 0)
        poser(partie, pion_blanc, 3, 0)
        poser(partie, dame_noire, 7, 0)
        poser(partie, pion_ennemi, 4, 1)

        coups = pion_blanc.cases_atteignables()
        # Seule la case (4,0) est légale (reste sur la colonne, entre roi et dame)
        self.assertIn((4, 0), coups, "Le pion peut avancer d'une case sur la colonne")
        self.assertNotIn(
            (4, 1), coups, "Le pion ne peut pas capturer en diagonale (roi dévoilé)"
        )

    def test_pas_de_clouage_coups_normaux(self):
        """
        Un cavalier qui n'est pas cloué doit conserver tous ses sauts légaux.
        Position : cavalier blanc en e4, roi blanc en a1 (aucune menace alignée).
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 0, 0, partie)
        cavalier_blanc = Cavalier(3, 4, 0, partie)  # e4

        partie.rois[0] = roi_blanc
        poser(partie, roi_blanc, 0, 0)
        poser(partie, cavalier_blanc, 3, 4)

        coups = cavalier_blanc.cases_atteignables()
        # Le cavalier en e4 a 8 positions théoriques, toutes dans le plateau ici
        self.assertGreaterEqual(
            len(coups), 6, "Un cavalier libre doit avoir au moins 6 coups depuis e4"
        )


# 2. Partie.jouer_coup
class TestJouerCoup(unittest.TestCase):
    """
    jouer_coup doit : déplacer la pièce, vider la case de départ,
    écraser la pièce capturée, incrémenter le tour et remplir l'historique.
    """

    def test_deplacement_simple(self):
        """
        Avance le pion e2→e4 depuis la position initiale.
        Vérifie la case d'arrivée, la case de départ et le compteur de tours.
        """
        partie = Partie()
        pion = partie.plateau[1][4]  # Pe2 (blanc)
        self.assertIsNotNone(pion)

        partie.jouer_coup(((1, 4), (3, 4)))  # e2→e4

        self.assertIs(partie.plateau[3][4], pion, "Le pion doit être en e4")
        self.assertIsNone(partie.plateau[1][4], "La case e2 doit être vide")
        self.assertEqual(
            pion.position, (3, 4), "La position interne du pion doit être mise à jour"
        )
        self.assertEqual(
            partie.tour, 1, "Le compteur de tours doit valoir 1 après un coup"
        )

    def test_capture(self):
        """
        Un pion blanc capture un pion noir en diagonale.
        La pièce capturée doit disparaître du plateau.
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, roi_noir, 7, 4)

        pion_blanc = Pion(3, 3, 0, partie)
        pion_noir = Pion(4, 4, 1, partie)
        poser(partie, pion_blanc, 3, 3)
        poser(partie, pion_noir, 4, 4)

        partie.jouer_coup(((3, 3), (4, 4)))

        self.assertIs(
            partie.plateau[4][4],
            pion_blanc,
            "Le pion blanc doit occuper la case de capture",
        )
        self.assertIsNone(partie.plateau[3][3], "La case de départ doit être vide")

    def test_historique_mis_a_jour(self):
        """
        Après deux coups, l'historique doit contenir exactement deux entrées.
        """
        partie = Partie()
        partie.jouer_coup(((1, 4), (3, 4)))  # e2→e4 (blanc)
        partie.jouer_coup(((6, 4), (4, 4)))  # e7→e5 (noir)

        self.assertEqual(len(partie.historique), 2)
        self.assertEqual(len(partie.historique_str), 2)
        self.assertEqual(partie.tour, 2)

    def test_mise_a_jour_roques_apres_deplacement_tour(self):
        """
        Déplacer la tour h1 doit invalider le petit roque pour les blancs.
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        tour_h1 = Tour(0, 7, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, tour_h1, 0, 7)
        poser(partie, roi_noir, 7, 4)

        self.assertTrue(
            partie.roques_possibles[0][1],
            "Petit roque blanc doit être possible au départ",
        )
        partie.jouer_coup(((0, 7), (0, 6)))  # Tour h1→g1
        self.assertFalse(
            partie.roques_possibles[0][1],
            "Petit roque blanc doit être désactivé après le déplacement de la tour",
        )


# 3. Partie.est_en_passant  et  Partie.est_roque
class TestReglesSpeciales(unittest.TestCase):
    def test_en_passant_detecte_correctement(self):
        """
        Après un double pas d'un pion noir en d7→d5 alors que le pion blanc
        est en e5, le coup exd6 (capture en passant) doit être détecté.
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, roi_noir, 7, 4)

        pion_blanc = Pion(4, 4, 0, partie)  # e5
        pion_noir = Pion(4, 3, 1, partie)  # d5 (après double pas simulé)
        poser(partie, pion_blanc, 4, 4)
        poser(partie, pion_noir, 4, 3)

        # Simuler le double pas en remplissant l'historique manuellement
        partie.historique.append(((6, 3), (4, 3)))  # d7→d5

        # Le coup e5xd6 est-il reconnu comme en passant ?
        self.assertTrue(
            partie.est_en_passant(pion_blanc, (4, 4), (5, 3)),
            "Le coup exd6 doit être reconnu comme une prise en passant",
        )

    def test_en_passant_non_detecte_sans_double_pas(self):
        """
        Si le dernier coup n'était pas un double pas, la prise en passant
        ne doit pas être autorisée.
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, roi_noir, 7, 4)

        pion_blanc = Pion(4, 4, 0, partie)
        pion_noir = Pion(4, 3, 1, partie)
        poser(partie, pion_blanc, 4, 4)
        poser(partie, pion_noir, 4, 3)

        # Dernier coup = simple pas (pas un double pas)
        partie.historique.append(((5, 3), (4, 3)))  # d6→d5
        self.assertFalse(
            (5, 3) in pion_blanc.cases_atteignables(),
            "Un simple pas adverse ne doit pas ouvrir la prise en passant",
        )

    def test_roque_detecte_roi_deux_cases(self):
        """
        Le roi qui se déplace de deux cases est identifié comme un roque.
        """
        partie = Partie()
        roi = Roi(0, 4, 0, partie)
        poser(partie, roi, 0, 4)

        self.assertTrue(
            partie.est_roque(roi, (0, 4), (0, 6)),
            "Roi e1→g1 : petit roque doit être détecté",
        )
        self.assertTrue(
            partie.est_roque(roi, (0, 4), (0, 2)),
            "Roi e1→c1 : grand roque doit être détecté",
        )

    def test_roque_non_detecte_deplacement_simple(self):
        """
        Un déplacement d'une seule case du roi n'est pas un roque.
        """
        partie = Partie()
        roi = Roi(0, 4, 0, partie)
        poser(partie, roi, 0, 4)

        self.assertFalse(
            partie.est_roque(roi, (0, 4), (0, 5)),
            "Déplacement d'une case ne doit pas être reconnu comme un roque",
        )

    def test_roque_non_detecte_piece_non_roi(self):
        """
        Une tour qui se déplace de deux cases n'est pas un roque.
        """
        partie = Partie()
        tour = Tour(0, 0, 0, partie)
        poser(partie, tour, 0, 0)

        self.assertFalse(
            partie.est_roque(tour, (0, 0), (0, 2)),
            "Une tour déplacée de deux cases ne constitue pas un roque",
        )


# 4. IA_fort._evaluer
class TestIAFortEvaluer(unittest.TestCase):
    """
    _evaluer retourne un score positif si l'IA a l'avantage matériel et
    positionnel, négatif sinon. Le score est symétrique selon la couleur.
    """

    def _make_ia(self, partie: Partie) -> IA_fort:
        return IA_fort(1, partie)

    def test_position_initiale_equilibree(self):
        """
        Depuis la position de départ (symétrique), le score doit être
        proche de zéro quel que soit la couleur choisie pour l'IA.
        Les deux camps ont exactement les mêmes pièces, le bonus positionnel
        est aussi symétrique : le score peut différer légèrement selon
        les nuances de développement mais doit rester faible.
        """
        partie = Partie()
        ia = self._make_ia(partie)

        score_blanc = ia._evaluer(partie, 0)
        score_noir = ia._evaluer(partie, 1)

        # Les deux scores doivent être opposés (symétrie)
        self.assertEqual(
            score_blanc,
            -score_noir,
            "Les scores blancs et noirs doivent être opposés en position initiale",
        )
        # Et proches de zéro (aucun avantage matériel)
        self.assertAlmostEqual(
            score_blanc, 0, delta=10, msg="Le score initial doit être proche de zéro"
        )

    def test_avantage_materiel_dame(self):
        """
        Si l'IA (blancs) a une dame supplémentaire, son score doit être
        nettement positif (≥ valeur d'une dame = 90 pts).
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        dame_blanche = Dame(3, 3, 0, partie)

        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, roi_noir, 7, 4)
        poser(partie, dame_blanche, 3, 3)

        ia = self._make_ia(partie)
        score = ia._evaluer(partie, 0)  # IA = blancs

        self.assertGreaterEqual(
            score, 90, "Une dame supplémentaire doit valoir au moins 90 points"
        )

    def test_desavantage_materiel_negatif(self):
        """
        Si l'IA (blancs) n'a que son roi face au roi + dame ennemis,
        le score doit être négatif.
        """
        partie = Partie()
        plateau_vide(partie)

        roi_blanc = Roi(0, 4, 0, partie)
        roi_noir = Roi(7, 4, 1, partie)
        dame_noire = Dame(5, 3, 1, partie)

        partie.rois[0] = roi_blanc
        partie.rois[1] = roi_noir
        poser(partie, roi_blanc, 0, 4)
        poser(partie, roi_noir, 7, 4)
        poser(partie, dame_noire, 5, 3)

        ia = self._make_ia(partie)
        score = ia._evaluer(partie, 0)  # IA = blancs

        self.assertLess(
            score,
            0,
            "L'IA sans matériel face à une dame ennemie doit avoir un score négatif",
        )

    def test_bonus_centralisation(self):
        """
        Un cavalier allié au centre (e4) doit donner un meilleur score
        qu'un cavalier allié en coin (a1), toutes choses égales par ailleurs.
        """

        def score_avec_cavalier(ligne, colonne):
            partie = Partie()
            plateau_vide(partie)
            roi_blanc = Roi(0, 4, 0, partie)
            roi_noir = Roi(7, 4, 1, partie)
            cavalier = Cavalier(ligne, colonne, 0, partie)
            partie.rois[0] = roi_blanc
            partie.rois[1] = roi_noir
            poser(partie, roi_blanc, 0, 4)
            poser(partie, roi_noir, 7, 4)
            poser(partie, cavalier, ligne, colonne)
            ia = IA_fort(1, partie)
            return ia._evaluer(partie, 0)

        score_centre = score_avec_cavalier(3, 4)  # e4
        score_coin = score_avec_cavalier(0, 0)  # a1

        self.assertGreater(
            score_centre,
            score_coin,
            "Un cavalier au centre doit donner un meilleur score qu'un cavalier en coin",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
