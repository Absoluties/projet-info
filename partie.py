import numpy as np
from pion import Pion
from roi import Roi
from dame import Dame
from cavalier import Cavalier
from tour import Tour
from fou import Fou
from piece import Piece

class Partie():
    def __init__(self):
        self.partie_finie = False
        self.plateau = [
            [Tour(0,0,0), Cavalier(0,1,0), Fou(0,2,0), Dame(0,3,0), Roi(0,4,0), Fou(0,5,0), Cavalier(0,6,0), Tour(0,7,0)],
            [Pion(1,0,0), Pion(1,1,0), Pion(1,2,0), Pion(1,3,0), Pion(1,4,0), Pion(1,5,0), Pion(1,6,0), Pion(1,7,0)],
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [Pion(6,0,1), Pion(6,1,1), Pion(6,2,1), Pion(6,3,1), Pion(6,4,1), Pion(6,5,1), Pion(6,6,1), Pion(6,7,1)],
            [Tour(7,0,1), Cavalier(7,1,1), Fou(7,2,1), Dame(7,3,1), Roi(7,4,1), Fou(7,5,1), Cavalier(7,6,1), Tour(7,7,1)]
        ]
        self.historique:list[str] = []
        self.tour:int = 0
        
        self.position_roi_blanc = (0,3)
        self.position_roi_noir = (7,4)
    
    def completer_coup_notation_abregee(self, position:tuple[int, int], type_piece:Piece) -> tuple[tuple[int, int], tuple[int, int]]:
        '''
        Il n'y a pas de manière simple de déterminer quelle est la seule pièce qui peut effectuer un certain coup, donc on vérifie toute les cases jusqu'à la trouver.
        '''
        for i in range(8):
            for j in range(8):
                piece_sur_case:Piece = self.plateau[i][j]
                if type(piece_sur_case) != None:
                    if piece_sur_case.couleur == self.tour%2 and position in piece_sur_case.cases_atteignables():
                        return ((i,j), position)
    
    def est_case(self, case:str) -> bool:
        if len(case) == 2:
            return (ord('a') <= ord(case[0]) <= ord('h')) and (ord('1') <= ord(case[1]) <= ord('8'))
        return False
    
    def verifier_syntaxe_coup(self, notation:str) -> bool:      
        initiales_pieces = ('p', 't', 'c', 'f', 'd', 'r')
        
        if not notation.isalnum():
            return False
        
        print(notation)
        match len(notation):
            case 2: # Coup de pion implicite
                return self.est_case(notation)
            case 3: # Coup de pièce quelconque implicite
                return (notation[0] in initiales_pieces) and self.est_case(notation[1:3])
            case 4: # Coup de pion explicite
                return self.est_case(notation[0:2]) and self.est_case(notation[2:4])
            case 5: # Coup de pièce quelconque explicite
                return (notation[0] in initiales_pieces) and self.est_case(notation[1:3]) and self.est_case(notation[3:5])
            case _:
                return False
    
    def verifier_validite_coup(self, coup:tuple[tuple[int, int], tuple[int, int]], type_piece:Piece) -> bool:
        piece_sur_case:Piece = self.plateau[coup[0][0], coup[0][1]]
        if piece_sur_case.couleur != self.tour%2:
            return False
        if coup[1] in piece_sur_case.cases_atteignables():
            return True
        return False
    
    def choisir_coup_cmd(self):
        '''
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
        '''
        
        while True:
            coup_notation = input(f'Tour des [{"NOIRS" if self.tour%2 else "BLANCS"}], choissisez un coup (notation standard) : ').strip().lower().replace('-', '').replace('x', '')
            if self.verifier_syntaxe_coup(coup_notation):
                break
            print("Syntaxe du coup invalide, utilisez la notation française standard.")

        # Il faut faire attention pour les pions à ne pas confondre la lettre de la case pour le type de pièce
        if len(coup_notation) in (2,4):
            coup_notation = 'p' + coup_notation               

        match coup_notation[0]:
            case 'p':
                type_piece = Pion
                coup_notation = coup_notation[1:]
            case 'r':
                type_piece = Roi
                coup_notation = coup_notation[1:]
            case 'd':
                type_piece = Dame
                coup_notation = coup_notation[1:]
            case 't':
                type_piece = Tour
                coup_notation = coup_notation[1:]
            case 'f':
                type_piece = Fou
                coup_notation = coup_notation[1:]
            case 'c':
                type_piece = Cavalier
                coup_notation = coup_notation[1:]
            case _:
                raise RuntimeError()

        coup_machine = coup_notation.split('')
        
        # On donne seulement la position d'arrivée : il faut déterminer la piece jouée
        if len(coup_machine) == 1:
            position = (ord(coup_machine[0][0]) - ord('a'), int(coup_machine[0][1]))
            coup_machine = self.completer_coup_notation_abregee(position, type_piece)
        elif len(coup_machine) == 2:
            coup_machine = ((ord(coup_machine[0][0]) - ord('a'), int(coup_machine[0][1])), (ord(coup_machine[1][0]) - ord('a'), int(coup_machine[1][1])))

        return coup_machine, type_piece
     
    def verifier_victoire(self):
        '''
        Pour vérifier la fin de la partie, il faut essayer tout les coups potentiels du joueur en échec.
        '''
        if self.tour%2: # Les noirs viennent de jouer
            roi:Roi = self.plateau[self.position_roi_blanc[0]][self.position_roi_blanc[1]]
        else:
            roi:Roi = self.plateau[self.position_roi_noir[0]][self.position_roi_noir[1]]
        if roi.echec():
            ...
        
        return False
    
    def print_plateau(self):
        print(self.plateau)
        res = '—.—.—.—.—.—.—.—\n'
        for ligne in self.plateau[::-1]:
            res += '|'.join([piece.representation if piece else ' ' for piece in ligne])
            res += '\n—.—.—.—.—.—.—.—\n'
        print(res)
    
    def jouer_coup(self, depart:tuple[int,int], arrivee:tuple[int,int]):
        self.plateau[arrivee[0], arrivee[1]] = self.plateau[depart[0], depart[1]]
        piece_arrivee = self.plateau[arrivee[0], arrivee[1]]
        piece_arrivee.position = arrivee
        if type(piece_arrivee) == Roi:
            if piece_arrivee.couleur == 0: # Blanc
                self.position_roi_blanc = arrivee
            else:
                self.position_roi_noir = arrivee
        
        self.plateau[depart[0], depart[1]] = None

        self.tour += 1
    
    def jouer_partie(self, mode='cmd'):
        if mode=='cmd':
            self.print_plateau()
            while not self.partie_finie:
                while True:
                    coup, type_piece = self.choisir_coup_cmd()
                    print(coup, type_piece)
                    if self.verifier_validite_coup(coup, type_piece):
                        break
                    print("Coup illicite, recommencez.")   
                self.jouer_coup(coup[0], coup[1])
                self.print_plateau()
                self.verifier_victoire()
    
        
        