from piece import Piece
from pion import Pion
from roi import Roi
from dame import Dame
from cavalier import Cavalier
from tour import Tour
from fou import Fou
from piece import Piece
from ia import IA
from ia_random import IARandom
from ia_ft import IA_fort


class Partie:
    def __init__(self):
        self.rois = {0: Roi(0, 4, 0, self), 1: Roi(7, 4, 1, self)}

        self.roques_possibles = {0: [True, True], 1: [True, True]}  # grand, petit roque

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
        """
        Il n'y a pas de manière simple de déterminer quelle est la seule pièce qui peut effectuer un certain coup, donc on vérifie toute les cases jusqu'à la trouver.
        On pourrait accélérer la fonction en cherchant depuis les cases de départs possibles selon le type de pièce mais on a pas besoin du gain de performance.
        """
        for i in range(8):
            for j in range(8):
                piece_sur_case: Piece | None = self.plateau[i][j]
                if piece_sur_case is not None and piece_sur_case.type == type_piece:
                    if (
                        piece_sur_case.couleur == self.tour % 2
                        and position_arrivee in piece_sur_case.cases_atteignables()
                    ):
                        return ((i, j), position_arrivee)
        return (
            (0, 0),
            (0, 0),
        )  # Ce coup est toujours impossible (une pièce ne peut pas se déplacer sur elle-même)

    def est_case(self, case: str) -> bool:
        if len(case) == 2:
            return (ord("a") <= ord(case[0]) <= ord("h")) and (ord("1") <= ord(case[1]) <= ord("8"))
        return False

    def verifier_syntaxe_coup(self, notation: str) -> bool:
        initiales_pieces = ("p", "t", "c", "f", "d", "r")

        if not notation.isalnum():
            return False

        match len(notation):
            case 2:  # Coup de pion implicite
                return self.est_case(notation)
            case 3:  # Coup de pièce quelconque implicite
                return (notation[0] in initiales_pieces) and self.est_case(notation[1:3])
            case 4:  # Coup de pion explicite
                return self.est_case(notation[0:2]) and self.est_case(notation[2:4])
            case 5:  # Coup de pièce quelconque explicite
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
        piece_sur_case: Piece | None = self.plateau[coup[0][0]][coup[0][1]]
        if (
            piece_sur_case is not None
            and piece_sur_case.type == type_piece
            and piece_sur_case.couleur == self.tour % 2
            and coup[1] in piece_sur_case.cases_atteignables()
        ):
            return True
        return False

    def choisir_coup_cmd(self):
        """
        Chaque camp est composé de seize pièces, notées ainsi dans la notation française :
            un roi, noté R
            une dame, notée D
            deux tours, notées T
            deux fous, notés F
            deux cavaliers, notés C
            huit pions, notés P en notation complète et non notés en notation abrégée.
        Au début de la partie, les pièces sont disposées sur l'échiquier comme indiqué sur le diagramme plus haut. Au centre, le roi et la dame (la dame sur la case de sa couleur sur la colonne d), puis de part et d'autre, les deux fous, les deux cavaliers puis les deux tours. Les 8 pions occupent la rangée située immédiatement devant ces pièces.
        La notation des pièces ci-dessus ne prend en compte que le type des pièces : par exemple, F désigne un fou blanc ou noir, on identifie chaque pièce individuellement sur l'échiquier en indiquant la case sur laquelle elle se trouve.
        Il n'est pas nécessaire normalement de noter le pion (il suffit d'indiquer sa case), mais quand on le fait, on utilise la lettre P en français.
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

        # Il faut faire attention pour les pions à ne pas confondre la lettre de la case pour le type de pièce
        if len(coup_notation) in (2, 4):
            coup_notation = "p" + coup_notation

        match coup_notation[0]:
            case "p":
                type_piece = "P"
                coup_notation = coup_notation[1:]
            case "r":
                type_piece = "R"
                coup_notation = coup_notation[1:]
            case "d":
                type_piece = "D"
                coup_notation = coup_notation[1:]
            case "t":
                type_piece = "T"
                coup_notation = coup_notation[1:]
            case "f":
                type_piece = "F"
                coup_notation = coup_notation[1:]
            case "c":
                type_piece = "C"
                coup_notation = coup_notation[1:]
            case _:
                raise RuntimeError()

        coup_machine_str = coup_notation[:2], coup_notation[2:]

        # On donne seulement la position d'arrivée : il faut déterminer la piece jouée
        if not coup_machine_str[1]:
            position = (int(coup_machine_str[0][1]) - 1, ord(coup_machine_str[0][0]) - ord("a"))
            coup_machine = self.completer_coup_notation_abregee(position, type_piece)
        else:
            coup_machine = (
                (int(coup_machine_str[0][1]) - 1, ord(coup_machine_str[0][0]) - ord("a")),
                (int(coup_machine_str[1][1]) - 1, ord(coup_machine_str[1][0]) - ord("a")),
            )

        return coup_machine, type_piece

    def verifier_victoire(self):
        """
        Pour vérifier la fin de la partie, il faut essayer tout les coups potentiels du joueur en échec.
        """
        roi: Roi = self.rois[self.tour % 2]
        if roi.attaquee():
            print("Roi en echec")
            for ligne in self.plateau:
                for piece in ligne:
                    if not piece is None and piece.couleur == roi.couleur:
                        if len(piece.cases_atteignables()):
                            return False
            return True

    def print_plateau(self):
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
        piece: Piece = self.plateau[coup[0][0]][coup[0][1]]
        if self.plateau[coup[1][0]][coup[1][1]]:
            separateur = "x"
        else:
            separateur = "-"
        notations_cases: list[str] = [chr(case[1] + ord("a")) + str(case[0] + 1) for case in coup]
        self.historique.append(coup)
        self.historique_str.append(
            f"{piece.type}{notations_cases[0]}{separateur}{notations_cases[1]}"
        )
        # print(f"Coup joué {self.historique_str[-1]}")

    def est_roque(self, piece: Piece, depart: tuple, arrivee: tuple) -> bool:
        # Roi se déplaçant de deux cases
        return piece is not None and piece.type == "R" and abs(arrivee[1] - depart[1]) == 2

    def est_en_passant(self, piece: Piece, depart: tuple, arrivee: tuple) -> bool:
        # Pion se déplaçant en diagonale vers une case vide = en passant
        return (
            piece is not None
            and piece.type == "P"
            and abs(arrivee[1] - depart[1]) == 1
            and self.plateau[arrivee[0]][arrivee[1]] is None
        )

    def jouer_coup(self, coup: tuple[tuple[int, int], tuple[int, int]]) -> None:
        self.ajouter_historique(coup)
        depart, arrivee = coup

        piece_depart: Piece | None = self.plateau[depart[0]][depart[1]]

        if piece_depart is None:
            return

        piece_depart.position = arrivee

        # Garder la trace des coups désactivant les roques évitent des vérifications de l'historique
        if piece_depart.type == "T":
            self.roques_possibles[piece_depart.couleur][piece_depart.position[1] // 7] = False
        elif piece_depart.type == "R":
            self.roques_possibles[piece_depart.couleur] = [False, False]
        if arrivee in ((0, 0), (0, 7), (7, 0), (7, 7)):
            self.roques_possibles[(piece_depart.couleur + 1) % 2][arrivee[1] // 7] = False

        if self.est_en_passant(piece_depart, depart, arrivee):
            self.plateau[arrivee[0] - (-1) ** piece_depart.couleur][arrivee[1]] = None

        if self.est_roque(piece_depart, depart, arrivee):
            y1 = 7 * (1 + (arrivee[1] - depart[1]) // 2) // 2
            y2 = depart[1] + (arrivee[1] - depart[1]) // 2
            self.plateau[depart[0]][y1], self.plateau[depart[0]][y2] = (
                self.plateau[depart[0]][y2],
                self.plateau[depart[0]][y1],
            )

        self.plateau[arrivee[0]][arrivee[1]] = self.plateau[depart[0]][depart[1]]
        self.plateau[depart[0]][depart[1]] = None

        self.tour += 1

    def jouer_partie_cmd(self, mode="cmd"):
        self.print_plateau()
        ia = IA_fort(4, self)
        while not self.verifier_victoire():
            if self.tour % 2 == 1:
                print("Coup de l'IA")
                coup = ia.choisir_coup()
                self.jouer_coup(coup)
                self.print_plateau()
                continue
            while True:
                coup, type_piece = self.choisir_coup_cmd()
                if self.verifier_validite_coup(coup, type_piece):
                    break
                print("Coup illicite, recommencez.")
            self.jouer_coup(coup)
            self.print_plateau()
        print(f"Le joueur {('Blanc','Noir')[(self.tour-1)%2]} a gagné")
