"""Comptes joueurs : hachage des mots de passe, tokens JWT, joueur connecté."""

import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlmodel import Session, select

from app.database import get_session
from app.models.player import Player
from app.schemas.auth import PlayerCreate

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-a-changer-en-production")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def _unauthorized(message: str) -> HTTPException:
    return HTTPException(
        status_code=401,
        detail={"error": "INVALID_TOKEN", "message": message},
        headers={"WWW-Authenticate": "Bearer"},
    )


def register(session: Session, data: PlayerCreate) -> Player:
    if session.exec(select(Player).where(Player.username == data.username)).first():
        raise HTTPException(
            status_code=409,
            detail={"error": "USERNAME_TAKEN", "message": f"Le nom {data.username} est déjà pris."},
        )
    player = Player(username=data.username, hashed_password=password_hash.hash(data.password))
    session.add(player)
    session.commit()
    session.refresh(player)
    return player


def login(session: Session, username: str, password: str) -> str:
    player = session.exec(select(Player).where(Player.username == username)).first()
    if player is None or not password_hash.verify(password, player.hashed_password):
        raise HTTPException(
            status_code=401,
            detail={"error": "INVALID_CREDENTIALS", "message": "Identifiants incorrects."},
            headers={"WWW-Authenticate": "Bearer"},
        )
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(player.id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_player(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
) -> Player:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        raise _unauthorized("Token invalide ou expiré.")
    player = session.get(Player, int(payload["sub"]))
    if player is None:
        raise _unauthorized("Ce joueur n'existe plus.")
    return player
