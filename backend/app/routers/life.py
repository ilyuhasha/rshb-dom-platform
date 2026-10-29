"""API: «Жизнь после ипотеки» (Задача 3) + авторизация и контур клиента."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..init_db import verify_password
from ..models import LifeService, LifeAction, Mortgage, User

router = APIRouter(prefix="/api/life", tags=["life"])


# ---------- Авторизация (демо: простой токен с временем жизни) ----------

class LoginIn(BaseModel):
    username: str
    password: str


_tokens: dict = {}  # демо-хранилище токенов в памяти процесса


@router.post("/login")
def login(data: LoginIn, db: Session = Depends(get_db)):
    user = db.execute(
        select(User).where(User.username == data.username)
    ).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Неверный логин или пароль")
    token = f"tk-{user.id}-{int(datetime.utcnow().timestamp())}"
    _tokens[token] = user.id
    return {"token": token, "user": {
        "id": user.id, "username": user.username,
        "full_name": user.full_name, "is_admin": user.is_admin}}


def current_user(request_header: str | None, db: Session) -> User | None:
    if not request_header or not request_header.startswith("Bearer "):
        return None
    token = request_header[7:]
    uid = _tokens.get(token)
    if uid is None:
        return None
    return db.get(User, uid)


# ---------- Каталог сервисов ----------

@router.get("/services")
def list_services(db: Session = Depends(get_db)):
    rows = db.execute(
        select(LifeService).where(LifeService.is_active == True)  # noqa: E712
        .order_by(LifeService.sort)
    ).scalars().all()
    return [{
        "key": r.key, "title": r.title, "category": r.category,
        "icon": r.icon, "description": r.description,
        "calculator": r.calculator, "requires_auth": r.requires_auth,
    } for r in rows]


@router.get("/services/{key}")
def get_service(key: str, db: Session = Depends(get_db)):
    row = db.execute(
        select(LifeService).where(LifeService.key == key)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Сервис не найден")
    return {
        "key": row.key, "title": row.title, "category": row.category,
        "icon": row.icon, "description": row.description,
        "how_to": row.how_to, "docs": row.docs, "hints": row.hints,
        "calculator": row.calculator, "requires_auth": row.requires_auth,
    }


# ---------- Демо-данные гостя vs банковский контур ----------

DEMO_MORTGAGE = {
    "name": "Демо: ипотека «Своё Жильё»",
    "object_address": "г. Рязань, ул. Садовая, д. 10, кв. 42",
    "object_type": "Квартира",
    "principal": 5200000.0, "rate": 14.0, "term_months": 300,
    "monthly_payment": 61847.0, "paid_months": 18,
    "remaining_debt": 5030000.0,
    "start_date": "2024-06-01", "insurance_end": "2027-06-01",
    "next_payment_date": "2026-11-12",
}


@router.get("/context")
def get_context(authorization: str | None = Header(None),
                db: Session = Depends(get_db)):
    """Гость получает демо-данные; авторизованный — свои кредиты из БД
    («банковский контур»)."""
    user = current_user(authorization, db)
    if user:
        mortgages = db.execute(
            select(Mortgage).where(Mortgage.user_id == user.id)
        ).scalars().all()
        src = "bank"
    else:
        mortgages = db.execute(
            select(Mortgage).where(Mortgage.user_id == 1)  # демо-пользователь
        ).scalars().all()
        src = "demo"
    data = [{
        "name": m.name, "object_address": m.object_address,
        "object_type": m.object_type, "principal": m.principal,
        "rate": m.rate, "term_months": m.term_months,
        "monthly_payment": m.monthly_payment, "paid_months": m.paid_months,
        "remaining_debt": m.remaining_debt, "start_date": m.start_date,
        "insurance_end": m.insurance_end,
        "next_payment_date": m.next_payment_date,
    } for m in mortgages]
    return {
        "source": src,
        "user": (user.full_name if user else "Гость (демо-данные)"),
        "mortgages": data if data else [DEMO_MORTGAGE],
    }


# ---------- Действия пользователя ----------

class ActionIn(BaseModel):
    service_key: str
    status: str = "planned"
    payload: dict = {}


@router.post("/actions")
def create_action(a: ActionIn, authorization: str | None = Header(None),
                  db: Session = Depends(get_db)):
    user = current_user(authorization, db)
    if not user:
        raise HTTPException(401, "Требуется вход (демо: demo/demo)")
    db.add(LifeAction(user_id=user.id, service_key=a.service_key,
                      status=a.status, payload=a.payload))
    db.commit()
    return {"ok": True}


@router.get("/actions")
def list_actions(authorization: str | None = Header(None),
                 db: Session = Depends(get_db)):
    user = current_user(authorization, db)
    if not user:
        raise HTTPException(401, "Требуется вход")
    rows = db.execute(
        select(LifeAction).where(LifeAction.user_id == user.id)
        .order_by(LifeAction.id.desc())
    ).scalars().all()
    return [{"id": r.id, "service_key": r.service_key, "status": r.status,
             "payload": r.payload, "created_at": r.created_at.isoformat()}
            for r in rows]
