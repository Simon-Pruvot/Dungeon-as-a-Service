"""Routes des héros : uniquement la couche HTTP, la logique est dans les services."""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.models.player import Player
from app.schemas.combat import AttackResult
from app.schemas.hero import HeroCreate, HeroRead
from app.schemas.room import MoveRequest, RoomRead
from app.services import combat_service, hero_service, room_service
from app.services.auth_service import get_current_player

router = APIRouter(prefix="/heroes", tags=["Héros"])


@router.post("", response_model=HeroRead, status_code=status.HTTP_201_CREATED)
def create_hero(
    data: HeroCreate,
    session: Session = Depends(get_session),
    player: Player = Depends(get_current_player),
):
    hero = hero_service.create_hero(session, data, player)
    return hero_service.to_hero_read(hero)


@router.get("", response_model=list[HeroRead])
def list_heroes(session: Session = Depends(get_session), player: Player = Depends(get_current_player)):
    heroes = hero_service.list_heroes(session, player)
    return [hero_service.to_hero_read(hero) for hero in heroes]


@router.get("/{hero_id}", response_model=HeroRead)
def read_hero(
    hero_id: int, session: Session = Depends(get_session), player: Player = Depends(get_current_player)
):
    hero = hero_service.get_hero(session, hero_id, player)
    return hero_service.to_hero_read(hero)


@router.get("/{hero_id}/room", response_model=RoomRead)
def read_room(
    hero_id: int, session: Session = Depends(get_session), player: Player = Depends(get_current_player)
):
    hero = hero_service.get_hero(session, hero_id, player)
    return room_service.describe_room(hero)


@router.post("/{hero_id}/move", response_model=RoomRead)
def move_hero(
    hero_id: int,
    data: MoveRequest,
    session: Session = Depends(get_session),
    player: Player = Depends(get_current_player),
):
    hero = hero_service.get_hero(session, hero_id, player)
    return room_service.move_hero(session, hero, data.direction)


@router.post("/{hero_id}/attack", response_model=AttackResult)
def attack(
    hero_id: int, session: Session = Depends(get_session), player: Player = Depends(get_current_player)
):
    hero = hero_service.get_hero(session, hero_id, player)
    return combat_service.attack(session, hero)


@router.post("/{hero_id}/rest", response_model=HeroRead)
async def rest(
    hero_id: int, session: Session = Depends(get_session), player: Player = Depends(get_current_player)
):
    hero = hero_service.get_hero(session, hero_id, player)
    hero = await combat_service.rest(session, hero)
    return hero_service.to_hero_read(hero)
