from tkinter import S

import piece
from pion import Pion
from roi import Roi
from dame import Dame
from cavalier import Cavalier
from tour import Tour
from fou import Fou
from piece import Piece


class Partie:
    def __init__(self):
        self.partie_finie = False
        self.plateau:list[list] = [
            [
                Tour(0, 0, 0, self),
                Cavalier(0, 1, 0, self),
                Fou(0, 2, 0, self),
                Dame(0, 3, 0, self),
                Roi(0, 4, 0, self),
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
                Roi(7, 4, 1, self),
                Fou(7, 5, 1, self),
                Cavalier(7, 6, 1, self),
                Tour(7, 7, 1, self),
            ],
        ]
        self.historique:list[tuple] = []
        self.historique_str:list[str] = []
        self.tour:int = 0

        self.rois = {
            0: self.plateau[0][4],
            1: self.plateau[7][4]
        }

    def completer_coup_notation_abregee(self, position_arrivee: tuple[int, int], type_piece: type) -> tuple[tuple[int, int], tuple[int, int]]:
        """
        Il n'y a pas de manière simple de déterminer quelle est la seule pièce qui peut effectuer un certain coup, donc on vérifie toute les cases jusqu'à la trouver.
        """
        for i in range(8):
            for j in range(8):
                piece_sur_case:Piece = self.plateau[i][j]
                if type(piece_sur_case) is type_piece:
                    if piece_sur_case.couleur == self.tour % 2 and position_arrivee in piece_sur_case.cases_atteignables(self.plateau, self.historique):
                        return ((i, j), position_arrivee)
        return False

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

    def verifier_validite_coup(self, coup: tuple[tuple[int, int], tuple[int, int]], type_piece: Piece) -> bool:
        piece_sur_case: Piece = self.plateau[coup[0][0]][coup[0][1]]
        if type(piece_sur_case) is type_piece and piece_sur_case.couleur == self.tour % 2 and coup[1] in piece_sur_case.cases_atteignables(self.plateau, self.historique):
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
                type_piece = Pion
                coup_notation = coup_notation[1:]
            case "r":
                type_piece = Roi
                coup_notation = coup_notation[1:]
            case "d":
                type_piece = Dame
                coup_notation = coup_notation[1:]
            case "t":
                type_piece = Tour
                coup_notation = coup_notation[1:]
            case "f":
                type_piece = Fou
                coup_notation = coup_notation[1:]
            case "c":
                type_piece = Cavalier
                coup_notation = coup_notation[1:]
            case _:
                raise RuntimeError()

        coup_machine_str = coup_notation[:2], coup_notation[2:]
        
        # On donne seulement la position d'arrivée : il faut déterminer la piece jouée
        if not coup_machine_str[1]:
            position = (int(coup_machine_str[0][1])-1, ord(coup_machine_str[0][0]) - ord("a"))
            coup_machine = self.completer_coup_notation_abregee(position, type_piece)
            if not coup_machine:
                return ((0,0),(0,0)), Piece
        else:
            coup_machine = (
                (int(coup_machine_str[0][1])-1, ord(coup_machine_str[0][0]) - ord("a")),
                (int(coup_machine_str[1][1])-1, ord(coup_machine_str[1][0]) - ord("a"))
            )

        return coup_machine, type_piece

    def verifier_victoire(self):
        """
        Pour vérifier la fin de la partie, il faut essayer tout les coups potentiels du joueur en échec.
        """
        roi:Roi = self.rois[self.tour%2]
        if roi.attaquee(self.plateau):
            print('Roi en echec')
            for ligne in self.plateau:
                for piece in ligne:
                    if not piece is None and piece.couleur == roi.couleur:
                        if len(piece.cases_atteignables(self.plateau, self.historique)):
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

    def ajouter_historique(self, coup:tuple[tuple,tuple]) -> None:
        piece:Piece = self.plateau[coup[0][0]][coup[0][1]]
        if self.plateau[coup[1][0]][coup[1][1]]:
            separateur = 'x'
        else:
            separateur = '-'
        notations_cases:list[str] = [chr(case[1] + ord("a")) + str(case[0] + 1) for case in coup]
        self.historique.append(coup)
        self.historique_str.append(f"{piece.type}{notations_cases[0]}{separateur}{notations_cases[1]}")
        print(f'Coup joué {self.historique_str[-1]}')

    def est_en_passant(self, depart: tuple[int, int], arrivee: tuple[int, int]) -> bool:
        piece:Piece = self.plateau[depart[0]][depart[1]]
        # Pion se déplaçant en diagonale vers une case vide = en passant
        return piece is not None and piece.type == 'P' and abs(arrivee[1] - depart[1]) == 1 and self.plateau[arrivee[0]][arrivee[1]] is None
        

    def jouer_coup(self, coup: tuple[tuple[int,int], tuple[int,int]]) -> None:
        self.ajouter_historique(coup)
        depart, arrivee = coup

        piece_depart:Piece = self.plateau[depart[0]][depart[1]]
        piece_depart.position = arrivee

        if self.est_en_passant(depart, arrivee):                         
            self.plateau[arrivee[0] - (-1) ** piece_depart.couleur][arrivee[1]] = None

        self.plateau[arrivee[0]][arrivee[1]] = self.plateau[depart[0]][depart[1]]
        self.plateau[depart[0]][depart[1]] = None

        self.tour += 1

    def jouer_partie(self, mode="cmd"):
        if mode == "cmd":
            self.print_plateau()
            while not self.partie_finie:
                while True:
                    coup, type_piece = self.choisir_coup_cmd()
                    if self.verifier_validite_coup(coup, type_piece):
                        break
                    print("Coup illicite, recommencez.")
                self.jouer_coup(coup)
                self.print_plateau()
                if self.verifier_victoire():
                    print(f'Le joueur {(self.tour-1)%2} a gagné')
                    break
