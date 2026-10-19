"""Logique des héros : création, lecture, conversion vers le schéma de sortie."""

from fastapi import HTTPException
from sqlmodel import Session, select

from app.domain.heros import creer_heros
from app.models.hero import Hero
from app.models.player import Player
from app.schemas.hero import HeroCreate, HeroRead
from app.services.dungeon_map import START_ROOM


def create_hero(session: Session, data: HeroCreate, player: Player) -> Hero:
    pv_max = creer_heros(data.classe, data.force, data.agilite, data.intelligence).pv_max
    hero = Hero(
        **data.model_dump(), pv=pv_max, pv_max=pv_max, salle_actuelle=START_ROOM, owner_id=player.id
    )
    session.add(hero)
    session.commit()
    session.refresh(hero)
    return hero


def list_heroes(session: Session, player: Player) -> list[Hero]:
    return list(session.exec(select(Hero).where(Hero.owner_id == player.id)).all())


def leaderboard(session: Session) -> list[Hero]:
    query = select(Hero).order_by(Hero.victoire.desc(), Hero.or_.desc()).limit(10)
    return list(session.exec(query).all())


def get_hero(session: Session, hero_id: int, player: Player) -> Hero:
    hero = session.get(Hero, hero_id)
    if hero is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "HERO_NOT_FOUND", "message": f"Aucun héros avec l'id {hero_id}."},
        )
    if hero.owner_id != player.id:
        raise HTTPException(
            status_code=403,
            detail={"error": "NOT_YOUR_HERO", "message": "Ce héros appartient à un autre joueur."},
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
