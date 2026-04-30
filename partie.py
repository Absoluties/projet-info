import numpy as np
from pion import Pion
from roi import Roi
from dame import Dame
from cavalier import Cavalier
from tour import Tour
from fou import Fou

class Partie():
    def __init__(self):
        self.partie_finie = False
        self.plateau = [[None] * 8] * 8
        self.historique:list[str] = []
        self.tour:int = 0
    
    def completer_coup_notation_abregee(self, position, type_piece) -> tuple[tuple[int, int], tuple[int, int]]:
        ...
    
    def verifier_syntaxe_coup(self, notation) -> bool:
        ...
    
    def verifier_validite_coup(self, position, type_piece) -> bool:
        ...
    
    def choisir_coup_cmd(self, coup):
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
        
        type_piece;
        while not self.verifier_syntaxe_coup(coup := input(f'Tour des [{"NOIRS" if self.tour%0 else "BLANCS"}], choissisez un coup (notation standard) : ').strip().lower()):
            print("Coup invalide, utilisez la notation française standard.")

        match coup[0]:
            case 'p':
                type_piece = Pion
                coup = coup[1:]
            case 'r':
                type_piece = Roi
                coup = coup[1:]
            case 'd':
                type_piece = Dame
                coup = coup[1:]
            case 't':
                type_piece = Tour
                coup = coup[1:]
            case 'f':
                type_piece = Fou
                coup = coup[1:]
            case 'c':
                type_piece = Cavalier
                coup = coup[1:]
            case _:
                type_piece = Pion

        if '-' in coup:
            coup = coup.split('-')
        if 'x' in coup:
            coup = coup.split('x')
        
        # On donne seulement la position d'arrivee : il faut déterminer la piece jouée
        if type(coup) == str:
            position = (ord(coup[0]) - ord('a'), int(coup[1:]))
            coup = self.completer_coup_notation_abregee(position, type_piece)
        elif type(coup) == list:
            coup = [(ord(morceau[0]) - ord('a'), int(morceau[1:])) for morceau in coup]
        
        return coup
        
    def commencer(self, mode='cmd'):
        if mode=='cmd':
            while not self.partie_finie:
                while not self.verifier_validite_coup(coup:= self.choisir_coup_cmd()):
                    print("Coup illicite, recommencez.")                
                
         
    
    def jouer_coup(self, id:str, coup:str, depart:tuple[int,int], arrivee:tuple[int,int]):
        self.historique.append(coup)
        self.plateau[depart[0], depart[1]] = None
        self.plateau[arrivee[0], arrivee[1]] = id

        self.tour += 1
        
    
        
        