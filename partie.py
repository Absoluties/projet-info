# Auteur : Aidan
from piece import Piece
from pion import Pion
from roi import Roi
from dame import Dame
from cavalier import Cavalier
from tour import Tour
from fou import Fou
from piece import Piece
import json


class Partie:
    def __init__(self):
        self.rois = {0: Roi(0, 4, 0, self), 1: Roi(7, 4, 1, self)}

        self.roques_possibles = {
            0: [True, True],
            1: [True, True],
        }  # [grand roque, petit roque]

        self.plateau: list[list[Piece | None]] = [
            [
                Tour(0, 0, 0, self),
                Cavalier(0, 1, 0, self),
                Fou(0, 2, 0, self),
                Dame(0, 3, 0, self),
                self.rois[0],
                Fou(0, 5, 0, self),
                Cavalier(0, 6, 0, self),
                Tour(0, 7, 0, self),
            ],
            [
                Pion(1, 0, 0, self),
                Pion(1, 1, 0, self),
                Pion(1, 2, 0, self),
                Pion(1, 3, 0, self),
                Pion(1, 4, 0, self),
                Pion(1, 5, 0, self),
                Pion(1, 6, 0, self),
                Pion(1, 7, 0, self),
            ],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [
                Pion(6, 0, 1, self),
                Pion(6, 1, 1, self),
                Pion(6, 2, 1, self),
                Pion(6, 3, 1, self),
                Pion(6, 4, 1, self),
                Pion(6, 5, 1, self),
                Pion(6, 6, 1, self),
                Pion(6, 7, 1, self),
            ],
            [
                Tour(7, 0, 1, self),
                Cavalier(7, 1, 1, self),
                Fou(7, 2, 1, self),
                Dame(7, 3, 1, self),
                self.rois[1],
                Fou(7, 5, 1, self),
                Cavalier(7, 6, 1, self),
                Tour(7, 7, 1, self),
            ],
        ]
        self.historique: list[tuple] = []
        self.historique_str: list[str] = []
        self.tour: int = 0

    def completer_coup_notation_abregee(
        self, position_arrivee: tuple[int, int], type_piece: str
    ) -> tuple[tuple[int, int], tuple[int, int]]:
        """Trouve la pièce du type donné pouvant atteindre position_arrivee et retourne le coup complet."""
        for i in range(8):
            for j in range(8):
                piece_sur_case: Piece | None = self.plateau[i][j]
                if piece_sur_case is not None and piece_sur_case.type == type_piece:
                    if (
                        piece_sur_case.couleur == self.tour % 2
                        and position_arrivee in piece_sur_case.cases_atteignables()
                    ):
                        return ((i, j), position_arrivee)
        # (0,0)→(0,0) est toujours un coup invalide : une pièce ne peut pas se déplacer sur elle-même
        return ((0, 0), (0, 0))

    def est_case(self, case: str) -> bool:
        """Retourne True si la chaîne représente une case valide en notation algébrique (ex: 'e4')."""
        if len(case) == 2:
            return (ord("a") <= ord(case[0]) <= ord("h")) and (
                ord("1") <= ord(case[1]) <= ord("8")
            )
        return False

    def verifier_syntaxe_coup(self, notation: str) -> bool:
        """Retourne True si la chaîne de notation de coup est syntaxiquement valide."""
        initiales_pieces = ("p", "t", "c", "f", "d", "r")

        if not notation.isalnum():
            return False

        match len(notation):
            case 2:  # Coup de pion implicite (ex: e4)
                return self.est_case(notation)
            case 3:  # Coup de pièce implicite (ex: Ce4)
                return (notation[0] in initiales_pieces) and self.est_case(
                    notation[1:3]
                )
            case 4:  # Coup de pion explicite (ex: e2e4)
                return self.est_case(notation[0:2]) and self.est_case(notation[2:4])
            case 5:  # Coup de pièce explicite (ex: Cc3e4)
                return (
                    (notation[0] in initiales_pieces)
                    and self.est_case(notation[1:3])
                    and self.est_case(notation[3:5])
                )
            case _:
                return False

    def verifier_validite_coup(
        self, coup: tuple[tuple[int, int], tuple[int, int]], type_piece: str
    ) -> bool:
        """Retourne True si le coup est légal pour une pièce du type donné appartenant au joueur actuel."""
        piece_sur_case: Piece | None = self.plateau[coup[0][0]][coup[0][1]]
        if (
            piece_sur_case is not None
            and piece_sur_case.type == type_piece
            and piece_sur_case.couleur == self.tour % 2
            and coup[1] in piece_sur_case.cases_atteignables()
        ):
            return True
        return False

    def choisir_coup_cmd(self) -> tuple[tuple[tuple[int, int], tuple[int, int]], str]:
        """Lit un coup en notation française depuis le terminal et retourne (coup, type_pièce).

        Notation acceptée (française, minuscules) :
          P/p pion, T/t tour, C/c cavalier, F/f fou, D/d dame, R/r roi.
          Formes : 'e4', 'Ce4', 'e2-e4', 'Ce2xf4' (le tiret et 'x' sont ignorés).
        """
        while True:
            coup_notation = (
                input(
                    f'Tour des [{"NOIRS" if self.tour%2 else "BLANCS"}], choissisez un coup (notation standard) : '
                )
                .strip()
                .lower()
                .replace("-", "")
                .replace("x", "")
            )
            if self.verifier_syntaxe_coup(coup_notation):
                break
            print("Syntaxe du coup invalide, utilisez la notation française standard.")

        # Les coups de pion (2 ou 4 caractères) n'ont pas de lettre de pièce : on la préfixe
        if len(coup_notation) in (2, 4):
            coup_notation = "p" + coup_notation

        match coup_notation[0]:
            case "p":
                type_piece = "P"
            case "r":
                type_piece = "R"
            case "d":
                type_piece = "D"
            case "t":
                type_piece = "T"
            case "f":
                type_piece = "F"
            case "c":
                type_piece = "C"
            case _:
                raise RuntimeError()

        coup_notation = coup_notation[1:]
        coup_machine_str = coup_notation[:2], coup_notation[2:]

        if not coup_machine_str[1]:
            # Notation abrégée : seule la case d'arrivée est fournie
            position = (
                int(coup_machine_str[0][1]) - 1,
                ord(coup_machine_str[0][0]) - ord("a"),
            )
            coup_machine = self.completer_coup_notation_abregee(position, type_piece)
        else:
            coup_machine = (
                (
                    int(coup_machine_str[0][1]) - 1,
                    ord(coup_machine_str[0][0]) - ord("a"),
                ),
                (
                    int(coup_machine_str[1][1]) - 1,
                    ord(coup_machine_str[1][0]) - ord("a"),
                ),
            )

        return coup_machine, type_piece

    def verifier_fin(self) -> int:
        """Retourne -1 si la partie est en cours, 0 en cas d'égalite et 1 en cas de défaite du joueur actuel."""
        roi: Roi = self.rois[self.tour % 2]
        for ligne in self.plateau:
            for piece in ligne:
                if not piece is None and piece.couleur == roi.couleur:
                    if len(piece.cases_atteignables()):
                        return -1
        if roi.attaquee():
            return 1
        return 0

    def print_plateau(self) -> None:
        """Affiche le plateau dans le terminal avec les coordonnées algébriques."""
        plateau_str = "\n"
        plateau_str += "    a   b   c   d   e   f   g   h\n"
        plateau_str += "  ┌───┬───┬───┬───┬───┬───┬───┬───┐\n"
        for i, ligne in enumerate(self.plateau[::-1]):
            numero_ligne = 8 - i
            plateau_str += f"{numero_ligne} │"
            for piece in ligne:
                caractere = piece.representation if piece else " "
                plateau_str += f" {caractere} │"
            plateau_str += f" {numero_ligne}\n"
            if i != 7:
                plateau_str += "  ├───┼───┼───┼───┼───┼───┼───┼───┤\n"
        plateau_str += "  └───┴───┴───┴───┴───┴───┴───┴───┘\n"
        plateau_str += "    a   b   c   d   e   f   g   h\n"
        print(plateau_str)

    def ajouter_historique(self, coup: tuple[tuple, tuple]) -> None:
        """Enregistre le coup dans l'historique (coordonnées brutes et notation algébrique)."""
        piece: Piece = self.plateau[coup[0][0]][coup[0][1]]
        if self.plateau[coup[1][0]][coup[1][1]]:
            separateur = "x"
        else:
            separateur = "-"
        notations_cases: list[str] = [
            chr(case[1] + ord("a")) + str(case[0] + 1) for case in coup
        ]
        self.historique.append(coup)
        self.historique_str.append(
            f"{piece.type}{notations_cases[0]}{separateur}{notations_cases[1]}"
        )

    def est_roque(self, piece: Piece, depart: tuple, arrivee: tuple) -> bool:
        """Retourne True si le coup est un roque (roi se déplaçant de deux cases)."""
        return (
            piece is not None and piece.type == "R" and abs(arrivee[1] - depart[1]) == 2
        )

    def est_en_passant(self, piece: Piece, depart: tuple, arrivee: tuple) -> bool:
        """Retourne True si le coup est une prise en passant (pion en diagonale vers case vide)."""
        return (
            piece is not None
            and piece.type == "P"
            and abs(arrivee[1] - depart[1]) == 1
            and self.plateau[arrivee[0]][arrivee[1]] is None
        )

    def jouer_coup(self, coup: tuple[tuple[int, int], tuple[int, int]]) -> None:
        """Applique le coup sur le plateau en gérant le roque et la prise en passant."""
        self.ajouter_historique(coup)
        depart, arrivee = coup

        piece_depart: Piece | None = self.plateau[depart[0]][depart[1]]

        if piece_depart is None:
            return

        piece_depart.position = arrivee

        # Mise à jour des droits de roque dès qu'une tour ou un roi bouge
        if piece_depart.type == "T" and depart in ((0, 0), (0, 7), (7, 0), (7, 7)):
            self.roques_possibles[piece_depart.couleur][depart[1] // 7] = False
        elif piece_depart.type == "R":
            self.roques_possibles[piece_depart.couleur] = [False, False]
        # Capturer la tour adverse sur sa case de départ révoque aussi le droit de roque
        if arrivee in ((0, 0), (0, 7), (7, 0), (7, 7)):
            self.roques_possibles[(piece_depart.couleur + 1) % 2][
                arrivee[1] // 7
            ] = False

        if self.est_en_passant(piece_depart, depart, arrivee):
            # Suppression du pion capturé en passant (il est sur la même rangée que le pion preneur)
            self.plateau[arrivee[0] - (-1) ** piece_depart.couleur][arrivee[1]] = None

        if self.est_roque(piece_depart, depart, arrivee):
            y1 = (
                7 * (1 + (arrivee[1] - depart[1]) // 2) // 2
            )  # colonne d'origine de la tour (0 ou 7)
            y2 = (
                depart[1] + (arrivee[1] - depart[1]) // 2
            )  # colonne d'arrivée de la tour
            # Positionnement de la tour
            self.plateau[depart[0]][y1], self.plateau[depart[0]][y2] = (
                self.plateau[depart[0]][y2],
                self.plateau[depart[0]][y1],
            )
            # Et mise à jour de sa position
            tour_piece = self.plateau[depart[0]][y2]
            if tour_piece is not None:
                tour_piece.position = (depart[0], y2)

        self.plateau[arrivee[0]][arrivee[1]] = self.plateau[depart[0]][depart[1]]
        self.plateau[depart[0]][depart[1]] = None

        self.tour += 1

    def jouer_partie_cmd(self, mode="cmd") -> None:
        """Lance une partie en ligne de commande (méthode de débogage utilisée avant que l'interface graphique soit implémentée)."""
        self.print_plateau()
        fin = -1
        while fin == -1:
            while True:
                coup, type_piece = self.choisir_coup_cmd()
                if self.verifier_validite_coup(coup, type_piece):
                    break
                print("Coup illicite, recommencez.")
            self.jouer_coup(coup)
            self.print_plateau()
            fin = self.verifier_fin()
        if fin:
            print(f"Le joueur {('Blanc','Noir')[(self.tour-1)%2]} a gagné")
        else:
            print("Égalité")

    def sauvegarder(self, chemin: str, promotions: list[str | None]) -> None:
        """Sauvegarde l'historique des coups et les promotions dans un fichier JSON."""
        data = {
            "historique": [
                [[coup[0][0], coup[0][1]], [coup[1][0], coup[1][1]]]
                for coup in self.historique
            ],
            "promotions": promotions,
        }
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def charger(chemin: str) -> tuple["Partie", list[str | None]]:
        """Charge et rejoue une partie depuis un fichier JSON. Retourne (partie, liste_promotions)."""
        TYPE_VERS_CLASSE = {"D": Dame, "T": Tour, "F": Fou, "C": Cavalier}

        with open(chemin, "r", encoding="utf-8") as f:
            data = json.load(f)

        partie = Partie()
        promotions: list[str | None] = data.get("promotions", [])

        for i, coup_data in enumerate(data["historique"]):
            coup = (tuple(coup_data[0]), tuple(coup_data[1]))
            partie.jouer_coup(coup)
            type_promo = promotions[i] if i < len(promotions) else None
            if type_promo is not None and type_promo in TYPE_VERS_CLASSE:
                arrivee = coup[1]
                piece = partie.plateau[arrivee[0]][arrivee[1]]
                if piece is not None:
                    couleur = piece.couleur
                    partie.plateau[arrivee[0]][arrivee[1]] = TYPE_VERS_CLASSE[
                        type_promo
                    ](arrivee[0], arrivee[1], couleur, partie)

        return partie, promotions
