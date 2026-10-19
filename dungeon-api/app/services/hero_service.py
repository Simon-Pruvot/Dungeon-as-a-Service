"""Logique des héros : création, lecture, conversion vers le schéma de sortie."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.models.hero import Hero
from app.schemas.hero import HeroCreate, HeroRead
from app.services.dungeon_map import START_ROOM


def create_hero(session: Session, data: HeroCreate) -> Hero:
    pv_max = 20 + data.force * 2
    hero = Hero(
        **data.model_dump(),  # nom, classe, force, agilite, intelligence
        pv=pv_max,  # le héros commence avec ses PV au maximum
        pv_max=pv_max,
        salle_actuelle=START_ROOM,
    )
    session.add(hero)
    session.commit()
    session.refresh(hero)  # récupère l'id attribué par la base
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


def to_hero_read(hero: Hero) -> HeroRead:
    # monstre_pv est ignoré par HeroRead (il n'en a pas le champ) : il n'apparaît pas dans la réponse
    return HeroRead(
        **hero.model_dump(),
        en_combat=hero.monstre_pv is not None,
        est_vivant=hero.pv > 0,
    )
