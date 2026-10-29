"""API: авторизация и роли (Гость / Пользователь / Администратор).

Три уровня доступа:
  guest  — без авторизации: демо-данные, расчёты без истории
  user   — вход по паролю: свои расчёты, прогресс, банковский контур
  admin  — отдельный пароль: + управление сценариями, формулами,
           параметрами и подсказками

Токены демонстрационные (в памяти процесса); пароли хранятся как
pbkdf2-hmac-sha256 с солью (256 тыс. итераций).
"""
import hashlib
import hmac
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

# ---------------- Хеширование паролей (pbkdf2 + соль) ----------------

PBKDF2_ITERATIONS = 260_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode(), PBKDF2_ITERATIONS)
    return f"pbkdf2${salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """Проверяет пароль; поддерживает старый формат sha256 (миграция)."""
    if stored.startswith("pbkdf2$"):
        try:
            _, salt, hexdig = stored.split("$", 2)
        except ValueError:
            return False
        dk = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode(), PBKDF2_ITERATIONS)
        return hmac.compare_digest(dk.hex(), hexdig)
    # легаси-демо sha256 (до обновления) — сравнение постоянного времени
    legacy = hashlib.sha256(password.encode("utf-8")).hexdigest()
    return hmac.compare_digest(legacy, stored)


# ---------------- Токены (демо-хранилище в памяти) ----------------

_tokens: dict[str, int] = {}          # token -> user.id
_token_exp: dict[str, datetime] = {}  # token -> срок действия
TOKEN_TTL_HOURS = 12


def _issue_token(user_id: int) -> str:
    token = "tk-" + secrets.token_urlsafe(24)
    _tokens[token] = user_id
    _token_exp[token] = datetime.utcnow()  # заменяется при проверке
    from datetime import timedelta
    _token_exp[token] = datetime.utcnow() + timedelta(hours=TOKEN_TTL_HOURS)
    return token


def _token_valid(token: str) -> bool:
    exp = _token_exp.get(token)
    return exp is not None and datetime.utcnow() <= exp


# ---------------- Зависимости (роли) ----------------

def resolve_user(authorization: str | None, db: Session) -> User | None:
    """Возвращает пользователя по заголовку Authorization или None (гость)."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization[7:]
    uid = _tokens.get(token)
    if uid is None or not _token_valid(token):
        _tokens.pop(token, None)
        _token_exp.pop(token, None)
        return None
    return db.get(User, uid)


def get_current_user(authorization: str | None = Header(None),
                     db: Session = Depends(get_db)) -> User | None:
    return resolve_user(authorization, db)


def require_user(user: User | None = Depends(get_current_user)) -> User:
    if user is None:
        raise HTTPException(401, "Требуется вход в систему")
    return user


def require_admin(user: User = Depends(require_user)) -> User:
    if not user.is_admin:
        raise HTTPException(403, "Доступ только для администратора")
    return user


# ---------------- Схемы ----------------

class LoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9_.-]+$")
    password: str = Field(min_length=4, max_length=128)
    full_name: str = Field(default="", max_length=128)


def user_payload(u: User, token: str | None = None) -> dict:
    role = "admin" if u.is_admin else "user"
    role_title = "Администратор" if u.is_admin else "Пользователь"
    out = {
        "id": u.id, "username": u.username, "full_name": u.full_name,
        "role": role, "role_title": role_title,
    }
    if token:
        out["token"] = token
    return out


# ---------------- Эндпоинты ----------------

@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.username == data.username)
    ).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    token = _issue_token(user.id)
    return {"ok": True, **user_payload(user, token)}


@router.post("/register")
def register(data: RegisterIn, db: Session = Depends(get_db)):
    """Самостоятельная регистрация — всегда роль «Пользователь»."""
    exists = db.execute(
        select(User).where(User.username == data.username)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Такой логин уже занят")
    u = User(username=data.username,
             password_hash=hash_password(data.password),
             full_name=data.full_name or data.username,
             is_admin=False)
    db.add(u)
    db.commit()
    token = _issue_token(u.id)
    return {"ok": True, **user_payload(u, token)}


@router.get("/me")
def me(user: User | None = Depends(get_current_user)):
    """Проверка токена при загрузке страницы. Гость — role=guest."""
    if user is None:
        return {"role": "guest", "role_title": "Гость",
                "user": None}
    return user_payload(user)


@router.post("/logout")
def logout(authorization: str | None = Header(None)):
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        _tokens.pop(token, None)
        _token_exp.pop(token, None)
    return {"ok": True}


# Для остальных роутеров (life/nav/sim) — общий доступ к хранилищу токенов
def get_user_from_header(authorization: str | None, db: Session) -> User | None:
    return resolve_user(authorization, db)
