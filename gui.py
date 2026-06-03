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
    QPushButton
)
from PyQt5.QtCore import Qt, QSize, QRectF
from PyQt5.QtGui import QPainter, QColor, QFont, QMouseEvent
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

class HistoriqueCoups(QPlainTextEdit):
    def __init__(self, partie: Partie, echelle_police:float):
        super().__init__()
        self.partie = partie
        self.setReadOnly(True)
        self.setMinimumWidth(200)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: {echelle_police*4}pt;
                padding: 10px;
            }}
        """)
        self.mettre_a_jour_coups()

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
        self.init_ui()

    def init_ui(self):
        taille_plateau = 8 * self.taille_case
        taille_totale = taille_plateau + 2 * self.taille_etiquette
        self.setGeometry(100, 100, taille_totale, taille_totale)
        self.setWindowTitle('Jeu d\'échecs')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def sizeHint(self) -> QSize:
        taille_plateau = 8 * self.taille_case
        taille_totale = taille_plateau + 2 * self.taille_etiquette
        return QSize(taille_totale, taille_totale)

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

    def mousePressEvent(self, a0: QMouseEvent | None):
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
                        self.en_promotion = False
                        self.case_selectionnee = None
                        if self.historique_coups:
                            self.historique_coups.mettre_a_jour_coups()
                        self.update()
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
                                self.en_promotion = True
                                self.ligne_promotion = ligne_cliquee
                                self.colonne_promotion = colonne_cliquee
                                self.case_selectionnee = None
                                self.update()
                                return

                        if self.historique_coups:
                            self.historique_coups.mettre_a_jour_coups()
                        self.case_selectionnee = None
                        self.update()
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

        # State
        self.mode = self.MODE_PVP
        self.couleur_joueur = self.COULEUR_BLANC # 0 blanc, 1 noir, 2 aleatoire
        self.difficulte = 0

        self.ajouter_boutons()

    def ajouter_boutons(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.historique = HistoriqueCoups(self.partie, self.echelle_police)
        layout.addWidget(self.historique, stretch=1)

        boutons_layout = QHBoxLayout()
        boutons_layout.setSpacing(6)
        boutons_layout.setContentsMargins(0, 0, 0, 0)

        COTE = 56 
        bouton_style_base = """
            QPushButton {{
                font-size: 22px;
                border: 2px solid #c8b89a;
                border-radius: 6px;
                background-color: {bg};
                color: {fg};
                min-width: {side}px;
                max-width: {side}px;
                min-height: {side}px;
                max-height: {side}px;
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

        def _style(bg="#f5efe6", fg="#333", hover="#ead9c0", pressed="#d4b896"):
            return bouton_style_base.format(bg=bg, fg=fg, hover=hover, pressed=pressed, side=COTE)

        self.btn_mode = QPushButton("👤")
        self.btn_mode.setToolTip("Mode : Joueur vs Joueur / Joueur vs IA")
        self.btn_mode.setStyleSheet(_style())
        self.btn_mode.clicked.connect(self.cycler_mode_jeu)

        self.btn_couleur = QPushButton("⬜")
        self.btn_couleur.setToolTip("Couleur du joueur")
        self.btn_couleur.setStyleSheet(_style())
        self.btn_couleur.clicked.connect(self.cycler_couleur)
        self.btn_couleur.setEnabled(False)

        self.btn_difficulte = QPushButton("0")
        self.btn_difficulte.setToolTip("Difficulté de l'IA")
        self.btn_difficulte.setStyleSheet(_style())
        self.btn_difficulte.clicked.connect(self.cycler_difficulte)
        self.btn_difficulte.setEnabled(False)

        for bouton in (self.btn_mode, self.btn_couleur, self.btn_difficulte):
            boutons_layout.addWidget(bouton)

        layout.addLayout(boutons_layout)
        
        # Bouton Jouer
        self.btn_jouer = QPushButton("Jouer")
        self.btn_jouer.setToolTip("Démarrer la partie")
        self.btn_jouer.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #2d7a2d;
                border-radius: 6px;
                background-color: #4caf50;
                color: white;
                min-height: 40px;
                padding: 0 12px;
            }
            QPushButton:hover {
                background-color: #43a047;
                border-color: #1b5e1b;
            }
            QPushButton:pressed {
                background-color: #388e3c;
            }
        """)
        self.btn_jouer.clicked.connect(self.on_jouer)
        layout.addWidget(self.btn_jouer)
        self.setMinimumWidth(200)
        self.rafraichir_boutons()

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

    def on_jouer(self):
        ...

class GUI(QMainWindow):
    def __init__(self, partie: Partie):
        super().__init__()
        echelle_police = QGuiApplication.primaryScreen().logicalDotsPerInch() / 96.0
        self.partie = partie
        self.panneau = PanneauLateral(partie, echelle_police)
        self.echiquier = Echiquier(partie, self.panneau.historique, echelle_police)
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