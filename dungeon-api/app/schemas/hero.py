"""Schémas Pydantic des héros : ce qui entre dans l'API et ce qui en sort."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


class HeroCreate(BaseModel):
    """Body de POST /heroes. Toute donnée invalide renvoie automatiquement une 422."""

    nom: str = Field(min_length=3, max_length=20)
    classe: Literal["guerrier", "mage", "voleur"]
    force: int = Field(ge=1, le=8)
    agilite: int = Field(ge=1, le=8)
    intelligence: int = Field(ge=1, le=8)

    @model_validator(mode="after")
    def verifier_somme_stats(self):
        # Exécuté après la validation des champs : on peut donc additionner sans risque
        if self.force + self.agilite + self.intelligence != 10:
            raise ValueError("La somme force + agilite + intelligence doit valoir exactement 10")
        return self


class HeroRead(BaseModel):
    """Réponse renvoyée par l'API : monstre_pv est remplacé par en_combat et est_vivant."""

    id: int
    nom: str
    classe: str
    force: int
    agilite: int
    intelligence: int
    pv: int
    pv_max: int
    salle_actuelle: str
    or_: int
    victoire: bool
    en_combat: bool
    est_vivant: bool
