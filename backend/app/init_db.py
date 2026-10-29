"""Инициализация БД: создание таблиц и загрузка сид-данных."""
from datetime import datetime, timedelta

from sqlalchemy import select

from .database import SessionLocal, engine, Base
from .models import (
    User, Mortgage, SimScenario, NavScenario, LifeService,
)
from .routers.auth import hash_password, verify_password
from .seed import SIM_SCENARIOS, NAV_SCENARIOS, LIFE_SERVICES, DEMO_USERS


def init_db() -> None:
    """Создаёт таблицы и заполняет справочники (идемпотентно)."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Сценарии симулятора
        for s in SIM_SCENARIOS:
            obj = db.execute(
                select(SimScenario).where(SimScenario.key == s["key"])
            ).scalar_one_or_none()
            if obj is None:
                obj = SimScenario(key=s["key"], is_builtin=True)
                db.add(obj)
            obj.title = s["title"]
            obj.description = s["description"]
            obj.category = s["category"]
            obj.icon = s["icon"]
            obj.params_schema = s["params_schema"]
            obj.formulas = s["formulas"]
            obj.hints = s["hints"]
            obj.sort = s["sort"]
            obj.is_builtin = True

        # Сценарии навигатора
        for s in NAV_SCENARIOS:
            obj = db.execute(
                select(NavScenario).where(NavScenario.key == s["key"])
            ).scalar_one_or_none()
            if obj is None:
                obj = NavScenario(key=s["key"])
                db.add(obj)
            obj.title = s["title"]
            obj.icon = s["icon"]
            obj.short = s["short"]
            obj.description = s["description"]
            obj.color = s["color"]
            obj.steps = s["steps"]
            obj.sort = s["sort"]

        # Сервисы «Жизнь после ипотеки»
        for s in LIFE_SERVICES:
            obj = db.execute(
                select(LifeService).where(LifeService.key == s["key"])
            ).scalar_one_or_none()
            if obj is None:
                obj = LifeService(key=s["key"])
                db.add(obj)
            obj.title = s["title"]
            obj.category = s["category"]
            obj.icon = s["icon"]
            obj.description = s["description"]
            obj.how_to = s["how_to"]
            obj.docs = s["docs"]
            obj.hints = s["hints"]
            obj.calculator = s.get("calculator", "")
            obj.requires_auth = s.get("requires_auth", False)
            obj.sort = s["sort"]

        # Демо-пользователи
        for u in DEMO_USERS:
            obj = db.execute(
                select(User).where(User.username == u["username"])
            ).scalar_one_or_none()
            if obj is None:
                obj = User(
                    username=u["username"],
                    password_hash=hash_password(u["password"]),
                    full_name=u["full_name"],
                    is_admin=u["is_admin"],
                )
                db.add(obj)
                db.flush()
                if u.get("mortgage"):
                    m = u["mortgage"]
                    db.add(Mortgage(user_id=obj.id, **m))

        db.commit()
        print(f"init_db: OK ({len(SIM_SCENARIOS)} симуляторов, "
              f"{len(NAV_SCENARIOS)} навигаторов, "
              f"{len(LIFE_SERVICES)} сервисов)")
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
