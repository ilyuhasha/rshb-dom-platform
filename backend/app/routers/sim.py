"""API: симулятор «Что, если...?» (Задача 1)."""
import math

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..finance import safe_eval, annuity_payment, months_to_repay
from ..models import SimScenario, SimCalculation, User
from .auth import get_current_user, require_user, require_admin

router = APIRouter(prefix="/api/sim", tags=["simulator"])

# Функции, доступные в формулах администратора
FORMULA_FUNCS = {
    "annuity": annuity_payment,
    "months_to_repay": months_to_repay,
}


class CalcRequest(BaseModel):
    scenario_key: str
    inputs: dict = {}


class ScenarioIn(BaseModel):
    key: str = ""
    title: str = ""
    description: str = ""
    category: str = "Прочее"
    icon: str = "📊"
    params_schema: list = []
    formulas: list = []
    hints: list = []
    sort: int = 100


def run_scenario(scenario: SimScenario, inputs: dict) -> dict:
    """Вычисляет формулы сценария по порядку. Ошибки отдельных формул
    не ломают расчёт — возвращают error для этой строки."""
    variables = dict(inputs)
    results, errors = [], []
    for f in scenario.formulas:
        try:
            value = safe_eval(f["expr"], {**variables, **FORMULA_FUNCS})
            value = float(value)
            # JSON не сериализует inf/nan — заменяем на None с пометкой
            if math.isnan(value) or math.isinf(value):
                results.append({
                    "key": f["key"], "label": f.get("label", f["key"]),
                    "value": None, "unit": f.get("unit", ""),
                    "hidden": bool(f.get("hidden")),
                    "error": "Проверьте ввод: платёж не покрывает проценты",
                })
                continue
            variables[f["key"]] = value
            results.append({
                "key": f["key"], "label": f.get("label", f["key"]),
                "value": round(value, 2), "unit": f.get("unit", ""),
                "hidden": bool(f.get("hidden")),
            })
        except Exception as e:
            errors.append({"key": f["key"], "error": str(e)})
            results.append({
                "key": f["key"], "label": f.get("label", f["key"]),
                "value": None, "unit": f.get("unit", ""),
                "hidden": bool(f.get("hidden")), "error": str(e),
            })
    # Подсказки: показываем те, чьё условие истинно (или без условия)
    hints = []
    for h in scenario.hints:
        cond = (h.get("condition") or "").strip()
        try:
            show = True if not cond else bool(safe_eval(cond, variables))
        except Exception:
            show = True
        if show:
            hints.append({"title": h["title"], "text": h["text"]})
    return {"results": results, "hints": hints, "errors": errors}


@router.get("/scenarios")
def list_scenarios(db: Session = Depends(get_db)):
    rows = db.execute(
        select(SimScenario).where(SimScenario.is_active == True)  # noqa: E712
        .order_by(SimScenario.sort)
    ).scalars().all()
    return [{
        "key": r.key, "title": r.title, "description": r.description,
        "category": r.category, "icon": r.icon,
        "params_schema": r.params_schema, "hints_count": len(r.hints),
    } for r in rows]


@router.get("/scenarios/{key}")
def get_scenario(key: str, db: Session = Depends(get_db)):
    row = db.execute(
        select(SimScenario).where(SimScenario.key == key)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Сценарий не найден")
    return {
        "key": row.key, "title": row.title, "description": row.description,
        "category": row.category, "icon": row.icon, "params_schema": row.params_schema,
        "formulas": row.formulas, "hints": row.hints, "is_builtin": row.is_builtin,
    }


@router.post("/calc")
def calc(req: CalcRequest, db: Session = Depends(get_db),
         user: User | None = Depends(get_current_user)):
    row = db.execute(
        select(SimScenario).where(SimScenario.key == req.scenario_key)
    ).scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Сценарий не найден")
    # Значения по умолчанию для незаполненных полей
    inputs = {}
    for p in row.params_schema:
        inputs[p["key"]] = req.inputs.get(p["key"], p.get("default", 0))
    out = run_scenario(row, inputs)
    # Изоляция расчётов: гостю результаты отдаются, но история
    # не сохраняется; пользователь — история только своя
    if user is not None:
        db.add(SimCalculation(user_id=user.id, scenario_key=req.scenario_key,
                              inputs=inputs, results=out))
        db.commit()
    return out


@router.get("/history")
def history(limit: int = 20, db: Session = Depends(get_db),
            user: User = Depends(require_user)):
    """История расчётов — изолирована: только собственные записи."""
    rows = db.execute(
        select(SimCalculation)
        .where(SimCalculation.user_id == user.id)
        .order_by(SimCalculation.id.desc()).limit(limit)
    ).scalars().all()
    return [{"id": r.id, "scenario_key": r.scenario_key,
             "created_at": r.created_at.isoformat()} for r in rows]


# ---- Администрирование: только роль «Администратор» (см. /api/auth) ----

@router.post("/admin/scenarios")
def create_scenario(data: ScenarioIn,
                    admin: User = Depends(require_admin),
                    db: Session = Depends(get_db)):
    exists = db.execute(
        select(SimScenario).where(SimScenario.key == data.key)
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(409, "Сценарий с таким key уже существует")
    obj = SimScenario(
        key=data.key, title=data.title, description=data.description,
        category=data.category, icon=data.icon,
        params_schema=data.params_schema, formulas=data.formulas,
        hints=data.hints, sort=data.sort, is_builtin=False,
    )
    db.add(obj)
    db.commit()
    return {"ok": True, "key": data.key}


@router.put("/admin/scenarios/{key}")
def update_scenario(key: str, data: ScenarioIn,
                    admin: User = Depends(require_admin),
                    db: Session = Depends(get_db)):
    obj = db.execute(
        select(SimScenario).where(SimScenario.key == key)
    ).scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Сценарий не найден")
    # Частичное обновление: меняем только явно переданные поля
    provided = data.model_fields_set
    for field in ("title", "description", "category", "icon",
                  "params_schema", "formulas", "hints", "sort"):
        if field in provided:
            setattr(obj, field, getattr(data, field))
    db.commit()
    return {"ok": True}


@router.delete("/admin/scenarios/{key}")
def delete_scenario(key: str,
                    admin: User = Depends(require_admin),
                    db: Session = Depends(get_db)):
    obj = db.execute(
        select(SimScenario).where(SimScenario.key == key)
    ).scalar_one_or_none()
    if not obj:
        raise HTTPException(404, "Сценарий не найден")
    if obj.is_builtin:
        raise HTTPException(400, "Встроенный сценарий удалить нельзя — "
                                 "можно деактивировать")
    db.delete(obj)
    db.commit()
    return {"ok": True}
