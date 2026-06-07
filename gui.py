from PyQt5.QtWidgets import (
    QStyleFactory,
    QSizePolicy,
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QInputDialog,
    QPlainTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QFontMetrics, QMouseEvent
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtSvg import QSvgRenderer
import os

from partie import Partie
from piece import Piece
from pion import Pion
from dame import Dame
from tour import Tour
from fou import Fou
from cavalier import Cavalier
from ia_fort import IA_fort
from ia_random import IARandom
import random

class HistoriqueCoups(QPlainTextEdit):
    LIGNE_REFERENCE = "99. Da1xh8+++ Da8xh1+++"

    def __init__(self, partie: Partie, echelle_police: float):
        super().__init__()
        self.partie = partie
        self.setReadOnly(True)
        self.setMinimumWidth(200)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._taille_police_courante = -1
        self._appliquer_style(8)
        self.mettre_a_jour_coups()

    def _appliquer_style(self, taille_pt: int):
        if taille_pt == self._taille_police_courante:
            return
        self._taille_police_courante = taille_pt
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {taille_pt}pt;
                padding: 10px;
            }}
        """)

    def _ajuster_police(self):
        largeur_dispo = self.viewport().width() - 4
        if largeur_dispo <= 0:
            return
        for taille in range(30, 3, -1):
            fm = QFontMetrics(QFont("Consolas", taille))
            if fm.horizontalAdvance(self.LIGNE_REFERENCE) <= largeur_dispo:
                self._appliquer_style(taille)
                return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._ajuster_police()

    def mettre_a_jour_coups(self):
        texte = ""
        coups = self.partie.historique_str

        for i in range(0, len(coups), 2):
            numero_coup = i // 2 + 1
            coup_blanc = coups[i] if i < len(coups) else ""
            coup_noir = coups[i + 1] if i + 1 < len(coups) else ""

            ligne_coup = f"{numero_coup:2}. {coup_blanc:<11}"
            if coup_noir:
                ligne_coup += f" {coup_noir}"

            texte += ligne_coup + "\n"

        self.setPlainText(texte)
        if barre_defilement := self.verticalScrollBar():
            barre_defilement.setValue(barre_defilement.maximum())

class Echiquier(QWidget):
    def __init__(self, partie: Partie, historique_coups: HistoriqueCoups, echelle_police:float):
        super().__init__()
        self.partie = partie
        self.taille_case = 60
        self.taille_etiquette = 30
        self.case_selectionnee = None
        self.historique_coups: HistoriqueCoups = historique_coups
        self.en_promotion = False
        self.ligne_promotion = 0
        self.colonne_promotion = 0
        self.pieces_promotion = [Dame, Tour, Fou, Cavalier]
        self.echelle_police = echelle_police
        self.en_jeu = False
        self.ia = None
        self.couleur_ia = None
        self.tour_ia_en_cours = False
        self.message_fin: str | None = None
        self.promotions: list[str | None] = []  # type promu par coup, None si pas de promotion
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Jeu d\'échecs')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        taille_plateau = 8 * self.taille_case
        taille_totale = taille_plateau + 2 * self.taille_etiquette
        return QSize(taille_totale, taille_totale)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cote = min(self.width(), self.height())
        self.taille_case = max(20, cote // 9)
        self.taille_etiquette = max(10, self.taille_case // 2)
        self.update()

    def paintEvent(self, a0):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.Antialiasing)

        # Dessiner les cases de l'échiquier
        for ligne in range(8):
            for colonne in range(8):
                ligne_affichee = 7 - ligne
                x = self.taille_etiquette + colonne * self.taille_case
                y = self.taille_etiquette + ligne_affichee * self.taille_case

                if (ligne + colonne) % 2 == 0:
                    couleur = QColor(240, 217, 181)  # Case claire
                else:
                    couleur = QColor(189, 172, 135)  # Case foncée

                peintre.fillRect(x, y, self.taille_case, self.taille_case, couleur)

                # Dessiner la bordure
                peintre.drawRect(x, y, self.taille_case, self.taille_case)

        # Dessiner les étiquettes des colonnes
        taille_police = int(self.taille_case * 0.1 * self.echelle_police)
        police = QFont("Arial", taille_police)
        peintre.setFont(police)
        peintre.setPen(QColor(0, 0, 0))
        for colonne in range(8):
            x = self.taille_etiquette + colonne * self.taille_case
            # Étiquettes du haut
            peintre.drawText(
                x,
                0,
                self.taille_case,
                self.taille_etiquette,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                chr(ord("a") + colonne),
            )
            # Étiquettes du bas
            peintre.drawText(
                x,
                self.taille_etiquette + 8 * self.taille_case,
                self.taille_case,
                self.taille_etiquette,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                chr(ord("a") + colonne),
            )

        # Dessiner les étiquettes des rangées
        for ligne in range(8):
            ligne_affichee = 7 - ligne
            y = self.taille_etiquette + ligne_affichee * self.taille_case
            rang = str(ligne + 1)
            # Étiquettes de gauche
            peintre.drawText(
                0,
                y,
                self.taille_etiquette,
                self.taille_case,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                rang,
            )
            # Étiquettes de droite
            peintre.drawText(
                self.taille_etiquette + 8 * self.taille_case,
                y,
                self.taille_etiquette,
                self.taille_case,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                rang,
            )

        self.dessiner_pieces(peintre)
        self.dessiner_surbrillances(peintre)
        self.dessiner_promotion(peintre)
        self._dessiner_overlay_fin(peintre)

    def dessiner_pieces(self, peintre: QPainter):
        padding = int(self.taille_case * 0.05)
        taille = self.taille_case - 2 * padding

        for ligne in range(8):
            for colonne in range(8):
                piece = self.partie.plateau[ligne][colonne]
                if piece is None:
                    continue

                ligne_affichee = 7 - ligne
                x = self.taille_etiquette + colonne * self.taille_case + padding
                y = self.taille_etiquette + ligne_affichee * self.taille_case + padding

                chemin_svg = f'svgs/{piece.type.lower()}{piece.couleur}.svg'

                if not os.path.isfile(chemin_svg):
                    continue  # skip if SVG not found

                renderer = QSvgRenderer(chemin_svg)
                renderer.render(peintre, QRectF(x, y, taille, taille))

    def dessiner_surbrillances(self, peintre: QPainter):
        if self.case_selectionnee is None:
            return

        ligne, colonne = self.case_selectionnee
        piece = self.partie.plateau[ligne][colonne]
        if piece is None:
            return

        cases_atteignables = piece.cases_atteignables()
        for ligne_cible, colonne_cible in cases_atteignables:
            ligne_affichee = 7 - ligne_cible
            x = self.taille_etiquette + colonne_cible * self.taille_case
            y = self.taille_etiquette + ligne_affichee * self.taille_case

            piece_cible = self.partie.plateau[ligne_cible][colonne_cible]
            if piece_cible is None:
                couleur = QColor(0, 0, 255, 100)  # Bleu pour les cases vides
            else:
                couleur = QColor(255, 0, 0, 100)  # Rouge pour les cases occupées

            peintre.fillRect(x, y, self.taille_case, self.taille_case, couleur)

    def dessiner_promotion(self, peintre: QPainter):
        if not self.en_promotion or self.ligne_promotion is None:
            return

        police = QFont("Arial", int(self.taille_case * 0.47 * self.echelle_police), QFont.Bold)
        peintre.setFont(police)

        # Afficher les 4 pièces de promotion
        for i, classe_piece in enumerate(self.pieces_promotion):
            # Les pièces s'affichent en remontant ou en descendant selon la couleur
            couleur:int = (self.partie.tour+1)%2
            if couleur:
                ligne_affichage = self.ligne_promotion + i
            else:
                ligne_affichage = self.ligne_promotion - i

            # Vérifier que la ligne est valide
            if not (0 <= ligne_affichage <= 7):
                continue

            ligne_affichee_ui = 7 - ligne_affichage
            x = self.taille_etiquette + self.colonne_promotion * self.taille_case
            y = self.taille_etiquette + ligne_affichee_ui * self.taille_case

            # Fond entièrement opaque
            couleur_fond = QColor(100, 150, 200, 255)
            peintre.fillRect(x, y, self.taille_case, self.taille_case, couleur_fond)

            # Créer une instance temporaire juste pour la représentation
            piece_temp = classe_piece(0, 0, 0, self.partie)

            # Couleur du texte
            if couleur:
                peintre.setPen(QColor(0, 0, 0))        # Pièces noires
            else:
                peintre.setPen(QColor(255, 255, 255))  # Pièces blanches

            peintre.drawText(
                x, y, self.taille_case, self.taille_case,
                Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                piece_temp.representation,
            )

    def _verifier_fin(self) -> bool:
        """Vérifie mat et pat. Pose message_fin et arrête le jeu si terminé. Retourne True si fin."""
        partie = self.partie
        roi = partie.rois[partie.tour % 2]
        couleur_joueur = ('Blancs', 'Noirs')[partie.tour % 2]
        couleur_gagnant = ('Noirs', 'Blancs')[partie.tour % 2]

        # Aucun coup légal disponible ?
        aucun_coup = all(
            not piece.cases_atteignables()
            for ligne in partie.plateau
            for piece in ligne
            if piece is not None and piece.couleur == partie.tour % 2
        )
        if not aucun_coup:
            return False

        if roi.attaquee():
            self.message_fin = f"Échec et mat !\n{couleur_gagnant} gagnent."
        else:
            self.message_fin = "Pat !\nPartie nulle."

        self.en_jeu = False
        self.tour_ia_en_cours = False
        self.update()
        return True

    def _dessiner_overlay_fin(self, peintre: QPainter):
        if self.message_fin is None:
            return
        taille_plateau = 8 * self.taille_case
        x = self.taille_etiquette
        y = self.taille_etiquette
        # Fond semi-transparent
        peintre.fillRect(x, y, taille_plateau, taille_plateau, QColor(0, 0, 0, 160))
        # Texte centré
        taille_police = max(12, self.taille_case * 28 // 60)
        police = QFont("Arial", taille_police, QFont.Bold)
        peintre.setFont(police)
        peintre.setPen(QColor(255, 220, 60))
        peintre.drawText(
            x, y, taille_plateau, taille_plateau,
            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
            self.message_fin,
        )

    def _planifier_coup_ia(self):
        if self.ia is None:
            return
        if self.partie.tour % 2 != self.couleur_ia:
            return
        self.tour_ia_en_cours = True
        QTimer.singleShot(100, self._jouer_coup_ia)

    def _jouer_coup_ia(self):
        if not self.en_jeu or self.ia is None:
            self.tour_ia_en_cours = False
            return
        if self.partie.tour % 2 != self.couleur_ia:
            self.tour_ia_en_cours = False
            return
        coup = self.ia.choisir_coup()
        if coup is None:
            self.tour_ia_en_cours = False
            return
        depart, arrivee = coup
        self.partie.jouer_coup(coup)
        # Promotion automatique en dame si un pion de l'IA atteint la dernière rangée
        piece = self.partie.plateau[arrivee[0]][arrivee[1]]
        type_promo = None
        if isinstance(piece, Pion):
            ligne_promo = 7 if piece.couleur == 0 else 0
            if arrivee[0] == ligne_promo:
                self.partie.plateau[arrivee[0]][arrivee[1]] = Dame(arrivee[0], arrivee[1], piece.couleur, self.partie)
                type_promo = "D"
        self.promotions.append(type_promo)
        if self.historique_coups:
            self.historique_coups.mettre_a_jour_coups()
        self.tour_ia_en_cours = False
        if self._verifier_fin():
            return
        self.update()

    def mousePressEvent(self, a0: QMouseEvent | None):
        if not self.en_jeu or self.tour_ia_en_cours:
            return
        if a0 is None:
            return

        x = a0.x() - self.taille_etiquette
        y = a0.y() - self.taille_etiquette

        if x < 0 or y < 0 or x >= 8 * self.taille_case or y >= 8 * self.taille_case:
            self.case_selectionnee = None
        else:
            colonne_cliquee = x // self.taille_case
            ligne_cliquee = 7 - y // self.taille_case

            # Gérer la promotion
            if self.en_promotion and self.ligne_promotion is not None:
                couleur:int = (self.partie.tour+1)%2
                # Calculer les lignes de promotion
                lignes_promotion = [self.ligne_promotion + i for i in range(4)] if couleur else [self.ligne_promotion - i for i in range(4)]

                # Vérifier si le clic est sur une pièce de promotion
                for i, ligne_promo in enumerate(lignes_promotion):
                    if 0 <= ligne_promo <= 7 and ligne_cliquee == ligne_promo and colonne_cliquee == self.colonne_promotion:
                        classe_piece = self.pieces_promotion[i]
                        piece_promue = classe_piece(self.ligne_promotion, self.colonne_promotion, couleur,self.partie)
                        self.partie.plateau[self.ligne_promotion][self.colonne_promotion] = piece_promue
                        if self.promotions:
                            self.promotions[-1] = piece_promue.type  # remplace le None posé au jouer_coup
                        self.en_promotion = False
                        self.case_selectionnee = None
                        if self.historique_coups:
                            self.historique_coups.mettre_a_jour_coups()
                        if self._verifier_fin():
                            return
                        self.update()
                        self._planifier_coup_ia()
                        return

                # Si le clic n'est pas sur une pièce de promotion, ignorer
                self.update()
                return

            # Vérifier si une pièce est déjà sélectionnée
            if self.case_selectionnee is not None:
                ligne_selectionnee, colonne_selectionnee = self.case_selectionnee
                piece_selectionnee: Piece | None = self.partie.plateau[ligne_selectionnee][colonne_selectionnee]

                if piece_selectionnee is not None:
                    cases_atteignables = piece_selectionnee.cases_atteignables()

                    # Si la case cliquée est dans les cases atteignables, jouer le coup
                    if (ligne_cliquee, colonne_cliquee) in cases_atteignables:
                        coup = ((ligne_selectionnee, colonne_selectionnee), (ligne_cliquee, colonne_cliquee))
                        self.partie.jouer_coup(coup)

                        # Vérifier si c'est une promotion
                        piece_deplacee = self.partie.plateau[ligne_cliquee][colonne_cliquee]
                        if isinstance(piece_deplacee, Pion):
                            est_blanc = piece_deplacee.couleur == 0
                            ligne_promo = 7 if est_blanc else 0
                            if ligne_cliquee == ligne_promo:
                                self.promotions.append(None)  # sera mis à jour au choix
                                self.en_promotion = True
                                self.ligne_promotion = ligne_cliquee
                                self.colonne_promotion = colonne_cliquee
                                self.case_selectionnee = None
                                self.update()
                                return

                        self.promotions.append(None)  # coup sans promotion
                        if self.historique_coups:
                            self.historique_coups.mettre_a_jour_coups()
                        self.case_selectionnee = None
                        if self._verifier_fin():
                            return
                        self.update()
                        self._planifier_coup_ia()
                        return

            # Sélectionner une pièce seulement si elle appartient au joueur actuel
            piece = self.partie.plateau[ligne_cliquee][colonne_cliquee]
            if piece is not None and piece.couleur == self.partie.tour % 2:
                self.case_selectionnee = (ligne_cliquee, colonne_cliquee)
            else:
                self.case_selectionnee = None

        self.update()


class PanneauLateral(QWidget):
    MODE_PVP = 0
    MODE_PVA = 1

    COULEUR_BLANC = 0
    COULEUR_NOIR = 1
    COULEUR_ALEATOIRE = 2

    def __init__(self, partie: Partie, echelle_police:float):
        super().__init__()
        self.partie = partie
        self.echelle_police = echelle_police
        self.echiquier: Echiquier | None = None

        # State
        self.mode = self.MODE_PVP
        self.couleur_joueur = self.COULEUR_BLANC # 0 blanc, 1 noir, 2 aleatoire
        self.difficulte = 0

        self.ajouter_boutons()

    def _style_icone(self, cote: int, bg="#f5efe6", fg="#333", hover="#ead9c0", pressed="#d4b896") -> str:
        taille_police = max(10, cote * 22 // 56)
        return f"""
            QPushButton {{
                font-size: {taille_police}px;
                border: 2px solid #c8b89a;
                border-radius: 6px;
                background-color: {bg};
                color: {fg};
                min-width: {cote}px;
                max-width: {cote}px;
                min-height: {cote}px;
                max-height: {cote}px;
            }}
            QPushButton:hover {{
                background-color: {hover};
                border-color: #a07850;
            }}
            QPushButton:pressed {{
                background-color: {pressed};
            }}
            QPushButton:disabled {{
                background-color: #e8e8e8;
                border-color: #d0d0d0;
                color: #b0b0b0;
            }}
        """

    def _style_jouer(self, hauteur: int) -> str:
        taille_police = max(8, hauteur * 16 // 40)
        return f"""
            QPushButton {{
                font-size: {taille_police}px;
                font-weight: bold;
                border: 2px solid #2d7a2d;
                border-radius: 6px;
                background-color: #4caf50;
                color: white;
                min-height: {hauteur}px;
                max-height: {hauteur}px;
                padding: 0 12px;
            }}
            QPushButton:hover {{
                background-color: #43a047;
                border-color: #1b5e1b;
            }}
            QPushButton:pressed {{
                background-color: #388e3c;
            }}
        """

    def ajouter_boutons(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.historique = HistoriqueCoups(self.partie, self.echelle_police)
        layout.addWidget(self.historique, stretch=1)

        boutons_layout = QHBoxLayout()
        boutons_layout.setSpacing(6)
        boutons_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_mode = QPushButton("👤")
        self.btn_mode.setToolTip("Mode : Joueur vs Joueur / Joueur vs IA")
        self.btn_mode.clicked.connect(self.cycler_mode_jeu)

        self.btn_couleur = QPushButton("⬜")
        self.btn_couleur.setToolTip("Couleur du joueur")
        self.btn_couleur.clicked.connect(self.cycler_couleur)
        self.btn_couleur.setEnabled(False)

        self.btn_difficulte = QPushButton("0")
        self.btn_difficulte.setToolTip("Difficulté de l'IA")
        self.btn_difficulte.clicked.connect(self.cycler_difficulte)
        self.btn_difficulte.setEnabled(False)

        for bouton in (self.btn_mode, self.btn_couleur, self.btn_difficulte):
            boutons_layout.addWidget(bouton)

        layout.addLayout(boutons_layout)

        self.btn_jouer = QPushButton("Jouer")
        self.btn_jouer.setToolTip("Démarrer la partie")
        self.btn_jouer.clicked.connect(self.on_jouer)
        layout.addWidget(self.btn_jouer)

        # Ligne sauvegarder / charger
        io_layout = QHBoxLayout()
        io_layout.setSpacing(6)
        io_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_sauvegarder = QPushButton("💾 Sauvegarder")
        self.btn_sauvegarder.setToolTip("Sauvegarder la partie en cours")
        self.btn_sauvegarder.clicked.connect(self.on_sauvegarder)

        self.btn_charger = QPushButton("📂 Charger")
        self.btn_charger.setToolTip("Charger une partie sauvegardée")
        self.btn_charger.clicked.connect(self.on_charger)

        io_layout.addWidget(self.btn_sauvegarder)
        io_layout.addWidget(self.btn_charger)
        layout.addLayout(io_layout)

        self.setMinimumWidth(150)
        self._appliquer_styles_boutons()
        self.rafraichir_boutons()

    def _appliquer_styles_boutons(self):
        largeur = self.width() or 200
        cote = max(30, min(largeur // 4, 80))
        hauteur_jouer = max(24, cote * 40 // 56)
        style = self._style_icone(cote)
        self.btn_mode.setStyleSheet(style)
        self.btn_couleur.setStyleSheet(style)
        self.btn_difficulte.setStyleSheet(style)
        self.btn_jouer.setStyleSheet(self._style_jouer(hauteur_jouer))
        style_io = self._style_jouer(max(22, hauteur_jouer * 3 // 4)).replace(
            "#4caf50", "#1976d2").replace("#43a047", "#1565c0").replace(
            "#388e3c", "#0d47a1").replace("#2d7a2d", "#0d47a1")
        self.btn_sauvegarder.setStyleSheet(style_io)
        self.btn_charger.setStyleSheet(style_io)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._appliquer_styles_boutons()

    def cycler_mode_jeu(self):
        self.mode = self.MODE_PVA if self.mode == self.MODE_PVP else self.MODE_PVP
        self.rafraichir_boutons()

    def cycler_couleur(self):
        self.couleur_joueur = (self.couleur_joueur + 1) % 3
        self.rafraichir_boutons()

    def cycler_difficulte(self):
        self.difficulte = (self.difficulte + 1) % 4
        self.rafraichir_boutons()

    def rafraichir_boutons(self):
        # Mode button
        if self.mode == self.MODE_PVP:
            self.btn_mode.setText("👤")
            self.btn_mode.setToolTip("Mode : Joueur vs Joueur (cliquer pour activer l'IA)")
        else:
            self.btn_mode.setText("🖥️")
            self.btn_mode.setToolTip("Mode : Joueur vs IA (cliquer pour revenir en PvP)")

        # Colour button
        pva = (self.mode == self.MODE_PVA)
        self.btn_couleur.setEnabled(pva)
        self.btn_difficulte.setEnabled(pva)
        icons = ["⬜", "⬛", "🎲"]
        tips = ["Jouer avec les Blancs", "Jouer avec les Noirs", "Couleur aléatoire"]
        self.btn_couleur.setText(icons[self.couleur_joueur])
        self.btn_couleur.setToolTip(tips[self.couleur_joueur])

        # Difficulty button
        self.btn_difficulte.setText(str(self.difficulte))
        self.btn_difficulte.setToolTip(f"Difficulté IA : {self.difficulte}/4")

    def mettre_a_jour_coups(self):
        self.historique.mettre_a_jour_coups()

    def on_sauvegarder(self):
        if self.echiquier is None or not self.partie.historique:
            QMessageBox.information(self, "Sauvegarder", "Aucune partie en cours à sauvegarder.")
            return
        chemin, _ = QFileDialog.getSaveFileName(
            self, "Sauvegarder la partie", "", "Parties d'échecs (*.json);;Tous les fichiers (*)"
        )
        if not chemin:
            return
        try:
            self.partie.sauvegarder(chemin, self.echiquier.promotions)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de sauvegarder :\n{e}")

    def on_charger(self):
        if self.echiquier is None:
            return
        chemin, _ = QFileDialog.getOpenFileName(
            self, "Charger une partie", "", "Parties d'échecs (*.json);;Tous les fichiers (*)"
        )
        if not chemin:
            return
        try:
            nouvelle_partie, promotions = Partie.charger(chemin)
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de charger :\n{e}")
            return

        # Arrêter proprement la partie en cours
        self.echiquier.en_jeu = False
        self.echiquier.tour_ia_en_cours = False

        # Brancher la partie chargée
        self.partie = nouvelle_partie
        self.historique.partie = nouvelle_partie
        self.echiquier.partie = nouvelle_partie
        self.echiquier.historique_coups = self.historique
        self.echiquier.promotions = promotions
        self.echiquier.case_selectionnee = None
        self.echiquier.en_promotion = False
        self.echiquier.message_fin = None
        self.echiquier.ia = None
        self.echiquier.couleur_ia = None

        self.historique.mettre_a_jour_coups()
        self.btn_jouer.setText("Rejouer")

        # Configurer l'IA selon les paramètres du panneau, comme on_jouer
        if self.mode == self.MODE_PVA:
            if self.couleur_joueur == self.COULEUR_ALEATOIRE:
                couleur_humain = random.randint(0, 1)
            else:
                couleur_humain = self.couleur_joueur
            couleur_ia = 1 - couleur_humain
            if self.difficulte:
                self.echiquier.ia = IA_fort(self.difficulte, nouvelle_partie)
            else:
                self.echiquier.ia = IARandom(0, nouvelle_partie)
            self.echiquier.couleur_ia = couleur_ia

        # La partie chargée est jouable immédiatement
        self.echiquier.en_jeu = True
        self.echiquier.update()
        # Si c'est le tour de l'IA dès le chargement, elle joue
        self.echiquier._planifier_coup_ia()

    def on_jouer(self):
        if self.echiquier is None:
            return
        self.echiquier.en_jeu = False
        self.echiquier.tour_ia_en_cours = False
        nouvelle_partie = Partie()
        self.partie = nouvelle_partie
        self.historique.partie = nouvelle_partie
        self.echiquier.partie = nouvelle_partie
        self.echiquier.historique_coups = self.historique
        self.historique.mettre_a_jour_coups()
        self.echiquier.case_selectionnee = None
        self.echiquier.en_promotion = False
        self.echiquier.message_fin = None
        self.echiquier.promotions = []
        self.echiquier.ia = None
        self.echiquier.couleur_ia = None
        if self.mode == self.MODE_PVA:
            if self.couleur_joueur == self.COULEUR_ALEATOIRE:
                couleur_humain = random.randint(0, 1)
            else:
                couleur_humain = self.couleur_joueur
            couleur_ia = 1 - couleur_humain
            if self.difficulte:
                self.echiquier.ia = IA_fort(self.difficulte, nouvelle_partie)
            else:
                self.echiquier.ia = IARandom(0, nouvelle_partie)
            self.echiquier.couleur_ia = couleur_ia
        self.btn_jouer.setText("Rejouer")
        self.echiquier.en_jeu = True
        self.echiquier.update()
        self.echiquier._planifier_coup_ia()

class GUI(QMainWindow):
    def __init__(self, partie: Partie):
        super().__init__()
        echelle_police = QGuiApplication.primaryScreen().logicalDotsPerInch() / 96.0
        self.partie = partie
        self.panneau = PanneauLateral(partie, echelle_police)
        self.echiquier = Echiquier(partie, self.panneau.historique, echelle_police)
        self.panneau.echiquier = self.echiquier
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Échecs')
        self.setStyle(QStyleFactory.create('Fusion'))

        widget_central = QWidget()
        widget_central.setStyleSheet("background-color: #ffffff;")
        disposition = QHBoxLayout(widget_central)
        disposition.setSpacing(15)
        disposition.setContentsMargins(10, 10, 10, 10)

        disposition.addWidget(self.echiquier, stretch=1)
        disposition.addWidget(self.panneau, stretch=0)

        self.setCentralWidget(widget_central)

        taille_plateau = 8 * self.echiquier.taille_case
        taille_totale = taille_plateau + 2 * self.echiquier.taille_etiquette
        self.resize(taille_totale + 300, taille_totale + 50)
        self.show()