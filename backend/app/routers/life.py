"""API: «Жизнь после ипотеки» (Задача 3) + банковский контур клиента.

Авторизация — общая для всего приложения (см. routers/auth.py):
гость видит демо-данные, пользователь — свой банковский контур.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LifeService, LifeAction, Mortgage, User
from .auth import get_current_user, require_user

router = APIRouter(prefix="/api/life", tags=["life"])


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
def get_context(db: Session = Depends(get_db),
                user: User | None = Depends(get_current_user)):
    """Гость получает демо-данные; авторизованный — свои кредиты из БД
    («банковский контур»)."""
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
def create_action(a: ActionIn,
                  db: Session = Depends(get_db),
                  user: User = Depends(require_user)):
    db.add(LifeAction(user_id=user.id, service_key=a.service_key,
                      status=a.status, payload=a.payload))
    db.commit()
    return {"ok": True}


@router.get("/actions")
def list_actions(db: Session = Depends(get_db),
                 user: User = Depends(require_user)):
    rows = db.execute(
        select(LifeAction).where(LifeAction.user_id == user.id)
        .order_by(LifeAction.id.desc())
    ).scalars().all()
    return [{"id": r.id, "service_key": r.service_key, "status": r.status,
             "payload": r.payload, "created_at": r.created_at.isoformat()}
            for r in rows]
