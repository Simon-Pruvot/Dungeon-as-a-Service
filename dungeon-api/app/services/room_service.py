"""Logique du donjon : description de la salle courante et déplacement du héros."""

import logging

from fastapi import HTTPException
from sqlmodel import Session

from app.models.hero import Hero
from app.schemas.room import MonsterRead, RoomRead
from app.services.dungeon_map import get_monster_of_room, get_room
from app.services.hero_service import ensure_alive, ensure_not_in_combat

logger = logging.getLogger("dungeon")


def describe_room(hero: Hero) -> RoomRead:
    room = get_room(hero.salle_actuelle)

    monstre = None
    monster = get_monster_of_room(hero.salle_actuelle)
    if monster is not None and hero.monstre_pv is not None:
        monstre = MonsterRead(
            nom=monster["name"],
            pv=hero.monstre_pv,
            pv_max=monster["hp"],
            attaque=monster["attack"],
        )

    return RoomRead(
        id=hero.salle_actuelle,
        nom=room["name"],
        description=room["description"],
        sorties=list(room["exits"].keys()),
        monstre=monstre,
    )


def move_hero(session: Session, hero: Hero, direction: str) -> RoomRead:
    ensure_alive(hero)
    ensure_not_in_combat(hero)

    room = get_room(hero.salle_actuelle)
    destination = room["exits"].get(direction)
    if destination is None:
        raise HTTPException(
            status_code=400,
            detail={"error": "NO_EXIT", "message": f"Il n'y a pas de passage vers le {direction}."},
        )

    hero.salle_actuelle = destination
    # le donjon est maudit : le monstre réapparaît à chaque entrée
    monster = get_monster_of_room(destination)
    hero.monstre_pv = monster["hp"] if monster is not None else None

    session.add(hero)
    session.commit()
    session.refresh(hero)
    logger.info("Héros %s se déplace vers %s (%s)", hero.id, destination, direction)
    return describe_room(hero)
