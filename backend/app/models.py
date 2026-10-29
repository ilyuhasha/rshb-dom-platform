"""Модели базы данных (SQLAlchemy 2.x)."""
from datetime import datetime

from sqlalchemy import (
    Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(128))
    full_name: Mapped[str] = mapped_column(String(128), default="")
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Mortgage(Base):
    """Кредитный портфель пользователя — «банковский контур» (демо-данные)."""
    __tablename__ = "mortgages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128), default="Ипотека РСХБ")
    object_address: Mapped[str] = mapped_column(String(255), default="")
    object_type: Mapped[str] = mapped_column(String(32), default="Квартира")
    principal: Mapped[float] = mapped_column(Float)          # первоначальная сумма
    rate: Mapped[float] = mapped_column(Float)               # % годовых
    term_months: Mapped[int] = mapped_column(Integer)
    monthly_payment: Mapped[float] = mapped_column(Float)
    paid_months: Mapped[int] = mapped_column(Integer, default=0)
    remaining_debt: Mapped[float] = mapped_column(Float)
    start_date: Mapped[str] = mapped_column(String(10), default="2024-06-01")
    insurance_end: Mapped[str] = mapped_column(String(10), default="2027-06-01")
    next_payment_date: Mapped[str] = mapped_column(String(10), default="")


class SimScenario(Base):
    """Сценарий симулятора «Что, если...?» (задача 1)."""
    __tablename__ = "sim_scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text, default="")
    category: Mapped[str] = mapped_column(String(64), default="Ипотека")
    icon: Mapped[str] = mapped_column(String(16), default="📊")
    # Схема параметров: [{key,label,unit,type,default,min,max,step,options?}]
    params_schema: Mapped[list] = mapped_column(JSON, default=list)
    # Формулы: [{key,label,expr,unit,format}] — вычисляются по порядку,
    # могут ссылаться на параметры и результаты предыдущих формул.
    formulas: Mapped[list] = mapped_column(JSON, default=list)
    # Подсказки: [{title,text}] или [{title,text,condition}]
    hints: Mapped[list] = mapped_column(JSON, default=list)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort: Mapped[int] = mapped_column(Integer, default=100)


class SimCalculation(Base):
    """История расчётов симулятора."""
    __tablename__ = "sim_calculations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, index=True)
    scenario_key: Mapped[str] = mapped_column(String(64), index=True)
    inputs: Mapped[dict] = mapped_column(JSON)
    results: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NavScenario(Base):
    """Сценарий навигатора «Путь к своему дому» (задача 2)."""
    __tablename__ = "nav_scenarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    icon: Mapped[str] = mapped_column(String(16), default="🏠")
    short: Mapped[str] = mapped_column(String(255), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    color: Mapped[str] = mapped_column(String(16), default="#1E9E4A")
    # Этапы: [{stage, key, title, summary, checklist:[str], tips:[str]}]
    steps: Mapped[list] = mapped_column(JSON, default=list)
    sort: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class NavProgress(Base):
    """Прогресс пользователя по чек-листам навигатора."""
    __tablename__ = "nav_progress"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    scenario_key: Mapped[str] = mapped_column(String(64), index=True)
    step_key: Mapped[str] = mapped_column(String(64))
    item_index: Mapped[int] = mapped_column(Integer)
    done: Mapped[bool] = mapped_column(Boolean, default=False)

    __mapper_args__ = {
        "primary_key": [user_id, scenario_key, step_key, item_index]
    }


class LifeService(Base):
    """Сервис «Жизнь после ипотеки» (задача 3)."""
    __tablename__ = "life_services"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    key: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(128))
    category: Mapped[str] = mapped_column(String(64), default="Управление кредитом")
    icon: Mapped[str] = mapped_column(String(16), default="🏦")
    description: Mapped[str] = mapped_column(Text, default="")
    how_to: Mapped[list] = mapped_column(JSON, default=list)   # шаги действия
    docs: Mapped[list] = mapped_column(JSON, default=list)     # нужные документы
    hints: Mapped[list] = mapped_column(JSON, default=list)
    calculator: Mapped[str] = mapped_column(String(64), default="")  # ключ калькулятора
    requires_auth: Mapped[bool] = mapped_column(Boolean, default=False)
    sort: Mapped[int] = mapped_column(Integer, default=100)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class LifeAction(Base):
    """Действия авторизованного пользователя по сервисам (заявки/планы)."""
    __tablename__ = "life_actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    service_key: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="planned")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
