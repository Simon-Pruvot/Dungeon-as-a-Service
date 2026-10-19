"""Routes d'authentification."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from app.database import get_session
from app.schemas.auth import PlayerCreate, PlayerRead, Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/register", response_model=PlayerRead, status_code=status.HTTP_201_CREATED)
def register(data: PlayerCreate, session: Session = Depends(get_session)):
    return auth_service.register(session, data)


@router.post("/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    return Token(access_token=auth_service.login(session, form.username, form.password))
