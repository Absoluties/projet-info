from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QInputDialog,
    QPlainTextEdit,
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QColor, QFont, QMouseEvent
from PyQt5.QtWidgets import QStyleFactory

from partie import Partie
from pion import Pion
from dame import Dame
from tour import Tour
from fou import Fou
from cavalier import Cavalier


class HistoriqueCoups(QPlainTextEdit):
    def __init__(self, partie: Partie):
        super().__init__()
        self.partie = partie
        self.setReadOnly(True)
        self.setMaximumWidth(250)
        self.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #f5f5f5;
                color: #333333;
                border: 1px solid #e0e0e0;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11pt;
                padding: 10px;
            }
        """)
        self.mettre_a_jour_coups()

    def mettre_a_jour_coups(self):
        texte = ""
        coups = self.partie.historique_str

        for i in range(0, len(coups), 2):
            numero_coup = i // 2 + 1
            coup_blanc = coups[i] if i < len(coups) else ""
            coup_noir = coups[i + 1] if i + 1 < len(coups) else ""

            # Aligner tous les points
            ligne_coup = f"{numero_coup:2}. {coup_blanc:<11}"
            if coup_noir:
                ligne_coup += f" {coup_noir}"

            texte += ligne_coup + "\n"

        self.setPlainText(texte)
        # Scroller vers le bas
        if barre_defilement := self.verticalScrollBar():
            barre_defilement.setValue(barre_defilement.maximum())


class EchiquierUI(QWidget):
    def __init__(self, partie: Partie, historique_coups: HistoriqueCoups):
        super().__init__()
        self.partie = partie
        self.taille_case = 60
        self.taille_etiquette = 30
        self.piece_selectionnee = None
        self.historique_coups: HistoriqueCoups = historique_coups
        self.init_ui()

    def init_ui(self):
        taille_plateau = 8 * self.taille_case
        taille_totale = taille_plateau + 2 * self.taille_etiquette
        self.setGeometry(100, 100, taille_totale, taille_totale)
        self.setWindowTitle('Jeu d\'échecs')

    def sizeHint(self) -> QSize:
        taille_plateau = 8 * self.taille_case
        taille_totale = taille_plateau + 2 * self.taille_etiquette
        return QSize(taille_totale, taille_totale)

    def paintEvent(self, a0):
        peintre = QPainter(self)
        peintre.setRenderHint(QPainter.Antialiasing)

        # Dessiner les cases de l'échiquier (inversées pour que les blancs soient en bas)
        for ligne in range(8):
            for colonne in range(8):
                ligne_affichee = 7 - ligne
                x = self.taille_etiquette + colonne * self.taille_case
                y = self.taille_etiquette + ligne_affichee * self.taille_case

                # Couleurs alternées de l'échiquier (palette moderne)
                if (ligne + colonne) % 2 == 0:
                    couleur = QColor(240, 217, 181)  # Case claire
                else:
                    couleur = QColor(189, 172, 135)  # Case foncée

                peintre.fillRect(x, y, self.taille_case, self.taille_case, couleur)

                # Dessiner la bordure
                peintre.drawRect(x, y, self.taille_case, self.taille_case)

        # Dessiner les étiquettes des colonnes (a-h)
        police = QFont("Arial", 12)
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

        # Dessiner les étiquettes des rangées (8-1, affichées de haut en bas)
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

        # Dessiner les pièces
        self.dessiner_pieces(peintre)

        # Dessiner les cases en surbrillance
        self.dessiner_surbrillances(peintre)

    def dessiner_pieces(self, peintre: QPainter):
        police = QFont("Arial", 36, QFont.Bold)
        peintre.setFont(police)

        for ligne in range(0, 8):
            for colonne in range(8):
                piece = self.partie.plateau[ligne][colonne]
                if piece is not None:
                    ligne_affichee = 7 - ligne
                    x = self.taille_etiquette + colonne * self.taille_case
                    y = self.taille_etiquette + ligne_affichee * self.taille_case

                    # Dessiner le texte de la pièce (couleurs inversées pour Unicode)
                    if piece.couleur == 0:
                        peintre.setPen(QColor(255, 255, 255))  # Pièces blanches
                    else:
                        peintre.setPen(QColor(0, 0, 0))        # Pièces noires

                    peintre.drawText(
                        x,
                        y,
                        self.taille_case,
                        self.taille_case,
                        Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter,
                        piece.representation,
                    )

    def dessiner_surbrillances(self, peintre: QPainter):
        if self.piece_selectionnee is None:
            return

        ligne, colonne = self.piece_selectionnee
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

    def mousePressEvent(self, a0: QMouseEvent | None):
        if a0 is None:
            return

        x = a0.x() - self.taille_etiquette
        y = a0.y() - self.taille_etiquette

        if x < 0 or y < 0 or x >= 8 * self.taille_case or y >= 8 * self.taille_case:
            self.piece_selectionnee = None
        else:
            colonne = x // self.taille_case
            ligne_affichee = y // self.taille_case
            ligne = 7 - ligne_affichee

            # Vérifier si une pièce est déjà sélectionnée
            if self.piece_selectionnee is not None:
                ligne_selectionnee, colonne_selectionnee = self.piece_selectionnee
                piece_selectionnee = self.partie.plateau[ligne_selectionnee][colonne_selectionnee]

                if piece_selectionnee is not None:
                    coup = ((ligne_selectionnee, colonne_selectionnee), (ligne, colonne))
                    type_piece = type(piece_selectionnee)

                    # Valider le coup avant de le jouer
                    if self.partie.verifier_validite_coup(coup, type_piece):
                        self.partie.jouer_coup(coup)
                        self.traiter_promotion(ligne, colonne)
                        if self.historique_coups:
                            self.historique_coups.mettre_a_jour_coups()
                        self.piece_selectionnee = None
                        self.update()
                        return

            # Sélectionner ou désélectionner une pièce
            if self.partie.plateau[ligne][colonne] is not None:
                self.piece_selectionnee = (ligne, colonne)
            else:
                self.piece_selectionnee = None

        self.update()

    def traiter_promotion(self, ligne: int, colonne: int):
        piece = self.partie.plateau[ligne][colonne]

        # Vérifier si un pion a atteint la fin
        if not isinstance(piece, Pion):
            return

        est_blanc = piece.couleur == 0
        ligne_promotion = 7 if est_blanc else 0

        if ligne != ligne_promotion:
            return

        options = ["Dame", "Tour", "Fou", "Cavalier"]
        choix, ok = QInputDialog.getItem(
            self, "Promotion de pion", "Choisissez la pièce:", options, 0, False
        )

        if not ok:
            return

        pieces_promotion = {
            "Dame": Dame,
            "Tour": Tour,
            "Fou": Fou,
            "Cavalier": Cavalier,
        }

        classe_piece = pieces_promotion[choix]
        piece_promue = classe_piece(ligne, colonne, piece.couleur, self.partie)
        self.partie.plateau[ligne][colonne] = piece_promue


class FenetreEchiquier(QMainWindow):
    def __init__(self, partie: Partie):
        super().__init__()
        self.partie = partie
        self.historique_coups = HistoriqueCoups(partie)
        self.echiquier = EchiquierUI(partie, self.historique_coups)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Jeu d\'échecs')
        self.setStyle(QStyleFactory.create('Fusion'))
        taille_plateau = 8 * self.echiquier.taille_case
        taille_totale = taille_plateau + 2 * self.echiquier.taille_etiquette

        # Créer un widget central avec une disposition horizontale
        widget_central = QWidget()
        widget_central.setStyleSheet("background-color: #ffffff;")
        disposition = QHBoxLayout(widget_central)
        disposition.setSpacing(15)
        disposition.setContentsMargins(10, 10, 10, 10)
        disposition.addWidget(self.echiquier)
        disposition.addWidget(self.historique_coups)
        self.setCentralWidget(widget_central)

        self.setGeometry(100, 100, taille_totale + 220, taille_totale + 50)
        self.show()
