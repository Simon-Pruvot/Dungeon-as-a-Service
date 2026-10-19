"""Règles de combat des héros, sans dépendance à FastAPI ni à la base."""

import random
from abc import ABC, abstractmethod


class Heros(ABC):
    def __init__(self, force: int, agilite: int, intelligence: int):
        self.force = force
        self.agilite = agilite
        self.intelligence = intelligence

    @property
    def pv_max(self) -> int:
        return 20 + self.force * 2

    @abstractmethod
    def calculer_degats(self) -> tuple[int, bool]:
        """Renvoie (dégâts infligés, coup critique)."""

    def subir_degats(self, attaque_monstre: int) -> int:
        return attaque_monstre


class Guerrier(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 2 + self.force * 2, False

    def subir_degats(self, attaque_monstre: int) -> int:
        return max(1, attaque_monstre - 1)


class Mage(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        return 1 + self.intelligence * 3, False


class Voleur(Heros):
    def calculer_degats(self) -> tuple[int, bool]:
        degats = 2 + self.agilite * 2
        critique = random.randint(1, 3) == 1
        return (degats * 2 if critique else degats), critique


CLASSES: dict[str, type[Heros]] = {"guerrier": Guerrier, "mage": Mage, "voleur": Voleur}


def creer_heros(classe: str, force: int, agilite: int, intelligence: int) -> Heros:
    return CLASSES[classe](force, agilite, intelligence)
