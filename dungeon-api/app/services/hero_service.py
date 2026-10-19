"""Logique des héros : création, lecture, conversion vers le schéma de sortie."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.domain.heros import creer_heros
from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroRead
from app.services.dungeon_map import START_ROOM


def create_hero(session: Session, data: HeroCreate) -> Hero:
    pv_max = creer_heros(data.classe, data.force, data.agilite, data.intelligence).pv_max
    hero = Hero(**data.model_dump(), pv=pv_max, pv_max=pv_max, salle_actuelle=START_ROOM)
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


def list_heroes(session: Session) -> list[Hero]:
    return list(session.exec(select(Hero)).all())


def get_hero(session: Session, hero_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "HERO_NOT_FOUND", "message": f"Aucun héros avec l'id {hero_id}."},
        )
    return hero


def ensure_alive(hero: Hero) -> None:
    if hero.pv <= 0:
        raise HTTPException(
            status_code=409,
            detail={"error": "HERO_DEAD", "message": f"{hero.nom} est mort et ne peut plus agir."},
        )


def ensure_not_in_combat(hero: Hero) -> None:
    if hero.monstre_pv is not None:
        raise HTTPException(
            status_code=409,
            detail={"error": "IN_COMBAT", "message": "Un monstre vous barre la route, il faut le combattre."},
        )


def to_hero_read(hero: Hero) -> HeroRead:
    return HeroRead(
        **hero.model_dump(),
        en_combat=hero.monstre_pv is not None,
        est_vivant=hero.pv > 0,
    )
