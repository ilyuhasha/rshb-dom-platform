"""Сценарий 3: Кредит на ремонт."""

SCENARIO = {
    "key": "repair_loan",
    "title": "Кредит на ремонт",
    "description": "Отделка с кредитом на ремонт: платёж, переплата и совокупная нагрузка вместе с ипотекой.",
    "category": "Ремонт",
    "icon": "🛠",
    "sort": 30,
    "params_schema": [
        {"key": "repair_cost", "label": "Стоимость ремонта", "unit": "₽", "type": "number", "default": 1500000, "min": 50000, "max": 30000000, "step": 50000},
        {"key": "repair_rate", "label": "Ставка по кредиту на ремонт", "unit": "% в год", "type": "number", "default": 21, "min": 0.1, "max": 40, "step": 0.1},
        {"key": "repair_years", "label": "Срок кредита на ремонт", "unit": "лет", "type": "number", "default": 5, "min": 1, "max": 15, "step": 1},
        {"key": "mortgage_payment", "label": "Платёж по ипотеке", "unit": "₽/мес.", "type": "number", "default": 61000, "min": 0, "max": 2000000, "step": 1000},
        {"key": "income", "label": "Доход семьи", "unit": "₽/мес.", "type": "number", "default": 180000, "min": 0, "max": 10000000, "step": 10000},
    ],
    "formulas": [
        {"key": "repair_payment", "label": "Платёж за ремонт", "expr": "annuity(repair_cost, repair_rate, repair_years * 12)", "unit": "₽/мес."},
        {"key": "repair_total", "label": "Всего за ремонт банку", "expr": "repair_payment * repair_years * 12", "unit": "₽"},
        {"key": "repair_overpay", "label": "Переплата за ремонт", "expr": "repair_total - repair_cost", "unit": "₽"},
        {"key": "total_payment", "label": "Итого платежей в месяц", "expr": "repair_payment + mortgage_payment", "unit": "₽/мес."},
        {"key": "dti", "label": "Долговая нагрузка", "expr": "if(income > 0, total_payment / income * 100, 0)", "unit": "%"},
        {"key": "budget_left", "label": "Остаток на жизнь", "expr": "income - total_payment", "unit": "₽/мес."},
    ],
    "hints": [
        {"title": "Считайте совокупную нагрузку", "text": "Банк одобряет кредит на ремонт по общему платежу всех кредитов — держите нагрузку ниже 50%.", "condition": "dti > 50"},
        {"title": "Ремонт в сельской местности", "text": "Через РСХБ доступны льготные программы на ремонт и благоустройство жилья в сельской местности — уточните в отделении.", "condition": ""},
    ],
}
