"""Schémas Pydantic du donjon : description d'une salle et body du déplacement."""

from typing import Literal

from pydantic import BaseModel


class MoveRequest(BaseModel):
    """Body de POST /heroes/{id}/move. Une direction inconnue renvoie automatiquement une 422."""

    direction: Literal["nord", "sud", "est", "ouest"]


class MonsterRead(BaseModel):
    """Monstre affronté par le héros (présent uniquement si un combat est en cours)."""

    nom: str
    pv: int
    pv_max: int
    attaque: int


class RoomRead(BaseModel):
    """Réponse de GET /heroes/{id}/room et de POST /heroes/{id}/move."""

    id: str
    nom: str
    description: str
    sorties: list[str]
    monstre: MonsterRead | None
