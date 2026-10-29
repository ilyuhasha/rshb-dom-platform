"""API: навигатор «Путь к своему дому» (Задача 2) + прогресс."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import NavScenario, NavProgress

router = APIRouter(prefix="/api/nav", tags=["navigator"])


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    rows = db.execute(
        select(NavScenario).where(NavScenario.is_active == True)  # noqa: E712
        .order_by(NavScenario.sort)
    ).scalars().all()
    return [{
        "key": r.key, "title": r.title, "icon": r.icon, "short": r.short,
        "color": r.color,
        "stages": [s["stage"] for s in r.steps],
        "steps_count": len(r.steps),
        "checklist_count": sum(len(s.get("checklist", [])) for s in r.steps),
    } for r in rows]


@router.get("/scenarios/{key}")
def get_scenario(key: str, db: Session = Depends(get_db)):
    row = db.execute(
        select(NavScenario).where(NavScenario.key == key)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Сценарий не найден")
    return {
        "key": row.key, "title": row.title, "icon": row.icon,
        "description": row.description, "color": row.color, "steps": row.steps,
    }


class ProgressIn(BaseModel):
    scenario_key: str
    step_key: str
    item_index: int
    done: bool


@router.post("/progress")
def set_progress(p: ProgressIn, user_id: int = 1, db: Session = Depends(get_db)):
    """Демо-режим: прогресс пишется для user_id=1 (гость).
    В ЛК — под токен авторизованного пользователя."""
    obj = db.execute(
        select(NavProgress).where(
            NavProgress.user_id == user_id,
            NavProgress.scenario_key == p.scenario_key,
            NavProgress.step_key == p.step_key,
            NavProgress.item_index == p.item_index,
        )
    ).scalar_one_or_none()
    if obj:
        obj.done = p.done
    else:
        obj = NavProgress(user_id=user_id, scenario_key=p.scenario_key,
                          step_key=p.step_key, item_index=p.item_index,
                          done=p.done)
        db.add(obj)
    db.commit()
    return {"ok": True}


@router.get("/progress/{scenario_key}")
def get_progress(scenario_key: str, user_id: int = 1,
                 db: Session = Depends(get_db)):
    rows = db.execute(
        select(NavProgress).where(
            NavProgress.user_id == user_id,
            NavProgress.scenario_key == scenario_key,
        )
    ).scalars().all()
    return [{"step_key": r.step_key, "item_index": r.item_index,
             "done": r.done} for r in rows]


@router.post("/progress/{scenario_key}/reset")
def reset_progress(scenario_key: str, user_id: int = 1,
                   db: Session = Depends(get_db)):
    rows = db.execute(
        select(NavProgress).where(
            NavProgress.user_id == user_id,
            NavProgress.scenario_key == scenario_key,
        )
    ).scalars().all()
    for r in rows:
        db.delete(r)
    db.commit()
    return {"ok": True}


# ---- Админ: управление сценариями навигатора ----

class NavScenarioIn(BaseModel):
    key: str
    title: str
    icon: str = "🏠"
    color: str = "#1E9E4A"
    short: str = ""
    description: str = ""
    steps: list = []
    sort: int = 100


@router.post("/admin/scenarios")
def create_scenario(data: NavScenarioIn, db: Session = Depends(get_db)):
    exists = db.execute(
        select(NavScenario).where(NavScenario.key == data.key)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Сценарий с таким key уже существует")
    obj = NavScenario(**data.model_dump())
    db.add(obj)
    db.commit()
    return {"ok": True, "key": data.key}


@router.put("/admin/scenarios/{key}")
def update_scenario(key: str, data: NavScenarioIn, db: Session = Depends(get_db)):
    obj = db.execute(
        select(NavScenario).where(NavScenario.key == key)
    ).scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Сценарий не найден")
    for k, v in data.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    return {"ok": True}
