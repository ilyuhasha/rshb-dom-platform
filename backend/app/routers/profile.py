"""API: личный кабинет пользователя.

Собирает в одном месте всё, что сделал пользователь:
  - прогресс по сценариям навигатора (таск-трекер),
  - черновики/историю расчётов симулятора,
  - ипотеки («банковский контур»),
  - планы по сервисам «Жизнь после ипотеки».
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LifeAction, Mortgage, NavProgress, NavScenario, SimCalculation, User
from .auth import require_user

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/summary")
def summary(db: Session = Depends(get_db),
            user: User = Depends(require_user)):
    """Сводка личного кабинета. Изоляция: только собственные данные."""
    # --- Прогресс навигатора ---
    scenarios = db.execute(
        select(NavScenario).where(NavScenario.is_active == True)  # noqa: E712
        .order_by(NavScenario.sort)
    ).scalars().all()
    progress_rows = db.execute(
        select(NavProgress).where(NavProgress.user_id == user.id)
    ).scalars().all()
    done_map: dict[str, int] = {}
    for p in progress_rows:
        if p.done:
            done_map[p.scenario_key] = done_map.get(p.scenario_key, 0) + 1
    nav = [{
        "scenario_key": s.key, "title": s.title,
        "done": done_map.get(s.key, 0),
        "total": sum(len(st.get("checklist", [])) for st in s.steps),
    } for s in scenarios]
    for n in nav:
        n["pct"] = round(n["done"] / n["total"] * 100) if n["total"] else 0

    # --- Черновики расчётов (последние 50) ---
    calcs = db.execute(
        select(SimCalculation).where(SimCalculation.user_id == user.id)
        .order_by(SimCalculation.id.desc()).limit(50)
    ).scalars().all()
    calculations = [{
        "id": c.id, "scenario_key": c.scenario_key,
        "created_at": c.created_at.isoformat(timespec="minutes"),
        "inputs": c.inputs, "results": c.results,
    } for c in calcs]

    # --- Ипотеки ---
    mortgages = db.execute(
        select(Mortgage).where(Mortgage.user_id == user.id)
    ).scalars().all()
    mortgages_out = [{
        "name": m.name, "object_address": m.object_address,
        "object_type": m.object_type, "principal": m.principal,
        "rate": m.rate, "term_months": m.term_months,
        "monthly_payment": m.monthly_payment, "paid_months": m.paid_months,
        "remaining_debt": m.remaining_debt,
        "next_payment_date": m.next_payment_date,
        "insurance_end": m.insurance_end,
    } for m in mortgages]

    # --- Планы по сервисам ---
    actions = db.execute(
        select(LifeAction).where(LifeAction.user_id == user.id)
        .order_by(LifeAction.id.desc())
    ).scalars().all()
    actions_out = [{
        "id": r.id, "service_key": r.service_key, "status": r.status,
        "created_at": r.created_at.isoformat(timespec="minutes"),
    } for r in actions]

    return {
        "user": {
            "username": user.username, "full_name": user.full_name,
            "role_title": "Администратор" if user.is_admin else "Пользователь",
            "created_at": user.created_at.isoformat(timespec="minutes"),
        },
        "nav": nav,
        "calculations": calculations,
        "mortgages": mortgages_out,
        "actions": actions_out,
    }


@router.delete("/calculations/{calc_id}")
def delete_calculation(calc_id: int, db: Session = Depends(get_db),
                       user: User = Depends(require_user)):
    obj = db.get(SimCalculation, calc_id)
    if not obj or obj.user_id != user.id:
        raise HTTPException(404, "Расчёт не найден")
    db.delete(obj)
    db.commit()
    return {"ok": True}


@router.delete("/calculations")
def clear_calculations(db: Session = Depends(get_db),
                       user: User = Depends(require_user)):
    db.execute(
        delete(SimCalculation).where(SimCalculation.user_id == user.id))
    db.commit()
    return {"ok": True}


@router.delete("/actions/{action_id}")
def delete_action(action_id: int, db: Session = Depends(get_db),
                  user: User = Depends(require_user)):
    obj = db.get(LifeAction, action_id)
    if not obj or obj.user_id != user.id:
        raise HTTPException(404, "Действие не найдено")
    db.delete(obj)
    db.commit()
    return {"ok": True}
