"""Combat et repos du héros."""

import asyncio
import logging

from fastapi import HTTPException
from sqlmodel import Session

from app.domain.heros import creer_heros
from app.models.hero import Hero
from app.schemas.combat import AttackResult
from app.services.dungeon_map import FINAL_ROOM, get_monster_of_room
from app.services.hero_service import ensure_alive, ensure_not_in_combat

logger = logging.getLogger("dungeon")


def attack(session: Session, hero: Hero) -> AttackResult:
    ensure_alive(hero)
    if hero.monstre_pv is None:
        raise HTTPException(
            status_code=409,
            detail={"error": "NO_MONSTER", "message": "Il n'y a aucun monstre à attaquer ici."},
        )

    monster = get_monster_of_room(hero.salle_actuelle)
    heros = creer_heros(hero.classe, hero.force, hero.agilite, hero.intelligence)

    degats, critique = heros.calculer_degats()
    hero.monstre_pv = max(0, hero.monstre_pv - degats)
    pv_monstre = hero.monstre_pv
    degats_subis = 0
    or_gagne = 0

    if hero.monstre_pv == 0:
        issue = "monstre_vaincu"
        hero.monstre_pv = None
        or_gagne = monster["gold"]
        hero.or_ += or_gagne
        if hero.salle_actuelle == FINAL_ROOM:
            hero.victoire = True
    else:
        degats_subis = heros.subir_degats(monster["attack"])
        hero.pv = max(0, hero.pv - degats_subis)
        issue = "en_cours"
        if hero.pv == 0:
            issue = "heros_mort"
            hero.monstre_pv = None

    session.add(hero)
    session.commit()
    session.refresh(hero)

    logger.info(
        "Héros %s frappe %s : %d dégâts%s, subit %d, issue=%s",
        hero.id, monster["name"], degats, " (critique)" if critique else "", degats_subis, issue,
    )
    return AttackResult(
        degats_infliges=degats,
        critique=critique,
        degats_subis=degats_subis,
        pv_heros=hero.pv,
        pv_monstre=pv_monstre,
        issue=issue,
        or_gagne=or_gagne,
        victoire=hero.victoire,
    )


async def rest(session: Session, hero: Hero) -> Hero:
    ensure_alive(hero)
    ensure_not_in_combat(hero)
    await asyncio.sleep(3)
    hero.pv = hero.pv_max
    session.add(hero)
    session.commit()
    session.refresh(hero)
    logger.info("Héros %s s'est reposé", hero.id)
    return hero
