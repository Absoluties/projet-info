from abc import ABC, abstractmethod


class IA:
    def __init__(self, niveau):
        self.niveau = niveau

    @abstractmethod
    def choisir_coup(self) -> tuple:
        pass
