import sys
from PyQt5.QtWidgets import QApplication

from partie import Partie
from gui import GUI


if __name__ == '__main__':
    partie = Partie()

    if '--cmd' in sys.argv:
        partie.jouer_partie(mode='cmd')
    else:
        app = QApplication(sys.argv)
        fenetre = GUI(partie)
        sys.exit(app.exec_())