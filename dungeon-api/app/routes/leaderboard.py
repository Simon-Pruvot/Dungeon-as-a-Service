"""Classement public des héros."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_session
from app.schemas.hero import HeroRead
from app.services import hero_service

router = APIRouter(prefix="/leaderboard", tags=["Classement"])


@router.get("", response_model=list[HeroRead])
def leaderboard(session: Session = Depends(get_session)):
    return [hero_service.to_hero_read(hero) for hero in hero_service.leaderboard(session)]
