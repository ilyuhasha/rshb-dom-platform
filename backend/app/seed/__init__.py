"""Агрегатор всех сид-данных: сценарии симулятора, навигатора и сервисов."""
from importlib import import_module

from .sim_mortgage_base import SCENARIO as SIM_MORTGAGE
from .sim_prepay import SCENARIO as SIM_PREPAY
from .sim_repair import SCENARIO as SIM_REPAIR
from .sim_rent import SCENARIO as SIM_RENT
from .sim_build import SCENARIO as SIM_BUILD
from .sim_rural import SCENARIO as SIM_RURAL

from .nav_apartment import SCENARIO as NAV_APARTMENT
from .nav_house import SCENARIO as NAV_HOUSE
from .nav_land import SCENARIO as NAV_LAND
from .nav_build import SCENARIO as NAV_BUILD
from .nav_repair import SCENARIO as NAV_REPAIR
from .nav_rural import SCENARIO as NAV_RURAL
from .nav_newbuild import SCENARIO as NAV_NEWBUILD

from .life_part1 import SERVICES as LIFE_1
from .life_part2 import SERVICES as LIFE_2


SIM_SCENARIOS = [
    SIM_MORTGAGE, SIM_PREPAY, SIM_REPAIR, SIM_RENT, SIM_BUILD, SIM_RURAL,
]

NAV_SCENARIOS = [
    NAV_APARTMENT, NAV_HOUSE, NAV_LAND, NAV_BUILD, NAV_REPAIR, NAV_RURAL,
    NAV_NEWBUILD,
]

LIFE_SERVICES = LIFE_1 + LIFE_2

# Демо-аккаунты трёх ролей:
#   guest  — без входа (пароль не нужен), демо-данные
#   demo/demo     — Пользователь: свой банковский контур, история расчётов
#   admin/admin   — Администратор: управление сценариями, формулами,
#                   параметрами и подсказками
DEMO_USERS = [
    {"username": "demo", "password": "demo", "full_name": "Иванов Иван",
     "is_admin": False,
     "mortgage": {
         "name": "Ипотека «Своё Жильё», квартира",
         "object_address": "г. Рязань, ул. Садовая, д. 10, кв. 42",
         "object_type": "Квартира",
         "principal": 5200000, "rate": 14.0, "term_months": 300,
         "monthly_payment": 61847, "paid_months": 18,
         "remaining_debt": 5030000,
     }},
    {"username": "user02", "password": "user02", "full_name": "Петрова Анна",
     "is_admin": False,
     "mortgage": {
         "name": "Ипотека «Своё Жильё», дом",
         "object_address": "Рязанская обл., с. Кузьмино, ул. Полевая, 7",
         "object_type": "Частный дом",
         "principal": 4300000, "rate": 6.0, "term_months": 240,
         "monthly_payment": 30812, "paid_months": 10,
         "remaining_debt": 4190000,
     }},
    {"username": "admin", "password": "admin", "full_name": "Администратор системы",
     "is_admin": True, "mortgage": None},
]
