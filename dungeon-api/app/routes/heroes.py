"""Routes des héros : uniquement la couche HTTP, la logique est dans le service."""

from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database import get_session
from app.schemas.hero import HeroCreate, HeroRead
from app.schemas.room import MoveRequest, RoomRead
from app.services import hero_service, room_service

router = APIRouter(prefix="/heroes", tags=["Héros"])


@router.post("", response_model=HeroRead, status_code=status.HTTP_201_CREATED)
def create_hero(data: HeroCreate, session: Session = Depends(get_session)):
    hero = hero_service.create_hero(session, data)
    return hero_service.to_hero_read(hero)


@router.get("", response_model=list[HeroRead])
def list_heroes(session: Session = Depends(get_session)):
    heroes = hero_service.list_heroes(session)
    return [hero_service.to_hero_read(hero) for hero in heroes]


@router.get("/{hero_id}", response_model=HeroRead)
def read_hero(hero_id: int, session: Session = Depends(get_session)):
    hero = hero_service.get_hero(session, hero_id)
    return hero_service.to_hero_read(hero)


@router.get("/{hero_id}/room", response_model=RoomRead)
def read_room(hero_id: int, session: Session = Depends(get_session)):
    hero = hero_service.get_hero(session, hero_id)
    return room_service.describe_room(hero)


@router.post("/{hero_id}/move", response_model=RoomRead)
def move_hero(hero_id: int, data: MoveRequest, session: Session = Depends(get_session)):
    hero = hero_service.get_hero(session, hero_id)
    return room_service.move_hero(session, hero, data.direction)
